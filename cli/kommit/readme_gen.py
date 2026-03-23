import os
import sys
import typer
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel
from kommit.api import call

console = Console()

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".nuxt"}
IGNORE_EXTS = {".pyc", ".pyo", ".lock", ".log", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".ttf"}
CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c", ".cpp", ".cs", ".rb", ".php", ".swift"}


def scan_project(root: str) -> dict:
    """Scan project directory and return structure + key file contents."""
    structure = []
    snippets = []
    total_chars = 0
    max_chars = 8000  # Keep context manageable

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter ignored dirs in place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        rel = os.path.relpath(dirpath, root)
        indent = "  " * (rel.count(os.sep) if rel != "." else 0)
        folder = os.path.basename(dirpath) if rel != "." else os.path.basename(root)
        structure.append(f"{indent}{folder}/")

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in IGNORE_EXTS:
                continue
            file_indent = indent + "  "
            structure.append(f"{file_indent}{fname}")

            # Read key files for context
            if ext in CODE_EXTS and total_chars < max_chars:
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2000)
                    snippets.append(f"--- {os.path.relpath(fpath, root)} ---\n{content}")
                    total_chars += len(content)
                except Exception:
                    pass

    return {
        "structure": "\n".join(structure),
        "snippets": "\n\n".join(snippets)
    }


def run(
    path: str = typer.Argument(".", help="Path to project root (default: current directory)"),
    output: str = typer.Option("README.md", "--output", "-o", help="Output file name"),
    overwrite: bool = typer.Option(False, "--overwrite", "-y", help="Overwrite existing README without asking"),
):
    """Scan your project and generate a README.md using AI."""
    root = os.path.abspath(path)

    if not os.path.isdir(root):
        rprint(f"[red]Directory not found: {root}[/red]")
        raise typer.Exit()

    out_path = os.path.join(root, output)
    if os.path.exists(out_path) and not overwrite:
        confirm = typer.confirm(f"{output} already exists. Overwrite?")
        if not confirm:
            rprint("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

    with console.status("[bold cyan]Scanning project...[/bold cyan]"):
        project = scan_project(root)

    with console.status("[bold cyan]Generating README...[/bold cyan]"):
        result = call("readme", {
            "structure": project["structure"],
            "snippets": project["snippets"],
            "project_name": os.path.basename(root)
        })

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)

    console.print()
    console.print(Panel(f"[bold green]✔ README saved to {output}[/bold green]", style="green"))
