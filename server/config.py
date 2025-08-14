"""Configuration for the RAG server."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment files in order of priority
# local.env takes precedence over .env
load_dotenv(".env")  # Load base config first
load_dotenv("local.env")  # Override with local config if it exists


class Config:
    """Configuration settings for the RAG backend."""
    
    # Source vault path - should be set in .env or local.env
    VAULT_PATH: str = os.getenv("VAULT_PATH", "./example-vault")
    
    # Storage paths
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    CHROMA_PATH: str = os.path.join(STORAGE_DIR, "chroma")
    INDEX_PERSIST_DIR: str = os.path.join(STORAGE_DIR, "index")
    
    # Vector store settings
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "vault_md")
    
    # Embedding model
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Retrieval settings
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "20"))
    
    # Chunking settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # File patterns
    MARKDOWN_EXTENSIONS: list[str] = [".md", ".mdx"]
    EXCLUDE_DIRS: list[str] = [".git", ".obsidian", ".trash", "node_modules", ".DS_Store", "__pycache__"]


config = Config()