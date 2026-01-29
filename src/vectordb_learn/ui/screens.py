"""Textual screens for the vector database learner."""

import asyncio
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Static, Label, Log

from ..db.operations import (
    search_similar, create_hnsw_index,
    create_ivfflat_index, drop_indexes, explain_query, get_schema_stats, create_schema
)
from ..embedding.ollama import get_embedding
from ..csv.loader import load_csv


class HomeScreen(Screen):
    """Main menu screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("╔══════════════════════════════════════════════════╗", classes="title"),
            Static("║     VECTOR DATABASE LEARNING TOOL v0.1          ║", classes="title"),
            Static("╚══════════════════════════════════════════════════╝", classes="title"),
            Static("Learn PostgreSQL + pgvector through hands-on experimentation", classes="subtitle"),
            Vertical(
                Button("1. Ingest CSV Data", id="ingest", classes="menu-btn"),
                Button("2. Vector Search", id="search", classes="menu-btn"),
                Button("3. Explain Query", id="explain", classes="menu-btn"),
                Button("4. Index Manager", id="indexes", classes="menu-btn"),
                Button("5. SQL Playground", id="playground", classes="menu-btn"),
                Button("6. View Metrics", id="metrics", classes="menu-btn"),
                Button("q. Quit", id="quit", classes="menu-btn quit-btn"),
                classes="menu",
            ),
            Static("Press F1 for help | F2 for debug panel", classes="footer"),
            id="home",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "ingest":
            self.app.push_screen("ingest")
        elif button_id == "search":
            self.app.push_screen("search")
        elif button_id == "explain":
            self.app.push_screen("explain")
        elif button_id == "indexes":
            self.app.push_screen("indexes")
        elif button_id == "playground":
            self.app.push_screen("playground")
        elif button_id == "metrics":
            self.app.push_screen("metrics")
        elif button_id == "quit":
            self.app.exit()


class SearchScreen(Screen):
    """Vector similarity search screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ VECTOR SIMILARITY SEARCH ━━━", classes="section-title"),
            Horizontal(
                Input(placeholder="Enter search query (e.g., 'How to optimize SQL queries')...", 
                      id="search_query", classes="search-input"),
                Button("Search", id="do_search", variant="primary", classes="search-btn"),
                classes="search-row",
            ),
            Static("━ Results ━", classes="section-title"),
            Static("Results will appear here...", id="results", classes="results-area"),
            Static("━ Explanation ━", classes="section-title"),
            Static("Use F2 to toggle explanation panel", id="explanation", classes="explanation-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                Button("Clear", id="clear", variant="warning"),
                classes="nav-row",
            ),
            id="search",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "clear":
            self.query_one("#search_query", Input).value = ""
            self.query_one("#results", Static).update("Results will appear here...")
        elif event.button.id == "do_search":
            query = self.query_one("#search_query", Input).value
            if query:
                async def run_search():
                    try:
                        self.query_one("#results", Static).update("Generating embedding...")
                        self.query_one("#explanation", Static).update("Generating embedding via Ollama...")
                        embedding = await get_embedding(query)
                        self.query_one("#results", Static).update("Searching...")
                        self.query_one("#explanation", Static).update(f"Searching with cosine distance (<=>)...\nQuery: {query[:50]}...\nEmbedding dim: {len(embedding)}")
                        results = await search_similar(self.app.pool, embedding, limit=10)
                        if results:
                            lines = ["Results:"]
                            for r in results:
                                preview = r.get('session_content', '')[:80].replace('\n', ' ')
                                lines.append(f"[{r['distance']:.3f}] {r.get('session_title', 'Untitled')[:40]}")
                                lines.append(f"   {preview}...")
                                lines.append("")
                            self.query_one("#results", Static).update("\n".join(lines))
                            self.query_one("#explanation", Static).update(
                                f"Searched {len(results)} results using cosine similarity.\n"
                                f"Distance formula: 1 - cosine_similarity\n"
                                f"Lower distance = more similar"
                            )
                        else:
                            self.query_one("#results", Static).update("No results found.")
                    except Exception as e:
                        self.query_one("#results", Static).update(f"Error: {e}")
                        self.query_one("#explanation", Static).update(f"Error: {e}")
                asyncio.create_task(run_search())


