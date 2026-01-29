"""Flashcard data generator using OpenRouter API."""

import asyncio
import csv
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import httpx


env_path = Path(__file__).parent.parent.parent / ".env"
env_example_path = Path(__file__).parent.parent.parent / ".env.example"

if not env_path.exists() and env_example_path.exists():
    shutil.copy(env_example_path, env_path)

load_dotenv(env_path)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "minimax/minimax-m2.1"


FLASH_CARD_TOPICS = {
    "pgvector": [
        ("What SQL data type does pgvector provide for storing vectors?", "vector(n) where n is the number of dimensions"),
        ("What operators does pgvector provide for vector comparison?", "<=> for cosine, <-> for Euclidean, <#> for inner product, <+> for Manhattan"),
        ("How do you enable the pgvector extension in PostgreSQL?", "CREATE EXTENSION IF NOT EXISTS vector;"),
        ("What is the maximum number of dimensions for a pgvector vector type?", "16,000 dimensions"),
        ("What index types does pgvector support for approximate nearest neighbor search?", "HNSW and IVFFlat"),
        ("What does HNSW stand for?", "Hierarchical Navigable Small World"),
        ("What does IVFFlat stand for?", "Inverted File Flat"),
        ("Which pgvector index is recommended for production workloads?", "HNSW (faster queries at same recall level)"),
        ("What is the formula for cosine distance used in pgvector?", "1 - (A · B) / (||A|| × ||B||)"),
        ("What is the purpose of the m parameter in HNSW indexing?", "Number of connections per layer (higher = more memory, better recall)"),
        ("What is the purpose of ef_construction in HNSW indexing?", "Index build quality (higher = slower build, better recall)"),
        ("How do you create an HNSW index in pgvector?", "CREATE INDEX ON table USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"),
        ("What is the recommended shared memory size for HNSW index builds?", "At least 1GB, preferably 2GB+"),
        ("What does halfvec(n) data type store?", "Half-precision (16-bit) floating point vectors, using 50% less storage"),
        ("What is binary quantization in pgvector?", "Converting float vectors to binary for faster search with less memory"),
        ("How do you insert a vector into pgvector?", "INSERT INTO table (embedding) VALUES ('[0.1, 0.2, 0.3, ...]');"),
        ("What is the difference between exact and approximate nearest neighbor search?", "Exact returns perfect recall but is slow; approximate (HNSW/IVFFlat) is faster with some recall loss"),
        ("What SQL function returns the dimension of a vector?", "vector_dims(embedding_column)"),
        ("How does pgvector store vector data internally?", "In a custom, memory-efficient binary format"),
        ("Does pgvector support write-ahead logging (WAL)?", "Yes, providing ACID compliance for vector operations"),
    ],
    "ollama_python": [
        ("What Python library is used to interact with Ollama?", "ollama (pip install ollama)"),
        ("How do you generate embeddings with Ollama in Python?", "response = ollama.embed(model='model-name', input='text')"),
        ("What does ollama.embed() return?", "A dictionary with 'embeddings' key containing a list of embedding vectors"),
        ("How do you chat with a model using Ollama Python library?", "response = ollama.chat(model='model-name', messages=[{'role': 'user', 'content': 'hello'}])"),
        ("What is the default host for Ollama API?", "http://localhost:11434"),
        ("How do you specify a different host for Ollama?", "OLLAMA_HOST=http://remote:11434 ollama pull model"),
        ("What is nomic-embed-text commonly used for?", "Generating text embeddings (384 dimensions)"),
        ("How do you pull a model in Ollama?", "ollama pull model-name"),
        ("How do you list installed models?", "ollama list"),
        ("What is phi4-mini useful for?", "Lightweight chat and title generation tasks"),
        ("How do you delete a model in Ollama?", "ollama rm model-name"),
        ("What is the structure of an Ollama chat response?", "Dict with 'message' key containing {'role': '...', 'content': '...'}"),
        ("How do you stream responses with Ollama?", "ollama.chat(model='name', messages=[...], stream=True)"),
        ("What is the difference between generate and chat in Ollama?", "generate is for text completion; chat is for conversational interactions"),
        ("What timeout parameters can be set for Ollama requests?", "request_timeout parameter in seconds"),
    ],
    "openrouter_python": [
        ("What is OpenRouter?", "A unified API gateway for accessing multiple LLM providers"),
        ("How do you authenticate with OpenRouter?", "Bearer token in Authorization header"),
        ("What Python HTTP client is commonly used with OpenRouter?", "httpx (async) or requests (sync)"),
        ("What is the base URL for OpenRouter API?", "https://openrouter.ai/api/v1"),
        ("How do you make a chat completion request to OpenRouter?", "POST to /chat/completions with model and messages"),
        ("What is Minimax M2.1?", "A fast, efficient LLM model available through OpenRouter"),
        ("How do you structure messages for OpenRouter?", "[{'role': 'system', 'content': '...'}, {'role': 'user', 'content': '...'}]"),
        ("What is the purpose of the 'model' parameter in OpenRouter requests?", "Specifies which LLM to use (e.g., 'minimax/minimax-m2.1')"),
        ("What does temperature control in LLM requests?", "Randomness of output (0 = deterministic, 1 = creative)"),
        ("What is max_tokens parameter?", "Maximum number of tokens in the response"),
        ("How do you handle rate limits in OpenRouter?", "Check X-RateLimit-Remaining headers and implement backoff"),
        ("What is the purpose of the /models endpoint?", "Lists available models and their pricing"),
        ("How do you enable streaming with OpenRouter?", "Set stream=True and iterate over the response chunks"),
        ("What information does OpenRouter provide about costs?", "Credits used and remaining in response headers"),
        ("How do you specify response format in OpenRouter?", "Use 'response_format' parameter for JSON mode"),
    ],
    "pydantic_ai": [
        ("What is pydantic-ai?", "A Python framework for building AI applications with type safety"),
        ("What company maintains pydantic-ai?", "Pydantic (makers of Pydantic validation)"),
        ("How do you define a system prompt in pydantic-ai?", "Pass 'system_prompt' parameter to Agent or use @agent.system_prompt decorator"),
        ("What is an Agent in pydantic-ai?", "A class that manages LLM interactions with typed inputs/outputs"),
        ("How do you specify the model for an agent?", "agent = Agent(model='openrouter:minimax/minimax-m2.1')"),
        ("What is the RunResult class in pydantic-ai?", "Contains the LLM's text response and any structured data"),
        ("How do you pass dependencies to an agent?", "Provide deps parameter to agent.run()"),
        ("What is the purpose of result_type in agent.run()?", "Specifies Pydantic model for structured output"),
        ("How do you stream responses in pydantic-ai?", "Use agent.run_streamed() instead of agent.run()"),
        ("What is system_prompt in pydantic-ai?", "A decorator or parameter that sets the AI's behavior instructions"),
        ("How does pydantic-ai handle type validation?", "Uses Pydantic models to validate inputs and outputs"),
        ("What is the difference between Agent and Worker in pydantic-ai?", "Agent is for conversational AI; Worker is for tool use"),
        ("How do you create a structured output with pydantic-ai?", "Define a Pydantic model and pass it to result_type parameter"),
        ("What is the current_status property in pydantic-ai?", "Tracks the state of agent execution (running, complete, failed)"),
        ("How do you handle errors in pydantic-ai?", "Try/except around agent.run() or use result.raise_on_failure()"),
    ],
    "postgresql_python": [
        ("What is asyncpg?", "A pure-Python, async PostgreSQL client"),
        ("How do you create a connection pool in asyncpg?", "pool = await asyncpg.create_pool(host='...', user='...', password='...', database='...')"),
        ("What is the difference between fetch and fetchval in asyncpg?", "fetch returns all rows; fetchval returns single value"),
        ("How do you execute a query with asyncpg?", "await conn.execute('SQL_QUERY') or await conn.fetch('SQL_QUERY')"),
        ("What is psycopg2-binary?", "A PostgreSQL adapter for Python (synchronous)"),
        ("How do you connect with psycopg2?", "conn = psycopg2.connect('postgresql://user:pass@host/db')"),
        ("How do you prevent SQL injection in Python PostgreSQL?", "Use parameterized queries with %s placeholders"),
        ("What is connection pooling and why use it?", "Maintains open connections for reuse, reducing connection overhead"),
        ("How do you fetch a single row in asyncpg?", "await conn.fetchrow('SELECT * FROM table WHERE id = $1', id)"),
        ("What is the purpose of min_size and max_size in connection pool?", "Minimum and maximum number of connections to maintain"),
        ("How do you handle transactions in psycopg2?", "Use context manager: with conn.cursor() as cur: or conn.commit()/conn.rollback()"),
        ("What is SQLAlchemy?", "An ORM and SQL toolkit for Python databases"),
        ("How do you create a table with SQLAlchemy?", "Table('name', metadata, Column('id', Integer, primary_key=True), ...)"),
        ("What is the difference between core and ORM in SQLAlchemy?", "Core is direct SQL manipulation; ORM maps Python objects to database rows"),
        ("How do you close a connection in asyncpg?", "await conn.close() or await pool.close()"),
    ],
    "ai_embeddings": [
        ("What is a text embedding?", "A vector representation of text that captures semantic meaning"),
        ("What is embedding dimension?", "The length of the vector (e.g., 384, 768, 1536)"),
        ("What is cosine similarity?", "A measure of angle between two vectors (range -1 to 1, higher = more similar)"),
        ("What is the difference between cosine distance and cosine similarity?", "Cosine similarity measures similarity (higher = closer); cosine distance measures difference (lower = closer)"),
        ("What is the formula for cosine similarity?", "(A · B) / (||A|| × ||B||)"),
        ("What embedding model produces 384-dimensional vectors?", "nomic-embed-text"),
        ("What OpenAI embedding model should you use for text?", "text-embedding-3-small (1536 dimensions)"),
        ("What is embedding normalization?", "Scaling vectors to unit length for consistent similarity calculations"),
        ("What is batch embedding?", "Generating embeddings for multiple texts in a single API call"),
        ("What is the difference between symmetric and asymmetric embeddings?", "Symmetric: same model for queries and documents; asymmetric: different models for short queries vs long documents"),
        ("What is mean pooling in embeddings?", "Averaging token embeddings to get sentence-level representation"),
        ("What is the maximum input length for most embedding models?", "8192 tokens"),
        ("What is embedding quantization?", "Reducing precision of vectors to save memory (e.g., float32 to int8)"),
        ("How do embeddings enable semantic search?", "Similar concepts have similar vectors, allowing nearest-neighbor search"),
        ("What is the relationship between embedding quality and search accuracy?", "Better embeddings produce more accurate semantic search results"),
    ],
    "vector_databases": [
        ("What is a vector database?", "A database optimized for storing and searching vector embeddings"),
        ("What is nearest neighbor search?", "Finding vectors closest to a query vector based on distance metric"),
        ("What is approximate nearest neighbor (ANN)?", "A fast search algorithm that trades some accuracy for speed"),
        ("What are the main ANN indexing algorithms?", "HNSW, IVFFlat, Product Quantization, LSH"),
        ("What is recall in vector search?", "Percentage of true nearest neighbors returned by the search"),
        ("What is latency in vector search?", "Time to return search results"),
        ("What is index build time?", "Time required to create the vector index structure"),
        ("What is the difference between exact and approximate search?", "Exact finds all true neighbors (slow); approximate finds most neighbors (fast)"),
        ("What is a distance metric?", "A function that measures similarity between vectors (cosine, Euclidean, inner product)"),
        ("What is a vector index?", "A data structure that enables fast similarity search"),
        ("What is filtering in vector search?", "Combining vector similarity with metadata filters"),
        ("What is hybrid search?", "Combining vector similarity with keyword/full-text search"),
        ("What is reranking?", "Using a more expensive model to refine ANN search results"),
        ("What is the trade-off between recall and latency?", "Higher recall typically requires longer search time"),
        ("What is vector quantization?", "Compressing vectors by reducing precision to save storage and memory"),
    ],
    "ai_overview": [
        ("What is an LLM?", "Large Language Model - a neural network trained on vast amounts of text data"),
        ("What is tokenization?", "Breaking text into smaller units (tokens) that models can process"),
        ("What is a system prompt?", "Instructions that define the AI's behavior and personality"),
        ("What is few-shot learning?", "Providing examples in the prompt to guide model behavior"),
        ("What is temperature in LLM generation?", "Controls randomness of output (0 = deterministic, 1 = creative)"),
        ("What is max_tokens?", "Maximum number of tokens the model can generate"),
        ("What is a prompt template?", "A reusable structure for building prompts with variable substitution"),
        ("What is RAG?", "Retrieval-Augmented Generation - combining search with LLM generation"),
        ("What is the difference between completion and chat completion?", "Completion completes a prefix; chat completion follows conversation format"),
        ("What is context window?", "Maximum tokens the model can see at once"),
        ("What is a token?", "A unit of text (roughly 4 characters or 0.75 words)"),
        ("What is prompt engineering?", "Crafting effective prompts to get desired model outputs"),
        ("What is fine-tuning?", "Training a model on specific data for improved performance on tasks"),
        ("What is embeddings API?", "A service that converts text to vector representations"),
        ("What is the difference between text-generation and embeddings?", "Text-generation produces new text; embeddings convert text to vectors"),
    ],
}


