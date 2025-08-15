# MCP Sidecar for Vault RAG

Status: Proposal implemented as documentation-first plan with minimal, review-ready changes.

This document defines how we enable a Model Context Protocol (MCP) sidecar for the existing FastAPI service using the fastapi_mcp project. It covers purpose, architecture, interfaces, setup, usage, testing, deployment, maintenance, and associated quality gates.

Assumptions
- MCP = Model Context Protocol (as confirmed).
- Runtime: Python 3.10, package manager: uv (compatible with requirements.txt).
- CI: GitHub Actions (we will add or extend .github/workflows/ci.yml).
- Configs centralized in pyproject.toml (ruff/black/isort/mypy/pytest/coverage).

Non-goals
- Do not change core app logic in [server/main.py](server/main.py).
- Do not expose all endpoints; we will curate a minimal, safe tool surface.
- Do not implement production auth in this PR; we document the pattern and provide placeholders.

--------------------------------------------------------------------------------
1) Overview

Problem
- Agents need stable, typed, discoverable tools to call our HTTP APIs. Handwritten adapters are fragile and duplicated.

Goal
- Surface a typed set of FastAPI routes as MCP tools so agents can discover and invoke them through the MCP protocol with minimal glue.

Why Sidecar
- Decouples MCP lifecycle and resource constraints from the main API process.
- Enables independent upgrades, access control, and rate limiting per MCP consumer class.

Success Criteria
- Tools auto-generated from OpenAPI or curated registry.
- Local dev: single command to run FastAPI and MCP servers.
- CI: quality gates (lint/format/types/tests/coverage) must pass.
- Docs-first: clear setup, usage, and testing instructions.

--------------------------------------------------------------------------------
2) Architecture

Pattern: Sidecar
- Agent (client) <—MCP (stdio/SSE/HTTP)—> MCP Server (fastapi_mcp sidecar) <—HTTP/ASGI—> FastAPI App

Components
- FastAPI app: [server/main.py](server/main.py).
- MCP sidecar: fastapi_mcp server that either:
  - Loads OpenAPI from http://localhost:8000/openapi.json, or
  - Imports the ASGI app object and introspects routes.
- Auth injector: optional bearer token/header injection for secured routes.
- Filters: route allowlist/denylist to keep surface minimal.

Data Flow
- Client lists MCP tools.
- Client invokes a tool with typed params.
- Sidecar maps the tool to an HTTP call on the FastAPI app, transforms request/response, returns typed result or error.

Boundaries
- The sidecar must not perform business logic; it only transforms and forwards.
- No direct DB/filesystem access by the sidecar beyond calling FastAPI.

Failure Modes
- FastAPI down: MCP tools return 5xx mapping with clear diagnostics.
- Schema drift: Mismatched request/response schemas break tools; mitigated via contract tests in CI.
- Auth failure: Explicit 401/403 surfaced as MCP errors with remediation hints.

--------------------------------------------------------------------------------
3) Interfaces

Primary Protocol
- MCP (Model Context Protocol) exposed by the sidecar.

Transport
- Target stdio or SSE/HTTP depending on fastapi_mcp and client support. For local dev with Cline/VSCode, prefer stdio if supported; otherwise local SSE on 127.0.0.1 with restricted port.

Tool Mapping
- One tool per FastAPI operationId or curated alias. Prioritize:
  - Safe GET/POST endpoints required by agents.
  - Avoid admin/debug/internal routes.

Schemas
- Request/response Pydantic models with explicit field types, constraints, and descriptions. Strong typing improves auto-generated MCP tool schemas.

Examples
- Tool: search_vault
  - Input: { query: string, k?: int, filters?: object }
  - Output: { matches: array, explanations?: array }
- Tool: summarize_scope
  - Input: { scope: "file|folder|tag", target: string, style?: string, length?: string }
  - Output: { summary: string, citations?: array }

Errors
- HTTP 4xx/5xx mapped to MCP error with:
  - code: http.status_text
  - message: helpful explanation
  - details: original HTTP status, path, request_id (if available)

--------------------------------------------------------------------------------
4) Local Development

Prerequisites
- Python 3.10
- uv package manager
- Running FastAPI server (for sidecar HTTP discovery) at http://127.0.0.1:8000

Install
- Add fastapi_mcp to requirements.txt (document-first; pinned in a follow-up PR once validated).
- Install deps:
  - uv pip install -r requirements.txt

Run
- Start FastAPI:
  - uvicorn server.main:app --host 127.0.0.1 --port 8000
