# Python TUI Framework Research for Learning Tool

## Overview of Popular TUI Frameworks

Based on research, here are the top Python TUI frameworks ranked by popularity and suitability for your learning tool project:

### 1. Textual (33.9k GitHub Stars) - RECOMMENDED FOR YOUR USE CASE

**Overview**: Modern, rapid application development framework for Python terminal apps. Can also run in web browsers.

**Pros**:
- **Modern Python API**: Clean, Pythonic interface with async support
- **Rich widget library**: Built-in widgets for menus, forms, data tables, buttons, inputs
- **Web deployment**: Can serve apps in browser - great for sharing demos
- **CSS styling**: Declarative styling similar to web development
- **Active development**: Frequent updates, large community (Textualize company)
- **Excellent documentation**: Comprehensive tutorials and API docs
- **Debugging tools**: Built-in dev console for debugging terminal apps

**Cons**:
- **Newer framework**: Less mature than urwid/prompt-toolkit
- **Learning curve**: More concepts to learn (DOM, CSS, workers)
- **Dependency size**: Larger footprint than lightweight alternatives

**Basic Usage Pattern**:
```python
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static

class LearningToolApp(App):
    CSS = """
    Screen { align: center middle; }
    Button { margin: 1; }
    Input { width: 40; }
    """
    
    def compose(self) -> ComposeResult:
        yield Static("Vector Database Learning Tool", classes="header")
        yield Input(placeholder="Enter CSV file path...", id="csv_path")
        yield Button("Load Data", id="load_btn")
        yield Button("Search", id="search_btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_btn":
            self.load_csv()
        elif event.button.id == "search_btn":
            self.search_vectors()
    
    def load_csv(self):
        csv_path = self.query_one("#csv_path", Input).value
        # Database integration here
        pass

if __name__ == "__main__":
    app = LearningToolApp()
    app.run()
```

**Integration with Databases**: Works well with any Python database library (psycopg2, asyncpg, sqlalchemy). Example integration:
```python
# Using async with psycopg2 or asyncpg
import asyncpg
from textual.app import App

class VectorDBApp(App):
    async def connect_db(self):
        self.conn = await asyncpg.connect('postgresql://user:pass@localhost/db')
    
    async def search_vectors(self, query: list):
        results = await self.conn.fetch(
            "SELECT * FROM embeddings ORDER BY embedding <-> $1 LIMIT 10",
            query
        )
        return results
```

---

### 2. Rich (55.3k GitHub Stars) - EXCELLENT FOR FORMATTING

**Overview**: Rich text and beautiful formatting library for terminal output.

**Pros**:
- **Beautiful output**: Excellent for tables, progress bars, syntax highlighting
- **Easy to use**: Simple API for colored/formatted output
- **Large ecosystem**: Used by 475k+ projects
- **Compatible**: Works alongside other TUI frameworks

**Cons**:
- **Not a full TUI framework**: Limited interactive capabilities
- **No widgets**: No built-in menus, forms, or interactive elements

**Basic Usage**:
```python
from rich import print
from rich.table import Table
from rich.console import Console

console = Console()

# Display search results as formatted table
table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID")
table.add_column("Content")
table.add_column("Similarity")

for result in search_results:
    table.add_row(result.id, result.content, f"{result.similarity:.3f}")

console.print(table)
```

**Best Use**: Combined with other frameworks for beautiful output, or for simple scripts.

---

### 3. Prompt Toolkit (10.2k GitHub Stars) - EXCELLENT FOR INTERACTIVE CLI

**Overview**: Library for building powerful interactive command line applications.

**Pros**:
- **Interactive excellence**: Best-in-class for prompts, completions, editing
- **Feature-rich**: Syntax highlighting, auto-completion, multi-line editing
- **Vi/Emacs bindings**: Familiar key bindings for power users
- **Mature**: Stable, well-tested over many years

**Cons**:
- **Less visual**: More text-based than visual TUI
- **Application structure**: Requires more boilerplate for complex apps

**Basic Usage**:
```python
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog
from prompt_toolkit.styles import Style

def main():
    # File selection
    result = input_dialog(
        title='Vector Search Tool',
        text='Enter CSV file path:',
    ).run()
    
    # Menu selection
    choices = [
        ("load", "Load CSV Data"),
        ("search", "Search Vectors"),
        ("debug", "Debug Mode")
    ]
    
    choice = radiolist_dialog(
        title='Main Menu',
        text='Select an action:',
        values=choices
    ).run()
```

---

### 4. Urwid (3k GitHub Stars) - MATURE TUI LIBRARY

**Overview**: Console user interface library for Python with mature widget set.

**Pros**:
- **Mature and stable**: 15+ years of development
- **Event loop support**: Twisted, asyncio, tornado integration
- **Complete widget set**: Buttons, forms, lists, tables
- **Good documentation**: Extensive examples and docs

**Cons**:
- **Older API**: Less Pythonic than newer frameworks
- **Verbose**: More boilerplate required
- **Windows support**: Limited to Windows 10+

**Basic Usage**:
```python
import urwid

def main():
    # Create interface
    palette = [
        ('header', 'bold', 'dark blue'),
        ('button', 'black', 'light gray'),
    ]
    
    # Build interface
    header = urwid.Text("Vector Database Learning Tool", align='center')
    csv_input = urwid.Edit("CSV File: ")
    load_btn = urwid.Button("Load Data")
    search_btn = urwid.Button("Search")
    
    pile = urwid.Pile([header, csv_input, load_btn, search_btn])
    top = urwid.Filler(pile, top=2)
    
    # Run application
    urwid.MainLoop(top, palette).run()
```