def generate_flashcard(topic: str, question_template: str) -> tuple[str, str]:
    """Generate a single flashcard using OpenRouter API."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env file")
    
    prompt = f"""Generate a flashcard question and answer on the topic: {topic}

Question: {question_template}

Format your response as:
QUESTION: [your question]
ANSWER: [your answer]

Make the question specific and technical. Keep the answer concise but informative."""

    async def call_api():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/anomalyco/learnVectordb",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a technical educator creating flashcards. Generate precise, accurate questions and answers."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 256,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    content = asyncio.run(call_api())
    
    lines = content.split("\n")
    question = ""
    answer = ""
    for line in lines:
        if line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()
    
    return question or "Question", answer or "Answer"


def generate_flashcards(num_per_topic: int = 5) -> list[tuple[str, str]]:
    """Generate flashcards using OpenRouter API."""
    flashcards = []
    total_needed = 400
    per_topic = max(1, total_needed // len(FLASH_CARD_TOPICS))
    
    print(f"Generating {total_needed} flashcards...")
    
    for topic, templates in FLASH_CARD_TOPICS.items():
        print(f"  Processing topic: {topic}")
        topic_flashcards = []
        
        for i in range(per_topic):
            template = templates[i % len(templates)]
            try:
                question, answer = generate_flashcard(topic, template)
                topic_flashcards.append((question, answer))
                print(f"    [{i+1}/{per_topic}] Generated: {question[:50]}...")
            except Exception as e:
                print(f"    [{i+1}/{per_topic}] Error: {e}")
                topic_flashcards.append((f"Q: {template}", "A: [Generation failed - see documentation]"))
            
            if len(topic_flashcards) + len(flashcards) >= total_needed:
                break
        
        flashcards.extend(topic_flashcards)
        
        if len(flashcards) >= total_needed:
            break
    
    return flashcards[:total_needed]


def make_flashcards():
    """Main function to generate and save flashcards CSV."""
    import shutil
    
    output_path = Path(__file__).parent.parent.parent / "data" / "flashcards.csv"
    example_path = Path(__file__).parent.parent.parent / "data" / "flashcards.csv.example"
    
    if output_path.exists():
        backup_path = Path(__file__).parent.parent.parent / "data" / f"flashcards_backup.csv"
        shutil.copy(output_path, backup_path)
        print(f"Backed up existing flashcards to: {backup_path}")
    
    flashcards = generate_flashcards(num_per_topic=50)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['question', 'answer'])
        for question, answer in flashcards:
            writer.writerow([question, answer])
    
    with open(example_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['question', 'answer'])
        for question, answer in flashcards[:10]:
            writer.writerow([question, answer])
    
    print(f"\nGenerated {len(flashcards)} flashcards")
    print(f"Saved to: {output_path}")
    print(f"Example saved to: {example_path}")
    
    return flashcards


if __name__ == "__main__":
    make_flashcards()