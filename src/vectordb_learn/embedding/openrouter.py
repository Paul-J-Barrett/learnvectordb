"""OpenRouter client for cloud-based embeddings (fallback)."""

import httpx
from ..config import openrouter as config


async def get_embedding(text: str) -> list[float]:
    """Get embedding using OpenRouter API with Minimax M2.1."""
    if not config.api_key:
        raise ValueError("OpenRouter API key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.model,
                "input": text,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
