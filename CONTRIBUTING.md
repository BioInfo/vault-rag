# Contributing to Vault RAG

We love your input! We want to make contributing to Vault RAG as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vault-rag.git
   cd vault-rag
   ```

2. **Set up development environment**
   ```bash
   python -m venv vault-rag-env
   source vault-rag-env/bin/activate  # On Windows: vault-rag-env\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Configure for development**
   ```bash
   cp .env.example .env
   # Edit .env with your test vault path
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

Run these before submitting:

```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy server/

# Run tests
pytest
```

## Testing

Please add tests for any new functionality. We use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server

# Run specific test file
pytest tests/test_api.py
```

### Test Structure

```
tests/
├── test_api.py           # API endpoint tests
├── test_config.py        # Configuration tests
├── test_ingestion.py     # Document ingestion tests
└── fixtures/             # Test data
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions and classes
- Update API documentation if you change endpoints
- Keep examples up to date

## Submitting Changes

### Bug Reports

Use GitHub issues to track public bugs. Write bug reports with detail, background, and sample code.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Feature Requests

We track feature requests using GitHub issues. When submitting a feature request:

- Explain the motivation behind the feature
- Provide a clear description of the functionality
- Include examples of how it would be used
- Consider the scope and complexity

### Code Guidelines

#### Python Style

- Follow PEP 8
- Use type hints for function parameters and return values
- Write descriptive variable and function names
- Keep functions focused and small
- Use docstrings for modules, classes, and functions

```python
def retrieve_documents(query: str, top_k: int = 5) -> List[RetrievalMatch]:
    """Retrieve relevant documents for a query.
    
    Args:
        query: The search query string
        top_k: Number of results to return (default: 5)
        
    Returns:
        List of retrieval matches sorted by relevance
        
    Raises:
        ValueError: If query is empty or top_k is invalid
    """
    pass
```

#### API Design

- Use clear, RESTful endpoint names
- Include proper HTTP status codes
- Provide comprehensive error messages
- Use Pydantic models for request/response validation
- Document all endpoints with OpenAPI/Swagger

#### Configuration

- Use environment variables for configuration
- Provide sensible defaults
- Document all configuration options
- Support both `.env` files and direct environment variables

## Project Structure

Understanding the codebase structure:

```
vault-rag/
├── server/              # FastAPI application
│   ├── __init__.py
│   ├── main.py         # API endpoints and server
│   └── config.py       # Configuration management
├── scripts/            # Utility scripts
│   └── ingest.py      # Document ingestion
├── tests/             # Test suite
├── docs/              # Additional documentation
├── .env.example       # Example configuration
├── requirements.txt   # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Create release tag
6. Update documentation

## Questions?

Feel free to open an issue for questions about contributing, or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in our README.md and release notes.

Thank you for contributing to Vault RAG! 🚀