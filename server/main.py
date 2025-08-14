"""
FastAPI server for the RAG backend.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import chromadb
from chromadb.config import Settings as ChromaSettings

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vault RAG API",
    description="Retrieval-Augmented Generation API for Markdown vault",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the index and retriever
index = None
retriever = None


class RetrievalRequest(BaseModel):
    """Request model for retrieval endpoint."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=config.DEFAULT_TOP_K, ge=1, le=config.MAX_TOP_K, description="Number of results to return")


class RetrievalMatch(BaseModel):
    """Model for a single retrieval match."""
    text: str = Field(..., description="Retrieved text content")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class RetrievalResponse(BaseModel):
    """Response model for retrieval endpoint."""
    matches: List[RetrievalMatch] = Field(..., description="List of retrieved matches")
    query: str = Field(..., description="Original query")
    total_matches: int = Field(..., description="Total number of matches")
    sources: List[str] = Field(..., description="List of unique markdown files used as sources")


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status: str = Field(..., description="Health status")
    collections: List[str] = Field(default_factory=list, description="Available collections")
    index_exists: bool = Field(..., description="Whether index storage exists")
    chroma_exists: bool = Field(..., description="Whether ChromaDB exists")
    embedding_model: str = Field(..., description="Embedding model being used")


def setup_embedding_model() -> HuggingFaceEmbedding:
    """Initialize the embedding model."""
    logger.info(f"Initializing embedding model: {config.EMBED_MODEL}")
    embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    Settings.embed_model = embed_model
    return embed_model


def setup_chroma_store() -> ChromaVectorStore:
    """Initialize ChromaDB vector store."""
    logger.info(f"Loading ChromaDB from: {config.CHROMA_PATH}")
    
    if not os.path.exists(config.CHROMA_PATH):
        raise RuntimeError(f"ChromaDB not found at {config.CHROMA_PATH}. Please run ingestion first.")
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path=config.CHROMA_PATH,
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Get collection
    try:
        collection = chroma_client.get_collection(config.COLLECTION_NAME)
        logger.info(f"Loaded collection: {config.COLLECTION_NAME}")
    except Exception as e:
        raise RuntimeError(f"Failed to load collection {config.COLLECTION_NAME}: {e}")
    
    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return vector_store


def load_index() -> None:
    """Load the persisted index."""
    global index, retriever
    
    logger.info("Loading vector index...")
    
    if not os.path.exists(config.INDEX_PERSIST_DIR):
        raise RuntimeError(f"Index storage not found at {config.INDEX_PERSIST_DIR}. Please run ingestion first.")
    
    # Setup embedding model
    setup_embedding_model()
    
    # Setup vector store
    vector_store = setup_chroma_store()
    
    # Load index from storage
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=config.INDEX_PERSIST_DIR
    )
    
    index = load_index_from_storage(storage_context)
    retriever = index.as_retriever(similarity_top_k=config.DEFAULT_TOP_K)
    
    logger.info("Index loaded successfully")


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    try:
        load_index()
        logger.info("RAG server startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to start RAG server: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if ChromaDB exists and get collections
        collections = []
        chroma_exists = os.path.exists(config.CHROMA_PATH)
        
        if chroma_exists:
            try:
                chroma_client = chromadb.PersistentClient(
                    path=config.CHROMA_PATH,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                collections = [col.name for col in chroma_client.list_collections()]
            except Exception as e:
                logger.warning(f"Failed to list collections: {e}")
        
        # Check if index exists
        index_exists = os.path.exists(config.INDEX_PERSIST_DIR)
        
        return HealthResponse(
            status="ok" if (index and retriever) else "not_ready",
            collections=collections,
            index_exists=index_exists,
            chroma_exists=chroma_exists,
            embedding_model=config.EMBED_MODEL
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {e}"
        )


@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_documents(request: RetrievalRequest):
    """Retrieve relevant documents for a query."""
    if not index or not retriever:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Index not loaded. Please check server startup logs."
        )
    
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Perform retrieval with requested top_k
        nodes = retriever.retrieve(request.query)
        # Limit to requested top_k if we got more results
        if len(nodes) > request.top_k:
            nodes = nodes[:request.top_k]
        
        # Convert to response format
        matches = []
        unique_sources = set()
        
        for node in nodes:
            # Handle score safely - it might be None
            score = 0.0
            if hasattr(node, 'score') and node.score is not None:
                score = float(node.score)
            
            match = RetrievalMatch(
                text=node.text,
                score=score,
                metadata=node.metadata or {}
            )
            matches.append(match)
            
            # Extract source file information
            if node.metadata and 'file_name' in node.metadata:
                unique_sources.add(node.metadata['file_name'])
        
        sources_list = sorted(list(unique_sources))
        logger.info(f"Retrieved {len(matches)} matches for query from {len(sources_list)} files")
        
        return RetrievalResponse(
            matches=matches,
            query=request.query,
            total_matches=len(matches),
            sources=sources_list
        )
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {e}"
        )


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "Vault RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "retrieve": "/retrieve",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")