"""Main TUI application for the Vector Database Learner."""

import asyncio
from textual.app import App, ComposeResult
from textual import events
from textual.screen import Screen
from textual.widgets import Static

from .ui.screens import (
    HomeScreen, SearchScreen, IngestScreen, ExplainScreen,
    IndexScreen, PlaygroundScreen, MetricsScreen,
)
from .ui.widgets import DebugPanel, StatusBar
from .db.connection import get_pool, close_pool, test_connection
from .db.operations import get_schema_stats
from .telemetry import setup_telemetry, get_tracer
from .logging import setup_logging


class VectorDBApp(App):
    """Main application class."""

    CSS_PATH = "src/vectordb_learn/ui/styles.css"

    BINDINGS = [
        ("f1", "show_help", "Help"),
        ("f2", "toggle_debug", "Debug"),
        ("f3", "toggle_sql", "SQL View"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    SCREENS = {
        "home": HomeScreen,
        "search": SearchScreen,
        "ingest": IngestScreen,
        "explain": ExplainScreen,
        "indexes": IndexScreen,
        "playground": PlaygroundScreen,
        "metrics": MetricsScreen,
    }

    def __init__(self):
        super().__init__()
        self.debug_visible = False
        self.pool = None
        self.connected = False
        self.row_count = 0

    async def on_mount(self) -> None:
        """Initialize application on startup."""
        setup_logging()
        setup_telemetry()
        
        self.tracer = get_tracer()
        
        with self.tracer.start_as_current_span("app.mount"):
            self.pool = await get_pool()
            self.connected = await test_connection()
            
            if self.connected:
                stats = await get_schema_stats(self.pool)
                self.row_count = stats.get("row_count", 0)
            
            self.push_screen("home")

    async def on_shutdown(self) -> None:
        """Cleanup on shutdown."""
        await close_pool()

    def action_show_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())

    def action_toggle_debug(self) -> None:
        """Toggle debug panel visibility."""
        self.debug_visible = not self.debug_visible
        debug = self.query_one("#debug_panel", DebugPanel)
        debug.display = self.debug_visible

    def action_toggle_sql(self) -> None:
        """Toggle SQL view."""
        pass

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


class HelpScreen(Screen):
    """Help overlay screen."""

    def compose(self) -> ComposeResult:
        yield Static(
            """
            ━━━ KEYBOARD SHORTCUTS ━━━
            
            F1  Show this help
            F2  Toggle debug panel
            F3  Toggle SQL view
            Q   Quit current screen
            Esc Quit current screen
            Ctrl+C  Exit application
            
            ━━━ VECTOR CONCEPTS ━━━
            
            Vector: A list of numbers representing 
            data in N-dimensional space.
            
            Embedding: Converting text/images to 
            vectors using ML models.
            
            pgvector Operators:
              <=>  Cosine distance (most common)
              <->  Euclidean (L2) distance
              <#>  Negative inner product
              <+>  Manhattan distance
            
            ━━━ EMBEDDING MODELS ━━━
            
            Local (Ollama):
              nomic-embed-text: 384 dimensions
              phi4-mini: For title generation
            
            Cloud (OpenRouter):
              Minimax M2.1: Fallback
            """,
            id="help",
        )

    def on_key(self, event: events.Key) -> None:
        if event.key in ("escape", "q", "f1"):
            self.app.pop_screen()


async def run_app():
    """Run the application."""
    app = VectorDBApp()
    try:
        await app.run_async()
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(run_app())
