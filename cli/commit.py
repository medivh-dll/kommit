import subprocess
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from kommit.api import call

console = Console()


def get_diff() -> str:
    """Get staged git diff."""
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        rprint("[red]Not a git repository or git not installed.[/red]")
        sys.exit(1)
    return result.stdout.strip()


def do_commit(message: str):
    """Run git commit with the given message."""
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        rprint(f"[green]✔ Committed:[/green] {message}")
    else:
        rprint(f"[red]Commit failed:[/red] {result.stderr}")


def run():
    """Generate AI commit messages from your staged diff and pick one."""
    diff = get_diff()

    if not diff:
        rprint("[yellow]No staged changes found. Use `git add` first.[/yellow]")
        raise typer.Exit()

    with console.status("[bold cyan]Generating commit messages...[/bold cyan]"):
        raw = call("commit", {"diff": diff})

    # Parse numbered list from response
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    options = []
    for line in lines:
        # Strip leading numbers like "1." "1)" etc
        for prefix in ["1.", "2.", "3.", "1)", "2)", "3)"]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
        if line:
            options.append(line)

    if not options:
        rprint("[red]Could not parse commit messages. Try again.[/red]")
        raise typer.Exit()

    # Display options
    console.print()
    console.print(Panel("[bold]Pick a commit message[/bold]", style="cyan"))
    for i, opt in enumerate(options[:3], 1):
        console.print(f"  [bold cyan]{i}.[/bold cyan] {opt}")
    console.print(f"  [bold cyan]4.[/bold cyan] [dim]Write my own[/dim]")
    console.print(f"  [bold cyan]5.[/bold cyan] [dim]Cancel[/dim]")
    console.print()

    choice = typer.prompt("Choose", default="1")

    if choice == "5":
        rprint("[yellow]Cancelled.[/yellow]")
        raise typer.Exit()
    elif choice == "4":
        custom = typer.prompt("Your commit message")
        do_commit(custom)
    elif choice in ["1", "2", "3"]:
        idx = int(choice) - 1
        if idx < len(options):
            do_commit(options[idx])
        else:
            rprint("[red]Invalid choice.[/red]")
    else:
        rprint("[red]Invalid choice.[/red]")
