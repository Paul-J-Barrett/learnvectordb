#!/usr/bin/env python3
"""
Generate synthetic conversation dataset for vector database learning.

This script creates 100 fake conversations about Python and PostgreSQL topics,
suitable for learning vector search operations.
"""

import csv
import random
import hashlib

random.seed(42)

TOPICS = [
    ("Python debugging", "How to debug Python exceptions and tracebacks effectively"),
    ("SQL optimization", "Techniques for optimizing slow SQL queries"),
    ("PostgreSQL extensions", "Setting up and using PostgreSQL extensions like pgvector"),
    ("Python async", "Understanding async/await patterns in Python"),
    ("Database migrations", "Best practices for database migration strategies"),
    ("ORM vs raw SQL", "Tradeoffs between using ORM and writing raw SQL queries"),
    ("PostgreSQL indexing", "Creating and using indexes effectively in PostgreSQL"),
    ("Python type hints", "Best practices for Python type hints and mypy"),
    ("Connection pooling", "Managing database connection pools in Python"),
    ("PostgreSQL JSONB", "Using JSONB columns for flexible data storage"),
    ("Python decorators", "Creating and using decorators in Python"),
    ("ACID transactions", "Understanding ACID compliance in databases"),
    ("FastAPI database", "Integrating databases with FastAPI applications"),
    ("pytest fixtures", "Using pytest fixtures for database testing"),
    ("Materialized views", "Using PostgreSQL materialized views for performance"),
    ("Python context managers", "Managing resources with context managers"),
    ("Database sharding", "Strategies for horizontal scaling with sharding"),
    ("Python multiprocessing", "Comparing multiprocessing vs threading"),
    ("PostgreSQL performance", "Performance tuning tips for PostgreSQL"),
    ("Virtual environments", "Managing Python dependencies with venv"),
    ("SQLAlchemy patterns", "Advanced SQLAlchemy patterns and techniques"),
    ("PostgreSQL replication", "Setting up database replication"),
    ("Python packaging", "Creating and distributing Python packages"),
    ("Index strategies", "Choosing between B-tree, Hash, and GIN indexes"),
    ("Python generators", "Using generators for memory-efficient iteration"),
    ("Transaction isolation", "Understanding transaction isolation levels"),
    ("PostgreSQL functions", "Creating and optimizing PostgreSQL functions"),
    ("Python comprehensions", "Mastering list, dict, and set comprehensions"),
    ("Database testing", "Strategies for unit testing database code"),
    ("PostgreSQL partitioning", "Table partitioning strategies in PostgreSQL"),
    ("Error handling", "Robust error handling patterns in Python"),
    ("Query caching", "Implementing query result caching"),
    ("PostgreSQL security", "Security best practices for PostgreSQL"),
    ("Python logging", "Effective logging strategies in Python"),
    ("JOIN optimization", "Optimizing complex JOIN operations"),
    ("Python closures", "Understanding closures and scope in Python"),
    ("PostgreSQL monitoring", "Monitoring and alerting for PostgreSQL"),
    ("Data validation", "Validating data before database insertion"),
    ("Python metaclasses", "Advanced metaclass patterns in Python"),
    ("Database locks", "Understanding and managing database locks"),
    ("PostgreSQL VACUUM", "Managing VACUUM and autovacuum for performance"),
    ("Configuration management", "Managing application configuration"),
    ("Python descriptors", "Creating Python descriptor protocols"),
    ("Index maintenance", "Rebuilding and maintaining database indexes"),
    ("PostgreSQL schemas", "Using schemas for database organization"),
    ("Testing patterns", "Integration testing with test databases"),
    ("Python properties", "Using @property and @setter decorators"),
    ("Database connections", "Connection management best practices"),
    ("PostgreSQL arrays", "Working with array columns in PostgreSQL"),
    ("Python concurrency", "Threading and asyncio patterns in Python"),
    ("Query analysis", "Using EXPLAIN ANALYZE for query optimization"),
    ("Python packaging tools", "Comparing pip, poetry, and uv package managers"),
    ("PostgreSQL full-text search", "Implementing full-text search in PostgreSQL"),
    ("Dependency injection", "Patterns for dependency injection in Python"),
    ("Database migrations tools", "Comparing Alembic and Flyway"),
    ("Python iterators", "Creating and using custom iterators"),
    ("PostgreSQL constraints", "Using CHECK, UNIQUE, and FOREIGN KEY constraints"),
    ("Caching strategies", "Implementing application-level caching"),
    ("Python protocols", "Using typing.Protocol for structural typing"),
    ("Database pooling", "Advanced connection pooling configurations"),
    ("PostgreSQL triggers", "Creating and optimizing database triggers"),
    ("Error recovery", "Strategies for database error recovery"),
    ("Python ABCs", "Using abstract base classes for interfaces"),
    ("Query building", "Safe query building to prevent SQL injection"),
    ("PostgreSQL views", "Using views for data abstraction"),
    ("Performance profiling", "Profiling Python database code"),
    ("Python async patterns", "Advanced async patterns with databases"),
    ("Database backups", "Strategies for database backup and recovery"),
    ("Python magic methods", "Implementing __str__, __repr__, and other magic methods"),
    ("PostgreSQL explain", "Interpreting EXPLAIN output for optimization"),
    ("Data serialization", "Serializing and deserializing database data"),
    ("Python context patterns", "Advanced context manager patterns"),
    ("Database health checks", "Implementing health check endpoints"),
    ("PostgreSQL extensions", "Creating custom PostgreSQL extensions"),
    ("Python memory management", "Understanding Python's memory management"),
    ("Query pagination", "Implementing efficient database pagination"),
    ("Python annotations", "Advanced type annotations with @overload"),
    ("PostgreSQL constraints", "Deferrable constraints and immediate checking"),
    ("Testing databases", "Strategies for testing with real databases"),
    ("Python inheritance", "Advanced inheritance patterns in Python classes"),
    ("Database schema design", "Best practices for schema design"),
    ("PostgreSQL statistics", "Using pg_stat for performance analysis"),
    ("Python functional patterns", "Functional programming patterns in Python"),
    ("Index selection", "Choosing the right index type for your queries"),
    ("Python concurrency safety", "Thread-safe database operations"),
    ("PostgreSQL tuning", "PostgreSQL configuration parameter tuning"),
    ("Python metaprogramming", "Dynamic attribute access patterns"),
    ("Database APIs", "Designing database access layers"),
    ("PostgreSQL constraints", "Exclusion constraints and use cases"),
    ("Python error patterns", "Custom exception hierarchies"),
    ("Query patterns", "Common query patterns and their optimizations"),
    ("PostgreSQL functions", "Window functions and common table expressions"),
    ("Python testing tools", "Comparing pytest, unittest, and nose"),
    ("Database migrations", "Zero-downtime migration strategies"),
    ("Python performance", "Performance optimization techniques"),
    ("PostgreSQL arrays", "Working with array functions and operators"),
    ("Dependency management", "Managing complex dependency graphs"),
    ("Database connections", "Connection timeout and retry strategies"),
]