- Start MCP sidecar (examples; exact CLI per fastapi_mcp docs):
  - fastapi_mcp --openapi http://127.0.0.1:8000/openapi.json
  - or: fastapi_mcp --import server.main:app
  - Add auth header if needed: --header "Authorization: Bearer <token>"

Environment Variables
- FASTAPI_BASE_URL (default http://127.0.0.1:8000)
- MCP_ALLOWLIST (comma-separated operationIds)
- MCP_DENYLIST (comma-separated operationIds)
- MCP_AUTH_BEARER (optional)
- LOG_LEVEL (info|debug|warning)

Verification
- Use an MCP client (e.g., Cline) to list tools and run a dry-run command against a non-destructive endpoint.

--------------------------------------------------------------------------------
5) Testing Strategy

Test Types
- Unit tests (FastAPI models and small handlers).
- Integration tests (sidecar-to-FastAPI via local HTTP).
- Contract tests (validate tool schemas match OpenAPI/mypy-checked models).
- Negative tests (auth errors, validation failures, timeouts).

Coverage
- Target ≥ 90% line coverage for sidecar utilities and adapters.
- Exclude simple __main__ or CLI bootstrap from strict coverage if needed.

Fixtures
- Reusable FastAPI test client fixture.
- Local MCP client harness (if provided) or HTTP proxy harness to simulate tool calls.

--------------------------------------------------------------------------------
6) Quality Gates

Policies (enforced in CI)
- Ruff lint: pyflakes, pycodestyle, flake8-bugbear, isort rules.
- Black format check: line length 88.
- Mypy: strict-ish (no implicit optional, disallow untyped defs, allow-redefinition off).
- Pytest with pytest-cov: coverage ≥ 90%.
- Pre-commit hooks: run all gates locally before commit.

--------------------------------------------------------------------------------
7) Security

Principles
- Least-privilege: expose only required endpoints as tools.
- Explicit auth: sidecar passes Authorization only if configured.
- Network scope: bind MCP sidecar to 127.0.0.1 for local dev.
- Secrets: pass via env vars; never commit secrets (.env in .gitignore).

Attack Surface
- Input validation: rely on FastAPI/Pydantic with strict models.
- Rate limiting/timeouts: configure HTTP client defaults for the sidecar.
- Logging: avoid sensitive payloads; include request_id for traceability.

--------------------------------------------------------------------------------
8) Observability

Logging
- Structured logs with request_id correlation between sidecar and FastAPI.

Metrics
- Requests per tool, error rates, latency (p50/p95/p99).
- Timeouts and retries.

Health/Readiness
- /health and /ready endpoints on FastAPI.
- Sidecar startup checks OpenAPI availability.

--------------------------------------------------------------------------------
9) Deployment

Environments
- Local dev: processes on 127.0.0.1
- Container: optional Dockerfiles for FastAPI and MCP sidecar.

Compose/K8s (hints)
- docker-compose: two services (api, mcp) with shared network.
- Kubernetes: two Deployments, MCP depends on API Service readiness.

Rollout/Rollback
- Sidecar is independently deployable; blue/green or canary per usual workflow.

--------------------------------------------------------------------------------
10) Maintenance

Versioning
- Pin fastapi_mcp and FastAPI compatible versions.
- Track breaking changes in MCP spec and FastAPI.

Upgrade Path
- Update fastapi_mcp, regenerate tool schemas in staging, run contract tests, then promote.

Deprecation
- Mark tools deprecated in docs and route metadata before removal.
- Maintain denylist for removed tools to block accidental use.

--------------------------------------------------------------------------------
11) Roadmap Placement

- MCP enablement occurs before existing roadmap items. We will add a minimal “Pre-Roadmap: MCP Enablement” section at the top of [docs/ROADMAP.md](docs/ROADMAP.md) listing:
  - Add fastapi_mcp dependency
  - Create MCP sidecar entrypoint/config
  - Curate allowlist of endpoints
  - Add contract tests
  - Add CI quality gates (ruff/black/isort/mypy/pytest/coverage)
  - Initial docs and examples

--------------------------------------------------------------------------------
12) Examples

Example: Running locally
- Terminal 1:
  - uvicorn server.main:app --host 127.0.0.1 --port 8000
- Terminal 2:
  - python -m server.mcp.sidecar

Example: Tool invocation (conceptual)
- Input:
  - { "tool": "search_vault", "params": {"query": "CRISPR", "k": 5 } }
- Output:
  - { "matches": [...], "explanations": [...] }

--------------------------------------------------------------------------------
Appendix: References

- fastapi_mcp: https://github.com/tadata-org/fastapi_mcp
- MCP spec and clients (Cline/VSCode, Cursor, etc.)
- FastAPI and Pydantic best practices