class IngestScreen(Screen):
    """CSV ingestion screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ INGEST CSV DATA ━━━", classes="section-title"),
            Horizontal(
                Input(placeholder="CSV file path (default: data/conversations.csv)", 
                      id="csv_path", classes="input"),
                Button("Ingest", id="do_ingest", variant="primary"),
                classes="input-row",
            ),
            Static("━ Progress ━", classes="section-title"),
            Log(id="progress_log", classes="log-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="ingest",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "do_ingest":
            path = self.query_one("#csv_path", Input).value or "data/conversations.csv"
            async def do_ingest():
                try:
                    self.query_one("#progress_log", Log).write_line(f"Ingesting {path}...")
                    await create_schema(self.app.pool)
                    count = await load_csv(self.app.pool, path)
                    self.query_one("#progress_log", Log).write_line(f"Successfully ingested {count} rows!")
                except Exception as e:
                    self.query_one("#progress_log", Log).write_line(f"Error: {e}")
            asyncio.create_task(do_ingest())


def get_dummy_embedding() -> str:
    """Generate a 768-dimensional zero vector for demo queries."""
    return "[" + ", ".join(["0.1"] * 768) + "]"

class ExplainScreen(Screen):
    """Query explanation screen."""

    def compose(self) -> ComposeResult:
        dummy_vec = get_dummy_embedding()
        yield Container(
            Static("━━━ EXPLAIN QUERY ━━━", classes="section-title"),
            Static("View the actual SQL and execution plan for vector searches.", classes="info"),
            Static("━ Example Query ━", classes="section-title"),
            Static(
                f"SELECT * FROM conversations ORDER BY embedding <=> '{dummy_vec[:50]}...' LIMIT 10",
                id="example_query",
                classes="code-area-small",
            ),
            Horizontal(
                Button("Explain Cosine (<=>)", id="explain_cosine", variant="primary"),
                Button("Explain L2 (<->)", id="explain_l2", variant="primary"),
                Button("Explain Inner (<#>)", id="explain_inner", variant="primary"),
                classes="btn-row",
            ),
            Static("━ EXPLAIN ANALYZE Output ━", classes="section-title"),
            Static("Run an explanation to see the output...", id="explain_output", classes="code-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="explain",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()

        elif event.button.id == "explain_cosine":
            dummy_vec = get_dummy_embedding()
            self.query_one("#example_query", Static).update(
                f"SELECT * FROM conversations ORDER BY embedding <=> '{dummy_vec[:50]}...' LIMIT 10"
            )
            async def run_explain():
                try:
                    result = await explain_query(
                        self.app.pool,
                        f"SELECT * FROM conversations ORDER BY embedding <=> '{dummy_vec}' LIMIT 10"
                    )
                    if result:
                        self.query_one("#explain_output", Static).update(str(result))
                    else:
                        self.query_one("#explain_output", Static).update("No results returned.")
                except Exception as e:
                    self.query_one("#explain_output", Static).update(f"Error running EXPLAIN ANALYZE. Make sure the database is running and has data.\n\nDetails: {e}")
            asyncio.create_task(run_explain())

        elif event.button.id == "explain_l2":
            dummy_vec = get_dummy_embedding()
            self.query_one("#example_query", Static).update(
                f"SELECT * FROM conversations ORDER BY embedding <-> '{dummy_vec[:50]}...' LIMIT 10"
            )
            async def run_explain():
                try:
                    result = await explain_query(
                        self.app.pool,
                        f"SELECT * FROM conversations ORDER BY embedding <-> '{dummy_vec}' LIMIT 10"
                    )
                    if result:
                        self.query_one("#explain_output", Static).update(str(result))
                    else:
                        self.query_one("#explain_output", Static).update("No results returned.")
                except Exception as e:
                    self.query_one("#explain_output", Static).update(f"Error running EXPLAIN ANALYZE. Make sure the database is running and has data.\n\nDetails: {e}")
            asyncio.create_task(run_explain())

        elif event.button.id == "explain_inner":
            dummy_vec = get_dummy_embedding()
            self.query_one("#example_query", Static).update(
                f"SELECT * FROM conversations ORDER BY embedding <#> '{dummy_vec[:50]}...' LIMIT 10"
            )
            async def run_explain():
                try:
                    result = await explain_query(
                        self.app.pool,
                        f"SELECT * FROM conversations ORDER BY embedding <#> '{dummy_vec}' LIMIT 10"
                    )
                    if result:
                        self.query_one("#explain_output", Static).update(str(result))
                    else:
                        self.query_one("#explain_output", Static).update("No results returned.")
                except Exception as e:
                    self.query_one("#explain_output", Static).update(f"Error running EXPLAIN ANALYZE. Make sure the database is running and has data.\n\nDetails: {e}")
            asyncio.create_task(run_explain())


class IndexScreen(Screen):
    """Index management screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ INDEX MANAGER ━━━", classes="section-title"),
            Static("Create and compare different vector index types.", classes="info"),
            Horizontal(
                Button("Create HNSW", id="create_hnsw", variant="success"),
                Button("Create IVFFlat", id="create_ivfflat", variant="success"),
                Button("Drop Indexes", id="drop_idx", variant="warning"),
                Button("Refresh", id="refresh_idx", variant="primary"),
                classes="btn-row",
            ),
            Static("━ Current Indexes ━", classes="section-title"),
            Static("Loading indexes...", id="index_info", classes="info-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="indexes",
        )

    async def on_mount(self) -> None:
        await self.load_indexes()

    async def load_indexes(self) -> None:
        try:
            stats = await get_schema_stats(self.app.pool)
            lines = [f"Total rows: {stats['row_count']}", "", "Indexes:"]
            if stats['indexes']:
                for idx in stats['indexes']:
                    lines.append(f"  • {idx['indexname']} ({idx['size']})")
            else:
                lines.append("  No indexes found")
            self.query_one("#index_info", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#index_info", Static).update(f"Error loading indexes: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()

        elif event.button.id == "create_hnsw":
            async def create_idx():
                try:
                    result = await create_hnsw_index(self.app.pool)
                    self.query_one("#index_info", Static).update(result)
                    await self.load_indexes()
                except Exception as e:
                    self.query_one("#index_info", Static).update(f"Error: {e}")
            asyncio.create_task(create_idx())

        elif event.button.id == "create_ivfflat":
            async def create_idx():
                try:
                    result = await create_ivfflat_index(self.app.pool)
                    self.query_one("#index_info", Static).update(result)
                    await self.load_indexes()
                except Exception as e:
                    self.query_one("#index_info", Static).update(f"Error: {e}")
            asyncio.create_task(create_idx())

        elif event.button.id == "drop_idx":
            async def drop_idx():
                try:
                    result = await drop_indexes(self.app.pool)
                    self.query_one("#index_info", Static).update(result)
                    await self.load_indexes()
                except Exception as e:
                    self.query_one("#index_info", Static).update(f"Error: {e}")
            asyncio.create_task(drop_idx())

        elif event.button.id == "refresh_idx":
            asyncio.create_task(self.load_indexes())


class PlaygroundScreen(Screen):
    """SQL playground screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ SQL PLAYGROUND ━━━", classes="section-title"),
            Static("Write and execute custom SQL queries.", classes="info"),
            Static("━ Custom Query ━", classes="section-title"),
            Input(placeholder="SELECT * FROM conversations ORDER BY embedding <=> '[0.1, 0.2, ...]' LIMIT 10",
                  id="custom_sql", classes="sql-input"),
            Horizontal(
                Button("Execute", id="run_sql", variant="primary"),
                Button("Clear", id="clear_sql", variant="warning"),
                classes="btn-row",
            ),
            Static("━ Results ━", classes="section-title"),
            Log(id="sql_results", classes="log-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="playground",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "clear_sql":
            self.query_one("#custom_sql", Input).value = ""
        elif event.button.id == "run_sql":
            query = self.query_one("#custom_sql", Input).value
            if query:
                async def run_q():
                    try:
                        async with self.app.pool.acquire() as conn:
                            rows = await conn.fetch(query)
                            for r in rows:
                                self.query_one("#sql_results", Log).write_line(str(dict(r)))
                    except Exception as e:
                        self.query_one("#sql_results", Log).write_line(f"Error: {e}")
                asyncio.create_task(run_q())


class MetricsScreen(Screen):
    """Performance metrics screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ PERFORMANCE METRICS ━━━", classes="section-title"),
            Horizontal(
                Static("━ Database Stats ━", classes="section-title"),
                Static("━ Query Stats ━", classes="section-title"),
                classes="stats-row",
            ),
            Static("Connection pool, query times, and index statistics will appear here.",
                   id="metrics_output", classes="metrics-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="metrics",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


class HelpScreen(Screen):
    """Help screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ KEYBOARD SHORTCUTS ━━━", classes="section-title"),
            Static("""
F1         Show this help
F2         Toggle debug panel
F3         Toggle SQL view
q / Esc    Quit current screen
Ctrl+C     Exit application

━━━ VECTOR CONCEPTS ━━━

Vector: A list of numbers representing data in N-dimensional space.
Embedding: Converting text/images to vectors using ML models.

pgvector Operators:
  <=>  Cosine distance (most common)
  <->  Euclidean (L2) distance
  <#>  Negative inner product
  <+>  Manhattan distance

Index Types:
  HNSW   Fast queries, higher memory (recommended)
  IVFFlat Faster build, slightly slower queries
  None   Sequential scan (slow for large datasets)

━━━ EMBEDDING MODELS ━━━

Local (Ollama):
  nomic-embed-text: 384 dimensions, very fast
  phi4-mini: 2.5GB, for title generation

Cloud (OpenRouter):
  Minimax M2.1: Fallback when Ollama unavailable
""", classes="help-text"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="help",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
