"""Ollama client for local embedding generation."""

import ollama
from ..config import ollama as config


async def get_embedding(text: str) -> list[float]:
    """Get embedding for text using local Ollama model."""
    try:
        response = ollama.embed(
            model=config.embed_model,
            input=text,
        )
        return response["embeddings"][0]
    except Exception as e:
        raise RuntimeError(f"Failed to get embedding from Ollama: {e}")


def generate_title(conversation: str) -> str:
    """Generate a title for the conversation using phi4-mini."""
    try:
        response = ollama.chat(
            model=config.title_model,
            messages=[
                {
                    "role": "system",
                    "content": "Generate a short, descriptive title (max 5 words) for this Python/PostgreSQL conversation. Just return the title, no quotes.",
                },
                {"role": "user", "content": conversation[:1000]},
            ],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Failed to generate title: {e}")
