"""Embedding providers for Ollama and OpenRouter."""

from .ollama import get_embedding, generate_title
from .openrouter import get_embedding as get_embedding_openrouter

__all__ = ["get_embedding", "generate_title", "get_embedding_openrouter"]