---

### 5. Blessed (1.4k GitHub Stars) - SIMPLE TERMINAL CAPABILITIES

**Overview**: Easy, practical library for terminal apps focusing on colors, positioning, and keyboard input.

**Pros**:
- **Easy to learn**: Simple API for basic terminal operations
- **Cross-platform**: Works on Windows, Mac, Linux
- **No curses complexity**: Cleaner than raw curses

**Cons**:
- **Limited widgets**: No built-in menu/form components
- **Lower level**: More work to build interactive UI

---

## Analysis for Your Specific Use Case

### Your Requirements:
1. **CSV ingestion functionality**
2. **Vector search functionality**  
3. **Educational/debugging features**
4. **PostgreSQL/pgvector integration**
5. **Interactive menus and forms**
6. **Ease of use for learning/demo**

### Framework Comparison Matrix

| Feature | Textual | Prompt Toolkit | Urwid | Rich + Custom |
|---------|---------|----------------|-------|---------------|
| **Interactive Forms** | Excellent | Good | Good | Limited |
| **Menus/Navigation** | Excellent | Good | Good | Manual |
| **Database Integration** | Excellent | Good | Good | Good |
| **Learning Curve** | Medium | Medium | Medium | Low |
| **Demo-Ready UI** | Excellent | Good | Fair | Limited |
| **Educational Features** | Excellent | Good | Fair | Good |
| **Community Support** | Excellent | Good | Good | Excellent |
| **Documentation** | Excellent | Good | Good | Excellent |

---

## RECOMMENDATION: Textual for Your Use Case

### Why Textual is Best for Your Learning Tool:

1. **Built for Rapid Development**: Quick to prototype and iterate
2. **Beautiful UI Out of Box**: Modern look with minimal effort
3. **Widget Rich**: Buttons, inputs, lists, tables, data grids ready to use
4. **Educational Features**: Built-in dev console, easy debugging, clean code structure
5. **Database Friendly**: Async support works well with database operations
6. **Demo Ready**: Impressive visual appearance for presentations
7. **Future-Proof**: Active development by Textualize company (same creators as Rich)

### Alternative: Textual + Rich Combo

For the best of both worlds:
```python
# Main application using Textual
from textual.app import App
from textual.widgets import RichLog

# Beautiful output using Rich
from rich.table import Table
from rich.console import Console

class VectorSearchApp(App):
    """Learning tool using Textual + Rich"""
    
    def compose(self):
        yield from [
            # Textual widgets for interaction
            Input(id="query", placeholder="Enter search query..."),
            Button("Search", id="search_btn"),
            Button("Load CSV", id="load_btn"),
            # RichLog for displaying formatted results
            RichLog(id="results", highlight=True)
        ]
    
    def on_button_pressed(self, event):
        if event.button.id == "search_btn":
            self.perform_search()
        elif event.button.id == "load_btn":
            self.load_csv()
    
    def display_results(self, results):
        """Use Rich for beautiful table display"""
        console = Console()
        table = Table(title="Vector Search Results")
        table.add_column("ID", style="dim")
        table.add_column("Content")
        table.add_column("Distance", justify="right")
        
        for result in results:
            table.add_row(result.id, result.text, f"{result.distance:.4f}")
        
        # Display in RichLog widget
        log = self.query_one("#results", RichLog)
        log.write(table)
```

### PostgreSQL/pgvector Integration Example

```python
import asyncpg
from textual.app import App

class VectorDBApp(App):
    async def setup_database(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            host='localhost',
            port=5432,
            user='postgres',
            database='vectordb',
            min_size=2,
            max_size=10
        )
    
    async def load_csv_to_db(self, csv_path: str):
        """Load CSV data into PostgreSQL with pgvector"""
        async with self.pool.acquire() as conn:
            # Example: Load and create embeddings
            await conn.executemany("""
                INSERT INTO documents (content, embedding) 
                VALUES ($1, $2)
            """, self.process_csv(csv_path))
    
    async def search_vectors(self, query: str):
        """Perform vector search"""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT content, embedding <-> $1 as distance
                FROM documents
                ORDER BY distance
                LIMIT 10
            """, query)
            return results
```

### Educational/Debugging Features

Textual excels for educational purposes:
```python
# Easy debugging with dev console
from textual.devtools import DevtoolsServer

class LearningToolApp(App):
    def on_mount(self) -> None:
        # Enable dev console automatically
        self.run_devtools()
    
    def log_state(self, message: str):
        """Educational: show internal state"""
        self.log(f"[DEBUG] {message}")
        self.notify(message, severity="information")

# Add educational tooltips
class Tooltip(Static):
    """Educational hints for users"""
    def __init__(self, text: str):
        super().__init__(text)
        self.styles.background = "dark blue"
        self.styles.color = "white"
```

---

## Final Recommendations

### For Your Specific Use Case:

**Primary Choice**: **Textual**
- Best balance of ease of use and features
- Modern, Pythonic API
- Excellent for demos and learning tools
- Strong database integration capabilities

**Secondary Choice**: **Prompt Toolkit** 
- If you need simpler CLI interactions
- Better for command-line focused tools
- Excellent auto-completion features

**Combination Approach**: **Textual + Rich**
- Use Textual for application structure and widgets
- Use Rich for beautiful table/data display
- Best of both worlds

---

## Resources

- **Textual Documentation:** https://textual.textualize.io/
- **Textual GitHub:** https://github.com/textualize/textual
- **Rich Documentation:** https://rich.readthedocs.io/
- **Prompt Toolkit:** https://python-prompt-toolkit.readthedocs.io/
- **Urwid:** https://urwid.org/
