# 🏛️ Vault RAG

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-blue)](https://www.llamaindex.ai/)
[![Vector Store: ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-orange)](https://www.trychroma.com/)

**A powerful Retrieval-Augmented Generation (RAG) API for your personal knowledge vault**

Transform your markdown notes into an intelligent, searchable knowledge base with semantic search capabilities.

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-api-documentation) • [⚙️ Configuration](#-configuration) • [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

🔍 **Semantic Search** - Find relevant information using natural language queries, not just keywords

📝 **Markdown-Native** - Works seamlessly with your existing markdown notes and vaults

🚀 **High Performance** - Built with FastAPI for lightning-fast API responses

🧠 **Smart Chunking** - Intelligent document splitting preserves context and meaning

🔌 **Easy Integration** - RESTful API that works with any application or workflow

🏗️ **Extensible** - Modular architecture supports custom embeddings and vector stores

📊 **Rich Metadata** - Preserves file structure, frontmatter, and document relationships

🔒 **Privacy-First** - Run entirely locally - your data never leaves your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vault-rag.git
   cd vault-rag
   ```

2. **Set up Python environment**
   ```bash
   python -m venv vault-rag-env
   source vault-rag-env/bin/activate  # On Windows: vault-rag-env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure your vault**
   ```bash
   cp .env.example .env
   # Edit .env with your vault path and preferences
   ```

4. **Ingest your documents**
   ```bash
   python scripts/ingest.py --vault /path/to/your/markdown/vault
   ```

5. **Start the server**
   ```bash
   uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```

6. **Test the API**
   ```bash
   curl -X POST "http://localhost:8000/retrieve" \
        -H "Content-Type: application/json" \
        -d '{"query": "machine learning concepts", "top_k": 5}'
   ```

Visit `http://localhost:8000/docs` for the interactive API documentation!

## 📖 API Documentation

### Retrieve Documents

**POST** `/retrieve`

Search your knowledge vault using natural language queries.

```bash
curl -X POST "http://localhost:8000/retrieve" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the benefits of RAG?",
       "top_k": 5
     }'
```

**Response:**
```json
{
  "matches": [
    {
      "text": "RAG combines retrieval and generation...",
      "score": 0.89,
      "metadata": {
        "file_name": "rag-concepts.md",
        "file_path": "/vault/ai/rag-concepts.md"
      }
    }
  ],
  "query": "What are the benefits of RAG?",
  "total_matches": 5,
  "sources": ["rag-concepts.md", "ai-overview.md"]
}
```

### Health Check

**GET** `/health`

Check the status of your RAG system.

```bash
curl http://localhost:8000/health
```

## ⚙️ Configuration

Configure Vault RAG using environment variables. Create a `.env` file or copy from `.env.example`:

```bash
# Path to your markdown vault
VAULT_PATH=./example-vault

# Storage for processed data
STORAGE_DIR=./storage

# Embedding model (Hugging Face)
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Retrieval settings
DEFAULT_TOP_K=5
MAX_TOP_K=20

# Document chunking
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

### Supported File Types

- `.md` - Markdown files
- `.mdx` - MDX files
- YAML frontmatter support
- Automatic exclusion of `.git`, `.obsidian`, and other system directories

## 🛠️ Development

### Project Structure

```
vault-rag/
├── server/           # FastAPI application
│   ├── main.py      # API endpoints and server setup
│   └── config.py    # Configuration management
├── scripts/         # Utility scripts
│   └── ingest.py   # Document ingestion and indexing
├── storage/        # Generated data (gitignored)
│   ├── chroma/     # ChromaDB vector store
│   └── index/      # LlamaIndex storage
└── requirements.txt # Python dependencies
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=server tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy server/
```

## 🔌 Integration Examples

### Python Client

```python
import requests

def search_vault(query: str, top_k: int = 5):
    response = requests.post(
        "http://localhost:8000/retrieve",
        json={"query": query, "top_k": top_k}
    )
    return response.json()

# Search your vault
results = search_vault("machine learning workflows")
for match in results["matches"]:
    print(f"Score: {match['score']:.2f}")
    print(f"Source: {match['metadata']['file_name']}")
    print(f"Text: {match['text'][:200]}...")
    print("---")
```

### cURL Command

```bash
# Add this as a shell function for quick searches
vault_search() {
    curl -s -X POST "http://localhost:8000/retrieve" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"$1\", \"top_k\": ${2:-5}}" | jq .
}

# Usage: vault_search "kubernetes deployment" 3
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contributing Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/vault-rag&type=Timeline)](https://star-history.com/#yourusername/vault-rag&Timeline)

</div>

---

<div align="center">

**[⬆ Back to Top](#-vault-rag)**

Made with ❤️ for the knowledge management community

</div>