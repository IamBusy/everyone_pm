from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from eopm.core.stage_manager import StageManager, Stage

console = Console()


def print_markdown(text: str) -> None:
    console.print(Markdown(text))


def print_stage_header(stage_manager: StageManager) -> None:
    """Print the current stage header with progress indicator."""
    stage = stage_manager.current_stage

    # Stage emoji and color mapping
    stage_info = {
        Stage.DISCOVERY: ("📋", "blue", "Discovery: Understand the Problem"),
        Stage.DEFINITION: ("🎯", "cyan", "Definition: Define the Solution"),
        Stage.IDEATION: ("💡", "yellow", "Ideation: Explore Technical Options"),
        Stage.DELIVERY: ("🚀", "green", "Delivery: Create Specifications"),
        Stage.COMPLETE: ("✅", "bright_green", "Complete: Ready for Development"),
    }

    emoji, _, description = stage_info.get(stage, ("", "", stage.value))

    # Create progress bar
    stage_order = [Stage.DISCOVERY, Stage.DEFINITION, Stage.IDEATION, Stage.DELIVERY]
    current_idx = stage_order.index(stage) if stage in stage_order else len(stage_order)

    progress_text = ""
    for i, s in enumerate(stage_order):
        if i < current_idx:
            progress_text += "[green]✓[/green] "
        elif i == current_idx:
            progress_text += "[blue]→[/blue] "
        else:
            progress_text += "○ "

    # Build the panel
    grid = Table.grid(padding=(0, 1))
    grid.add_column(justify="left")

    title = Text(f"{emoji} Stage: {stage.upper()}", style="bold")
    grid.add_row(title)
    grid.add_row(Text(description, style="dim"))
    grid.add_row("")
    grid.add_row(Text("Progress:", style="bold"))
    grid.add_row(progress_text)

    console.print(Panel(grid, padding=(0, 1), border_style="blue"))
    console.print("")


def print_welcome(session_path: Path, messages: list[dict], stage_manager: StageManager, version: str = "0.1.0") -> None:
    title = Text("EveryonePM", style="bold")
    subtitle = Text(f"Interactive PRD + Tech Spec assistant | Double Diamond Workflow | v{version}", style="dim")

    grid = Table.grid(padding=(0, 1))
    grid.add_column(justify="left")

    grid.add_row(title)
    grid.add_row(subtitle)
    grid.add_row("")

    cmds = Table.grid(padding=(0, 2))
    cmds.add_column(style="bold")
    cmds.add_column(style="dim")
    cmds.add_row("/export <dir>", "Export PRD.md + TECH_SPEC.md")
    cmds.add_row("/status", "Show current stage and progress")
    cmds.add_row("/next", "Advance to next stage (when ready)")
    cmds.add_row("/goto <stage>", "Jump to stage (debug only)")
    cmds.add_row("/read <path>", "Read file and ask AI to analyze")
    cmds.add_row("/write <kind> <path>", "Generate PRD/TechSpec to file")
    cmds.add_row("confirm", "Confirm current stage artifacts")
    cmds.add_row("/fresh", "Reset session and start over")
    cmds.add_row("exit | quit | /exit", "Leave the session")

    grid.add_row(Text("Quick commands", style="bold"))
    grid.add_row(cmds)
    grid.add_row("")

    # Session info
    if session_path.exists():
        status_text = Text(f"Resumed {len(messages)} messages from {session_path}", style="green")
    else:
        status_text = Text(f"No existing session at {session_path}", style="yellow")

    grid.add_row(Text("Session", style="bold"))
    grid.add_row(status_text)
    grid.add_row("")

    # Stage info
    stage = stage_manager.current_stage
    stage_text = Text(f"Current Stage: {stage.value.upper()}", style="blue bold")
    grid.add_row(Text("Workflow", style="bold"))
    grid.add_row(stage_text)
    grid.add_row("")

    grid.add_row(Text("Type your first prompt to begin.", style="bold"))

    console.print(Panel(grid, padding=(1, 2)))


@contextmanager
def status(message: str = "Thinking..."):
    """Show a status spinner with the given message."""
    with console.status(message):
        yield


def show_progress_stages() -> None:
    """Display progress stages to give user feedback during long operations."""
    stages = [
        "[dim]●[/dim] Connecting to API...",
        "[dim]●[/dim] Sending request...",
        "[dim]●[/dim] AI is thinking...",
        "[dim]●[/dim] Processing response...",
    ]
    for stage in stages:
        console.print(stage)


class ProgressSpinner:
    """A progress spinner that shows different stages of processing."""

    def __init__(self, stages: list[str] | None = None):
        self.stages = stages or [
            "Connecting to API...",
            "Sending request...",
            "AI is thinking...",
            "Processing response...",
        ]
        self.current_stage = 0
        self._status = None

    def start(self) -> None:
        """Start the progress spinner."""
        self._status = console.status(self.stages[0])
        self._status.__enter__()

    def next_stage(self) -> None:
        """Move to the next stage."""
        if self._status and self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self._status.update(self.stages[self.current_stage])

    def stop(self) -> None:
        """Stop the progress spinner."""
        if self._status:
            self._status.__exit__(None, None, None)
            self._status = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red]{message}[/red]")


def print_version(version: str) -> None:
    """Print the version information."""
    console.print(f"EveryonePM v{version}")
