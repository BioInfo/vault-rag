#!/usr/bin/env python3
"""
Ingestion script for building the RAG vector database from Markdown files.
"""

import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from server.config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """Process Markdown files with frontmatter parsing."""

    def __init__(self):
        self.frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content."""
        match = self.frontmatter_pattern.match(content)

        if match:
            frontmatter_str = match.group(1)
            content_without_frontmatter = content[match.end() :]

            try:
                frontmatter = yaml.safe_load(frontmatter_str) or {}
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse frontmatter: {e}")
                frontmatter = {}

            return frontmatter, content_without_frontmatter

        return {}, content

    def process_file(self, file_path: Path) -> Optional[Document]:
        """Process a single markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            frontmatter, main_content = self.parse_frontmatter(content)

            # Create metadata - ensure ChromaDB compatible types
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_stem": file_path.stem,
            }

            # Process frontmatter to ensure compatible types
            for key, value in frontmatter.items():
                if value is None:
                    continue  # Skip None values
                elif isinstance(value, (str, int, float)):
                    metadata[key] = str(value)
                elif isinstance(value, bool):
                    metadata[key] = str(value)
                elif isinstance(value, list):
                    # Convert lists to comma-separated strings
                    metadata[key] = ", ".join(str(item) for item in value)
                else:
                    # Convert other types to strings
                    metadata[key] = str(value)

            # Create document
            doc = Document(text=main_content, extra_info=metadata)

            return doc

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return None


def setup_embedding_model() -> HuggingFaceEmbedding:
    """Initialize the embedding model."""
    logger.info(f"Initializing embedding model: {config.EMBED_MODEL}")
    embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    Settings.embed_model = embed_model
    return embed_model


def setup_chroma_store() -> ChromaVectorStore:
    """Initialize ChromaDB vector store."""
    logger.info(f"Setting up ChromaDB at: {config.CHROMA_PATH}")

    # Ensure storage directory exists
    os.makedirs(config.CHROMA_PATH, exist_ok=True)

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path=config.CHROMA_PATH, settings=ChromaSettings(anonymized_telemetry=False)
    )

    # Get or create collection
    try:
        collection = chroma_client.get_collection(config.COLLECTION_NAME)
        logger.info(f"Using existing collection: {config.COLLECTION_NAME}")
    except Exception:
        collection = chroma_client.create_collection(config.COLLECTION_NAME)
        logger.info(f"Created new collection: {config.COLLECTION_NAME}")

    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return vector_store


def load_documents(vault_path: str) -> List[Document]:
    """Load and process all markdown documents from the vault."""
    vault_path_obj = Path(vault_path)

    if not vault_path_obj.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    logger.info(f"Loading documents from: {vault_path}")

    # Find all markdown files
    markdown_files: List[Path] = []
    for ext in config.MARKDOWN_EXTENSIONS:
        markdown_files.extend(vault_path_obj.rglob(f"*{ext}"))

    # Filter out excluded directories
    filtered_files = []
    for file_path in markdown_files:
        if not any(excluded in file_path.parts for excluded in config.EXCLUDE_DIRS):
            filtered_files.append(file_path)

    logger.info(f"Found {len(filtered_files)} markdown files")

    # Process files
    processor = MarkdownProcessor()
    documents = []

    for file_path in filtered_files:
        doc = processor.process_file(file_path)
        if doc:
            documents.append(doc)

        if len(documents) % 100 == 0:
            logger.info(f"Processed {len(documents)} documents...")

    logger.info(f"Successfully processed {len(documents)} documents")
    return documents


def create_index(
    documents: List[Document], vector_store: ChromaVectorStore
) -> VectorStoreIndex:
    """Create the vector index from documents."""
    logger.info("Creating vector index...")

    # Setup node parser for chunking
    node_parser = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
    )
    Settings.node_parser = node_parser

    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create index
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )

    logger.info("Vector index created successfully")
    return index


def persist_index(index: VectorStoreIndex):
    """Persist the index to disk."""
    logger.info(f"Persisting index to: {config.INDEX_PERSIST_DIR}")
    os.makedirs(config.INDEX_PERSIST_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=config.INDEX_PERSIST_DIR)
    logger.info("Index persisted successfully")


def main() -> int:
    """Main ingestion function."""
    parser = argparse.ArgumentParser(
        description="Ingest markdown files into vector database"
    )
    parser.add_argument(
        "--vault", default=config.VAULT_PATH, help="Path to vault directory"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=config.CHUNK_SIZE,
        help="Chunk size for splitting",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=config.CHUNK_OVERLAP,
        help="Chunk overlap",
    )
    parser.add_argument(
        "--collection",
        default=config.COLLECTION_NAME,
        help="ChromaDB collection name",
    )

    args = parser.parse_args()

    try:
        # Update config with CLI args
        config.VAULT_PATH = args.vault
        config.CHUNK_SIZE = args.chunk_size
        config.CHUNK_OVERLAP = args.chunk_overlap
        config.COLLECTION_NAME = args.collection

        logger.info("Starting ingestion process...")
        logger.info(f"Vault path: {config.VAULT_PATH}")
        logger.info(f"Storage directory: {config.STORAGE_DIR}")
        logger.info(f"Chunk size: {config.CHUNK_SIZE}")
        logger.info(f"Chunk overlap: {config.CHUNK_OVERLAP}")

        # Setup components
        setup_embedding_model()
        vector_store = setup_chroma_store()

        # Load documents
        documents = load_documents(config.VAULT_PATH)

        if not documents:
            logger.error("No documents found to ingest")
            return 1

        # Create and persist index
        index = create_index(documents, vector_store)
        persist_index(index)

        logger.info("Ingestion completed successfully!")
        logger.info(f"Ingested {len(documents)} documents")
        logger.info(f"Vector store: {config.CHROMA_PATH}")
        logger.info(f"Index storage: {config.INDEX_PERSIST_DIR}")

        return 0

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
