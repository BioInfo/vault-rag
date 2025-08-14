# Vault RAG Roadmap: From Starter to Supercharged

Purpose: Define a clear, staged plan to evolve Vault RAG into a best-in-class, privacy-first personal knowledge intelligence platform with richer context, smarter chunking, and deeper insights.

Version: 0.1
Status: Draft
Owner: Core Maintainers

--------------------------------------------------------------------

1) Vision & Outcomes
- Vision: Turn any Markdown vault into an intelligent, self-organizing knowledge system that surfaces the right context at the right time, provides trustworthy synthesis, and unlocks actionable insights.
- Core Outcomes
  - Precision: Retrieve the most relevant passages with explainability.
  - Comprehension: Preserve document structure, intent, and relationships.
  - Insight: Generate summaries, timelines, topic clusters, and entity networks.
  - Trust: Keep all data local with robust security and auditability.
  - DX: Make setup, use, and extension delightful.

--------------------------------------------------------------------

2) Architecture Evolution

2.1 Context Graph Layer
- Add a lightweight knowledge graph (KG) that captures:
  - File-level: path, tags, links, backlinks, headings, modified time
  - Section-level: heading hierarchy, anchor IDs
  - Entities: people, orgs, compounds, diseases, methods (configurable domain ontology)
  - Relations: mentions, references, derived-from, authored-by
- Storage options:
  - Start: Persist as JSON/SQLite alongside vector store (no extra infra)
  - Later: Optional Neo4j/DuckDB for advanced analytics

2.2 Hybrid Retrieval
- Use a hybrid retrieval pipeline:
  - Sparse: BM25/Okapi (e.g., Lucene via Whoosh or simple-scoring with Elastic optional)
  - Dense: Existing Chroma embeddings
  - RRF (Reciprocal Rank Fusion) to merge
  - Cross-Encoder re-ranking (e.g., ms-marco MiniLM) for final top-k

2.3 Query Understanding
- Query parsing and intent classification:
  - Detect filters: date ranges, tags, authors, headings
  - Detect task type: lookup, compare, summarize, explain, list, timeline
  - Expand queries via synonyms/tag/alias tables (configurable)

2.4 Explainability
- Return why a result ranked high:
  - Show scoring breakdown (dense, sparse, reranker)
  - Show matched headings and tags
  - Show citations with character offsets

--------------------------------------------------------------------

3) Smarter Chunking (Structure-Aware)

3.1 Heading- and Section-Aware Chunking
- Split on Markdown headings first (H1-H6), then apply semantic chunking within sections
- Preserve anchors and section context (parents/children)
- Keep sibling context windows for Q&A to avoid brittle isolation

3.2 Semantic & Recursive Chunking
- Use a text splitter that:
  - Uses sentence boundaries and semantic similarity
  - Recursively merges small chunks to meet min_token thresholds
  - Respects code blocks, lists, tables, callouts

3.3 Table, Code, and Image Handling
- Tables: flatten to TSV/CSV-like and store both as raw and normalized
- Code blocks: language-aware chunking; embed docstrings/comments more heavily
- Images (optional): store alt text and captions; future: OCR hooks

3.4 Metadata-Rich Chunks
- Each node stores:
  - file_name, file_path, section_title, section_hierarchy
  - headings_above, backlinks_count, tags, created/modified time
  - frontmatter normalized (types coerced)
  - token_count, checksum

--------------------------------------------------------------------

4) Insight Generation

4.1 Summarization & Synthesis
- Map-reduce summarization across:
  - Single file
  - Folder/project
  - Tag-based collections
- Styles:
  - Executive summary, key takeaways, open questions
  - Chain-of-density technique to maximize signal
- Citations inline with paragraph-level anchors

4.2 Entity & Topic Extraction
- Named Entity Recognition (local models where possible)
- Topic modeling (BERTopic or LLM-aided clustering)
- Tag suggestions and taxonomy expansion (user-approved)

4.3 Timeline & Evolution
- Build timelines of:
  - Concepts over time (first mention → latest)
  - Decisions from decision logs
  - Project milestones from dated notes/frontmatter
- Produce “What changed since last month?” digests

4.4 Similarity & Discovery
- “Related Notes” recommendations for any note
- “You might be looking for…” navigation cards
- Duplicate/overlap detection and merge suggestions

--------------------------------------------------------------------

5) Security, Privacy, Governance