SYSTEM_PROMPTS = [
    "You are a helpful senior developer mentoring a junior engineer.",
    "You are a database administrator helping a developer understand concepts.",
    "You are a Python expert explaining best practices.",
    "You are a systems architect discussing design patterns.",
]

USERNAMES = [
    "alex_dev", "jordan_coder", "taylor_swe", "casey_engineer", "morgan_prog",
    "riley_tech", "quinn_builder", "skyler_hacker", "jamie_coder", "avery_dev",
    "devonte_lead", "sami_architect", "kayden_backend", "marley_fullstack",
    "piper_dba", "finley_sre", "harper_devops", "dakota_backend", "rowan_data",
    "tatum_platform",
]

CONVERSATION_STARTERS = {
    "Python debugging": [
        "I'm getting a traceback that's hard to decipher. Can you help me understand what's happening?",
        "My Python script keeps crashing with an unexpected error. How should I approach debugging?",
    ],
    "SQL optimization": [
        "My query is running very slow on a table with millions of rows. What should I check?",
        "How do I identify which part of my complex JOIN is causing the slowdown?",
    ],
}

def generate_conversation(topic: str, description: str) -> tuple[str, str]:
    """Generate a synthetic conversation pair."""
    username = random.choice(USERNAMES)
    
    user_question = random.choice(CONVERSATION_STARTERS.get(topic, [
        f"I'm learning about {topic.lower()}. Can you explain the key concepts?",
        f"Can you help me understand {description.lower()}?",
        f"I want to learn more about {topic}. What should I know to get started?",
    ]))
    
    answer_content = f"""User's Question:
{user_question}

Assistant's Response:
Thank you for asking about {topic}! Let me explain the key concepts.

**Understanding the Basics**

{topic} is an important concept in modern software development. When working with {topic.lower()}, you'll encounter several fundamental patterns.

**Key Principles**

1. **Start Simple**: Begin with the most straightforward approach before optimizing.
2. **Measure First**: Always profile before making changes to understand actual bottlenecks.
3. **Iterate Slowly**: Make one change at a time to understand the impact.

**Practical Example**

Here's a common pattern for {topic.lower()}:

```python
# Example implementation
def example_function():
    # Step 1: Set up context
    result = []
    
    # Step 2: Process data
    for item in items:
        if condition:
            result.append(transform(item))
    
    # Step 3: Return result
    return result
```

**Common Pitfalls**

- Forgetting to handle edge cases
- Not considering error conditions
- Missing proper cleanup or resource management

**Best Practices**

- Write tests for your implementation
- Document your assumptions
- Consider performance implications early

**Further Learning**

I recommend practicing with small examples first, then gradually increasing complexity. The official documentation and community resources are excellent for deeper understanding.

Is there a specific aspect of {topic} you'd like me to elaborate on?"""
    
    return username, answer_content

def main():
    output_path = "data/conversations.csv"
    
    print("Generating synthetic conversation dataset...")
    print(f"Topics: {len(TOPICS)}")
    print(f"Output: {output_path}")
    print()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'session_content'])
        
        for topic, description in TOPICS:
            username, content = generate_conversation(topic, description)
            writer.writerow([username, content])
    
    print(f"Generated {len(TOPICS)} conversations")
    print(f"Output saved to: {output_path}")
    print()
    print("Next steps:")
    print("  1. Run ./scripts/start-postgres.sh to start the database")
    print("  2. Ingest with: uv run python -m vectordb_learn.db.ingest data/conversations.csv")

if __name__ == "__main__":
    main()
