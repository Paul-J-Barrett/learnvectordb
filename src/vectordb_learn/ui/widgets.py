"""Custom Textual widgets for the vector database learner."""

from textual.widgets import Static, Button, Input, Log
from textual.containers import Container
from rich.table import Table
from rich.console import Console


class DebugPanel(Static):
    """Panel displaying debug information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.border = ("solid", "green")
        self.styles.padding = (1, 2)

    def update_info(self, info: dict):
        """Update the debug panel with new information."""
        lines = [
            "━━━ DEBUG PANEL ━━━",
            f"Connection Pool: {info.get('pool_status', 'N/A')}",
            f"Last Query Time: {info.get('query_time', 'N/A')}",
            f"Index Type: {info.get('index_type', 'N/A')}",
            f"Embedding Dim: {info.get('embedding_dim', 'N/A')}",
            f"Tracing: {info.get('tracing', 'N/A')}",
            "",
            "━━━ KEYBOARD SHORTCUTS ━━━",
            "F1: Help",
            "F2: Toggle Debug Panel",
            "F3: Toggle SQL View",
            "Ctrl+C: Quit",
        ]
        self.update("\n".join(lines))


class ResultsTable(Static):
    """Table displaying search results."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.border = ("solid", "blue")
        self.styles.padding = (1, 1)

    def display_results(self, results: list[dict], query: str):
        """Display search results in a formatted table."""
        if not results:
            self.update("No results found.")
            return

        console = Console()
        table = Table(title=f"Search Results for: {query[:50]}...")
        table.add_column("Score", justify="right", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Preview", style="dim")

        for row in results:
            similarity = 1 - row.get('distance', 0)
            title = row.get('session_title', 'Untitled')[:30]
            preview = row.get('session_content', '')[:60].replace('\n', ' ')
            table.add_row(f"{similarity:.3f}", title, f"{preview}...")

        with console.capture() as capture:
            console.print(table)

        self.update(capture.get())


class ExplanationPanel(Static):
    """Panel explaining vector concepts."""

    def __init__(self, concept: str = "", **kwargs):
        super().__init__(**kwargs)
        self.styles.border = ("solid", "yellow")
        self.styles.padding = (1, 2)
        self.concepts = {
            "cosine": """━━━ COSINE SIMILARITY ━━━
Measures the angle between two vectors.
• Range: -1 to 1 (pgvector uses 0 to 2 for distance)
• Best for: Comparing document embeddings
• Formula: (A · B) / (||A|| × ||B||)
• Distance operator: <=""",
            "l2": """━━━ EUCLIDEAN (L2) DISTANCE ━━
Measures straight-line distance between points.
• Range: 0 to infinity
• Best for: Geographic data, clustering
• Formula: √Σ(Aᵢ - Bᵢ)²
• Distance operator: <->""",
            "inner": """━━━ INNER PRODUCT ━━━
Measures vector multiplication sum.
• Range: -infinity to +infinity
• Best for: Normalized vectors
• Formula: Σ(Aᵢ × Bᵢ)
• Distance operator: <#>""",
            "hnsw": """━━━ HNSW INDEX ━━━
Hierarchical Navigable Small World
• Fast approximate nearest neighbor search
• Build time: Slower, memory-intensive
• Query time: Very fast
• Recall: High (adjustable with ef_search)
• Parameters: m, ef_construction""",
            "ivfflat": """━━━ IVFFLAT INDEX ━━━
Inverted File Flat
• Clusters vectors into lists
• Build time: Fast
• Query time: Fast
• Recall: Depends on probes
• Parameters: lists, probes""",
        }

    def show_concept(self, concept: str):
        """Show explanation for a concept."""
        self.update(self.concepts.get(concept, f"No explanation for: {concept}"))

    def watch_concept(self, concept: str):
        """Watch for concept changes."""
        self.show_concept(concept)


class SQLView(Static):
    """Panel displaying the raw SQL query."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.border = ("solid", "cyan")
        self.styles.background = "#1e1e1e"
        self.styles.color = "#00ff00"
        self.styles.padding = (1, 2)
        self.font = "monospace"

    def display_query(self, sql: str, params: dict = None):
        """Display the SQL query being executed."""
        display = "━━━ RAW SQL QUERY ━━━\n"
        display += sql
        if params:
            display += "\n\n━━━ PARAMETERS ━━━"
            for k, v in params.items():
                display += f"\n{k}: {v}"
        self.update(display)


class StatusBar(Static):
    """Status bar showing connection and statistics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styles.background = "#333333"
        self.styles.color = "white"
        self.styles.padding = (0, 1)

    def update_status(self, connected: bool, row_count: int = 0, index_type: str = "HNSW"):
        """Update status bar information."""
        status = " ● " if connected else " ○ "
        status += "Connected" if connected else "Disconnected"
        status += f" | Rows: {row_count} | Index: {index_type}"
        self.update(status)
