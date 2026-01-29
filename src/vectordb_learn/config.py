"""Configuration settings."""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path if env_path.exists() else None)


@dataclass
class PostgresConfig:
    """PostgreSQL connection configuration."""
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "learnvectordb")
    database: str = os.getenv("POSTGRES_DB", "vectordb")
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class OllamaConfig:
    """Ollama configuration for local embeddings."""
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    title_model: str = os.getenv("OLLAMA_TITLE_MODEL", "phi4-mini")
    embedding_dimensions: int = 768


@dataclass
class OpenRouterConfig:
    """OpenRouter API configuration for cloud fallback."""
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "minimax/minimax-m2.1"


@dataclass
class TelemetryConfig:
    """OpenTelemetry configuration."""
    endpoint: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://dockerhost:4318/v1/traces")
    service_name: str = os.getenv("OTEL_SERVICE_NAME", "vectordb-learn")


postgres = PostgresConfig()
ollama = OllamaConfig()
openrouter = OpenRouterConfig()
telemetry = TelemetryConfig()