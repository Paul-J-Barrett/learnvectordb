# uv Package Manager Research

## What is uv?

**uv** is an extremely fast Python package manager written in Rust, developed by Astral. It aims to be a drop-in replacement for pip, pip-tools, pipx, poetry, and pyenv.

### Key Differences from Other Tools:

| Feature | uv | pip | poetry | conda |
|---------|-----|-----|--------|-------|
| Speed | 10-100x faster | Baseline | Slow | Very slow |
| Language | Rust | Python | Python | Python |
| Dependency resolver | Modern, fast | Legacy | Good | Different ecosystem |
| Virtualenvs | Built-in | Needs venv | Built-in | Own env system |
| PEP 582 support | Yes | No | No | No |
| Non-Python deps | No | No | No | Yes |

---

## Installation Methods

```bash
# curl (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# pip
pip install uv

# Homebrew
brew install uv

# pipx (recommended)
pipx install uv

# Cargo (from source)
cargo install uv

# Windows (Scoop)
scoop install uv

# Docker
docker run -it ghcr.io/astral-sh/uv:latest
```

---

## Basic Commands

### Project Setup
```bash
# Initialize a new project
uv init myproject
cd myproject

# Create pyproject.toml
uv init --name myproject
uv init --python 3.11  # specific version

# Create virtual environment
uv venv
uv venv --python 3.11

# Activate (source venv/bin/activate on Unix, venv\Scripts\activate on Windows)
```

### Dependency Management
```bash
# Install single package
uv add requests
uv add "requests>=2.28"

# Install dev dependencies
uv add --dev pytest black

# Install from requirements.txt
uv pip install -r requirements.txt

# Install all dependencies from pyproject.toml
uv sync

# Add optional dependency group
uv add --optional extra pandas

# Remove package
uv remove requests

# Upgrade packages
uv lock --upgrade
uv sync --upgrade
```

### Running Commands/Scripts
```bash
# Run Python script
uv run script.py

# Run with specific Python version
uv run --python 3.11 script.py

# Run in project context (uses pyproject.toml deps)
uv run pytest

# One-off commands
uv run python -c "print('hello')"

# Create standalone tool installation (like pipx)
uv tool install ruff
uv tool run ruff check .
```

### Managing Python Versions
```bash
# Install Python versions
uv python install 3.11 3.12

# List installed versions
uv python list

# Create project with specific version
uv init --python 3.12 myproject

# Run with specific version
uv run --python 3.11 script.py
```

### Lock Files & Reproducibility
```bash
# Generate/update lock file
uv lock

# Install exact versions from lock file
uv sync

# Check for updates
uv pip list --outdated
```

---

## Features for Data/ML Projects

1. **PEP 582 Support**: Native support for local package directories (`__pypackages__/`), useful for environments without system-wide installs

2. **Fast Dependency Resolution**: Critical for large ML dependency trees (PyTorch, TensorFlow, etc.)

3. **Workspace Support**: Manage multiple related packages in a monorepo:
   ```toml
   [tool.uv.workspace]
   members = ["packages/*"]
   ```

4. **Compiled Extensions**: Automatic handling of C-extension packages

5. **Alternative Index Support**: Configure multiple package indices for private registries

6. **Cross-platform Lockfiles**: Consistent environments across dev/prod

---

## Integration with Vector Databases

uv works seamlessly with all major vector database clients:

```bash
# Install vector DB libraries
uv add langchain-community
uv add pymilvus          # Milvus
uv add pinecone-client   # Pinecone
uv add qdrant-client     # Qdrant
uv add weaviate-client   # Weaviate
uv add chromadb           # Chroma
uv add faiss-cpu          # FAISS (local)

# Full ML stack example
uv add "torch>=2.0" numpy pandas sentence-transformers transformers
```

---

## Comparison Summary

### When to use uv:
- **New projects**: Start with uv for speed and modern UX
- **CI/CD**: Faster builds, reliable locking
- **Large dependency trees**: ML/data science projects
- **Dev/prod parity**: Lock files ensure consistency
- **Monorepos**: Workspace support

### When to consider alternatives:
- **conda**: If you need non-Python dependencies (R, CUDA, MKL)
- **poetry**: If team already familiar and no performance issues
- **pip**: For simple, one-off installations

---

## Recommendations

### For a New Python Project:
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
uv init myproject
cd myproject
uv venv
source .venv/bin/activate

# Add dependencies
uv add requests pandas numpy
uv add --dev pytest black ruff mypy

# Run development commands
uv run pytest
uv run black .
uv lock  # create reproducible lock file

# CI/CD
uv sync  # install exact versions from lock file
```

### Migration from pip/poetry:
```bash
# Import from requirements.txt
uv add -r requirements.txt

# Import from poetry (creates pyproject.toml if needed)
poetry export -f requirements.txt --without-hashes | uv pip install -r -
```

### Key Takeaways:
1. **Use `uv run`** for reproducible script execution
2. **Use `uv lock`** for production lockfiles
3. **Use `uv python install`** to manage versions
4. **Replace pip-tools**: Use `uv pip compile` for requirements generation

uv is production-ready and recommended for new Python projects, especially in data science/ML workflows where dependency management complexity and build speed matter significantly.

---

## Resources

- **uv Documentation:** https://docs.astral.sh/uv/
- **uv GitHub:** https://github.com/astral-sh/uv
- **Astral Tools:** https://astral.sh/