5.1 Data Boundaries
- Local-only by default
- Optional network calls behind explicit feature flags
- Redaction filters (PII/PHI) for any export/integration

5.2 Auditability & Logging
- Structured logs for queries and retrieved sources
- Privacy mode that disables persistent logs
- Hash-based doc IDs in logs (no raw paths)

5.3 Access Guards
- Directory allowlists
- File pattern filters
- “Do not ingest” glob rules surfaced in docs

--------------------------------------------------------------------

6) Observability & Evaluation

6.1 Quality Benchmarks
- Build a small suite of evaluation prompts + expected sources:
  - Precision@k on hand-labeled queries
  - Reranker ablation studies
  - Latency and throughput metrics

6.2 Telemetry (Local)
- Time per phase: embedding, retrieval, rerank, generation
- Cache hit rates (embeddings, generations)
- Index size growth and ingest time

6.3 UX Feedback Loop
- Thumbs up/down per answer with free-text
- Feedback stored locally to improve reranking and chunking heuristics

--------------------------------------------------------------------

7) Developer Experience (DX)

7.1 Unified CLI
- vault-rag ingest
- vault-rag reindex
- vault-rag search "query" --k 8 --filters tag:biology
- vault-rag eval --suite default
- vault-rag web (starts local UI)

7.2 SDK
- Python client with:
  - search(), retrieve(), summarize(), related_notes()
  - simple dataclasses for results and metadata

7.3 Local UI (Phase 2)
- Minimal web app:
  - Search bar, filters (tags/dates/folders)
  - Reader pane with citations, highlights
  - “Related Notes” sidebar
  - One-click “Summarize folder” and “Build timeline” actions

--------------------------------------------------------------------

8) Performance & Caching

8.1 Caches
- Embedding cache (SQLite or file-based)
- Generation cache keyed by prompt+context hash
- Query results cache for recent queries

8.2 Parallelism
- Multi-process ingestion
- Batch embeddings
- Async retrieval calls to vector + sparse backends

8.3 Index Management
- Checkpointing for long ingests
- Partial reindex for changed files only
- Background index compaction

--------------------------------------------------------------------

9) Extensibility & Integrations

9.1 Plugins (Later Phase)
- Ingestion hooks:
  - Convert PDF/DOCX to Markdown (optional OCR)
  - External knowledge imports (GitHub wiki, Notion export)
- Post-retrieval hooks:
  - Custom rerankers
  - Domain adapters (biomed, legal, finance)
- Output exporters:
  - Static site (mkdocs)
  - JSON API schema for external tools

9.2 Multi-Model Support
- Pluggable embedding models (local and remote)
- Pluggable rerankers and summarizers (with feature flags)
- Safe defaults for fully-local pipelines

--------------------------------------------------------------------

10) Milestones (Phased Plan)

Phase 1: Context + Chunking Foundations (Weeks 1–3)
- [ ] Section-aware splitter: headings-first, semantic second
- [ ] Metadata-rich nodes: full hierarchy, tags, frontmatter normalized
- [ ] Entity extraction (lightweight) and topic tags (optional flag)
- [ ] Hybrid retrieval: BM25 + Chroma + RRF
- [ ] Cross-encoder reranking (configurable)
- [ ] Explainability in /retrieve response
- [ ] CLI: ingest, reindex, search
- [ ] Eval suite v0.1 (precision@k with 10–20 handcrafted queries)

Phase 2: Insight Layer (Weeks 4–6)
- [ ] Map-reduce summarization (file/folder/tag scopes)
- [ ] Chain-of-density summaries with citations
- [ ] Timelines (basic): by file date and heading dates
- [ ] Related Notes endpoint
- [ ] Generation and embedding caches
- [ ] Python SDK v0.1

Phase 3: UX & Observability (Weeks 7–9)
- [ ] Minimal local UI for search + reader + related notes
- [ ] Feedback capture (thumbs + notes) stored locally
- [ ] Observability dashboard (latency, cache hit, index stats)
- [ ] Eval suite v0.2 with ablation toggles and latency histograms

Phase 4: Hardening & Extensions (Weeks 10–12)
- [ ] Partial reindex and checkpointing
- [ ] Plugin interface (ingest hooks, post-retrieval hooks)
- [ ] Optional PDF/DOCX to MD ingest
- [ ] Advanced timeline (entity-aware)
- [ ] Docs and tutorials

--------------------------------------------------------------------

11) API Additions (Proposed)

