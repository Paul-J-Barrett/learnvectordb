"""Flashcard TUI application using Textual."""

import asyncio
import csv
import random
import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Static, Label, Log
from textual.screen import Screen
from textual.events import Key


sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class FlashcardScreen(Screen):
    """Flashcard quiz screen."""
    
    def __init__(self, flashcards: list[tuple[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.flashcards = flashcards
        self.current_index = 0
        self.show_answer = False
        self.score = 0
        self.total_shown = 0
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("━━━ VECTOR DATABASE FLASHCARDS ━━━", classes="header"),
            Static("", id="progress", classes="progress"),
            Static("Question will appear here...", id="question", classes="question"),
            Button("Show Answer", id="show_answer", variant="primary", classes="action-btn"),
            Static("Answer will appear here...", id="answer", classes="answer hidden"),
            Container(
                Button("Incorrect", id="wrong", variant="warning", classes="grade-btn"),
                Button("Correct", id="right", variant="success", classes="grade-btn"),
                id="grade_buttons",
                classes="grade-row hidden",
            ),
            Vertical(
                Button("Next Card", id="next", classes="nav-btn"),
                Button("Shuffle", id="shuffle", classes="nav-btn"),
                Button("Random Card", id="random", classes="nav-btn"),
                Button("Exit", id="exit", classes="nav-btn"),
                classes="nav-row",
            ),
            classes="flashcard-screen",
        )
    
    def on_mount(self) -> None:
        self.update_card()
    
    def update_card(self) -> None:
        if not self.flashcards:
            self.query_one("#question", Static).update("No flashcards loaded!")
            return
        
        if self.current_index >= len(self.flashcards):
            self.current_index = 0
        
        question, answer = self.flashcards[self.current_index]
        
        self.query_one("#question", Static).update(f"Q: {question}")
        self.query_one("#answer", Static).update(f"A: {answer}")
        self.query_one("#progress", Static).update(
            f"Card {self.current_index + 1}/{len(self.flashcards)} | Score: {self.score}/{self.total_shown}"
        )
        
        self.show_answer = False
        self.query_one("#answer", Static).add_class("hidden")
        self.query_one("#show_answer", Button).remove_class("hidden")
        self.query_one("#grade_buttons", Container).add_class("hidden")
        self.query_one("#show_answer", Button).label = "Show Answer"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        
        if button_id == "show_answer":
            self.show_answer = True
            self.query_one("#answer", Static).remove_class("hidden")
            self.query_one("#show_answer", Button).add_class("hidden")
            self.query_one("#grade_buttons", Container).remove_class("hidden")
        
        elif button_id == "right":
            self.score += 1
            self.total_shown += 1
            self.current_index = (self.current_index + 1) % len(self.flashcards)
            self.update_card()
        
        elif button_id == "wrong":
            self.total_shown += 1
            self.current_index = (self.current_index + 1) % len(self.flashcards)
            self.update_card()
        
        elif button_id == "next":
            self.current_index = (self.current_index + 1) % len(self.flashcards)
            self.update_card()
        
        elif button_id == "shuffle":
            random.shuffle(self.flashcards)
            self.current_index = 0
            self.update_card()
        
        elif button_id == "random":
            self.current_index = random.randint(0, len(self.flashcards) - 1)
            self.update_card()
        
        elif button_id == "exit":
            self.app.pop_screen()
    
    def on_key(self, event: Key) -> None:
        if event.key == "space":
            if self.show_answer:
                self.score += 1
                self.total_shown += 1
                self.current_index = (self.current_index + 1) % len(self.flashcards)
                self.update_card()
            else:
                self.show_answer = True
                self.query_one("#answer", Static).remove_class("hidden")
                self.query_one("#show_answer", Button).add_class("hidden")
                self.query_one("#grade_buttons", Container).remove_class("hidden")
        
        elif event.key == "r":
            self.current_index = random.randint(0, len(self.flashcards) - 1)
            self.update_card()
        
        elif event.key == "s":
            random.shuffle(self.flashcards)
            self.current_index = 0
            self.update_card()
        
        elif event.key == "escape":
            self.app.pop_screen()


class FlashcardApp(App):
    """Main flashcard application."""
    
    CSS = """
    FlashcardScreen {
        background: #1e1e2e;
    }
    
    .header {
        text-align: center;
        color: #89b4fa;
        font-size: 18;
        font-weight: bold;
        margin-bottom: 1;
    }
    
    .progress {
        text-align: center;
        color: #6c7086;
        font-size: 12;
        margin-bottom: 2;
    }
    
    .question {
        background: #313244;
        border: solid #89b4fa;
        padding: 2;
        margin: 1;
        color: #cdd6f4;
        font-size: 14;
        height: auto;
        max-height: 10;
        overflow-y: auto;
    }
    
    .answer {
        background: #1e1e2e;
        border: solid #a6e3a1;
        padding: 2;
        margin: 1;
        color: #a6e3a1;
        font-size: 13;
        height: auto;
        max-height: 10;
        overflow-y: auto;
    }
    
    .answer.hidden {
        display: none;
    }
    
    .action-btn {
        width: 100%;
        margin: 1 0;
    }
    
    .grade-row {
        margin: 1 0;
    }
    
    .grade-btn {
        width: 48%;
        margin: 0 1%;
    }
    
    .nav-row {
        margin-top: 2;
        align: center middle;
    }
    
    .nav-btn {
        width: 22%;
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]
    
    def on_mount(self) -> None:
        pass


def run_flashcards(csv_path: str = None):
    """Run the flashcard application."""
    if csv_path is None:
        csv_path = Path(__file__).parent.parent.parent / "data" / "flashcards.csv"
    
    if not Path(csv_path).exists():
        print(f"Error: Flashcards file not found at {csv_path}")
        print("Run 'python -m vectordb_learn.flashcards.generator' first to generate flashcards.")
        sys.exit(1)
    
    flashcards = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flashcards.append((row.get('question', ''), row.get('answer', '')))
    
    if not flashcards:
        print("Error: No flashcards found in CSV file.")
        sys.exit(1)
    
    print(f"Loaded {len(flashcards)} flashcards.")
    print("Keyboard shortcuts: Space=Show Answer, R=Random, S=Shuffle, Escape=Exit")
    print("Starting TUI...")
    
    class MainApp(App):
        def on_mount(self) -> None:
            self.push_screen(FlashcardScreen(flashcards))
    
    app = MainApp()
    asyncio.run(app.run_async())


if __name__ == "__main__":
    run_flashcards()