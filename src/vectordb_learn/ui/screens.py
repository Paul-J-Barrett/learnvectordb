"""Textual screens for the vector database learner."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Static, Label, Log


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
            self.app.push_screen("IngestScreen()")
        elif button_id == "search":
            self.app.push_screen("SearchScreen()")
        elif button_id == "explain":
            self.app.push_screen("ExplainScreen()")
        elif button_id == "indexes":
            self.app.push_screen("IndexScreen()")
        elif button_id == "playground":
            self.app.push_screen("PlaygroundScreen()")
        elif button_id == "metrics":
            self.app.push_screen("MetricsScreen()")
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


class ExplainScreen(Screen):
    """Query explanation screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ EXPLAIN QUERY ━━━", classes="section-title"),
            Static("View the actual SQL and execution plan for vector searches.", classes="info"),
            Horizontal(
                Button("Explain Cosine", id="explain_cosine", variant="info"),
                Button("Explain L2", id="explain_l2", variant="info"),
                Button("Explain Inner", id="explain_inner", variant="info"),
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
                classes="btn-row",
            ),
            Static("━ Current Indexes ━", classes="section-title"),
            Static("Index information will appear here...", id="index_info", classes="info-area"),
            Horizontal(
                Button("← Back", id="back", variant="default"),
                classes="nav-row",
            ),
            id="indexes",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


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