New Endpoints
- POST /search
  - body: { query, k, filters: {tags[], folder, date_range}, with_explanations: bool }
  - returns: { matches[], explanations[], fused_scores[], sources[] }

- POST /summarize
  - body: { scope: file|folder|tag, target: path|tag, style: exec|bullets|qna, length: short|medium|long }
  - returns: { summary, citations[] }

- POST /related
  - body: { file_path, k }
  - returns: { files[] with reasons }

- GET /timeline
  - query: { tag|folder|entity, start, end }
  - returns: { events[] with citations }

- GET /entities
  - query: { tag|folder|file_path }
  - returns: { entities[], relations[] }

--------------------------------------------------------------------

12) Data Model (Nodes)

Node (per chunk)
- id, file_path, file_name, file_stem
- section_title, section_hierarchy (array)
- headings_above (array)
- tags (array), backlinks (int), mentions (array)
- frontmatter_normalized (object)
- created_ts, modified_ts
- text, token_count, checksum
- embedding_vector_id
- sparse_tokens (optional, for BM25-lite)
- parents/siblings references (ids)

--------------------------------------------------------------------

13) Security Model

- Defaults:
  - No external calls; all processing local
  - Redaction filters optional and disabled by default
- Exports:
  - Explicit allowlists required
  - “No-vault-content in logs” mode
- Testing:
  - Add security tests for:
    - Leakage in logs
    - Respect of exclude patterns
    - Exports obeying allowlists only

--------------------------------------------------------------------

14) Engineering Tasks (Backlog Candidates)

Chunking & Context
- [ ] Implement heading-first splitter with recursive semantic merge
- [ ] Normalize frontmatter types; store tags consistently
- [ ] Compute backlinks from wiki-links/markdown links
- [ ] Add entity extractor with configurable models

Retrieval
- [ ] Integrate BM25 (Whoosh/Elasticsearch optional)
- [ ] RRF fusion implementation
- [ ] Cross-encoder reranking (MiniLM or equivalent)
- [ ] Explanations payload

Insights
- [ ] Map-reduce summarization operator
- [ ] Chain-of-density prompt templates
- [ ] Timelines (basic, then entity-aware)
- [ ] Related Notes API

Infra & DX
- [ ] Embedding + generation caches
- [ ] Partial reindex (mtime-based)
- [ ] CLI & SDK
- [ ] Eval harness and metrics dashboard
- [ ] Minimal local UI

Security & Privacy
- [ ] Redaction filters
- [ ] Privacy mode logs
- [ ] Security tests

Docs
- [ ] Developer Guide: architecture, extension points
- [ ] User Guide: query filters, scopes, and examples
- [ ] Evaluations: how to run and interpret

--------------------------------------------------------------------

15) Success Criteria & KPIs

Quality
- Precision@5 ≥ 0.7 on curated eval set
- Reranker improves NDCG@10 by ≥ 10% vs. dense-only baseline

Performance
- P50 retrieval + rerank ≤ 300ms on local laptop
- Ingest throughput ≥ 50 docs/sec (100–300 tokens/doc) with batch embeds

Usage
- 5+ community plugins in first 3 months
- 200+ GitHub stars; 10+ contributors

Trust
- Zero leakage in security tests
- Clear explainability for top answers

--------------------------------------------------------------------

16) Risks & Mitigations

- Risk: Over-indexing on dense vectors hurts explainability
  - Mitigation: Hybrid retrieval + explanations API + sparse-only fallback

- Risk: Complex chunking increases ingest time
  - Mitigation: Parallel ingest + caching + partial reindex

- Risk: Privacy concerns with models
  - Mitigation: Local-only defaults; feature flags; redaction filters

--------------------------------------------------------------------

17) Next Steps (Immediate)

- [ ] Implement heading-first + semantic recursive splitter
- [ ] Add RRF fusion and basic reranker
- [ ] Extend RetrievalResponse with explanations and section metadata
- [ ] Ship a minimal eval harness and initial metrics
- [ ] Draft API contracts for /search, /summarize, /related

--------------------------------------------------------------------

References & Inspiration
- RRF: Reciprocal Rank Fusion for robust search result merging
- Chain-of-Density summarization
- BERTopic for topic modeling (optional, localizable)
- Sparse + dense hybrid retrieval literature

This roadmap is a living document. Propose changes via PRs. Prioritize local-first, privacy-safe, and explainable features.