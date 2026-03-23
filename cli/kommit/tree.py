import subprocess
import sys
import typer
from rich.console import Console
from rich.tree import Tree
from rich import print as rprint
from rich.text import Text

console = Console()


def get_branches() -> list[str]:
    result = subprocess.run(
        ["git", "branch", "-a"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        rprint("[red]Not a git repository or git not installed.[/red]")
        sys.exit(1)
    branches = []
    for line in result.stdout.splitlines():
        b = line.strip().lstrip("* ").strip()
        if b and "->" not in b:
            branches.append(b)
    return branches


def get_log(branch: str, limit: int) -> list[dict]:
    result = subprocess.run(
        ["git", "log", branch, f"--max-count={limit}",
         "--pretty=format:%h|%s|%an|%ar", "--no-walk=unsorted"],
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "message": parts[1],
                "author": parts[2],
                "when": parts[3]
            })
    return commits


def get_current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def run(
    limit: int = typer.Option(5, "--limit", "-n", help="Commits to show per branch"),
    all_branches: bool = typer.Option(False, "--all", "-a", help="Show all branches including remotes"),
):
    """Visualize your git branch history in a clean tree view."""
    current = get_current_branch()
    branches = get_branches()

    if not all_branches:
        branches = [b for b in branches if not b.startswith("remotes/")]

    if not branches:
        rprint("[yellow]No branches found.[/yellow]")
        raise typer.Exit()

    console.print()
    root_tree = Tree(
        f"[bold cyan]📁 Git History[/bold cyan] [dim]({len(branches)} branch{'es' if len(branches) != 1 else ''})[/dim]"
    )

    for branch in branches:
        is_current = branch == current
        branch_label = Text()
        if is_current:
            branch_label.append("● ", style="bold green")
            branch_label.append(branch, style="bold green")
            branch_label.append(" (current)", style="dim green")
        else:
            branch_label.append("○ ", style="cyan")
            branch_label.append(branch, style="cyan")

        branch_node = root_tree.add(branch_label)
        commits = get_log(branch, limit)

        if not commits:
            branch_node.add("[dim]No commits[/dim]")
        else:
            for i, c in enumerate(commits):
                is_last = i == len(commits) - 1
                prefix = "└─" if is_last else "├─"
                commit_text = Text()
                commit_text.append(f"{prefix} ", style="dim")
                commit_text.append(c["hash"], style="bold yellow")
                commit_text.append(f" {c['message']}", style="white")
                commit_text.append(f"  {c['author']}", style="dim cyan")
                commit_text.append(f" · {c['when']}", style="dim")
                branch_node.add(commit_text)

    console.print(root_tree)
    console.print()
