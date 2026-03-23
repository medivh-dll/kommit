import os
import ast
import typer
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel
from kommit.api import call

console = Console()

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def extract_python_signatures(filepath: str) -> list[dict]:
    """Extract function and class signatures with existing docstrings from a Python file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception:
        return []

    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            docstring = ast.get_docstring(node) or ""
            # Get source lines for the signature
            try:
                lines = source.splitlines()
                sig_line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            except Exception:
                sig_line = name
            items.append({
                "name": name,
                "signature": sig_line.strip(),
                "existing_doc": docstring,
                "type": "class" if isinstance(node, ast.ClassDef) else "function"
            })
    return items


def scan_for_docs(root: str) -> list[dict]:
    """Scan all Python files and collect items needing documentation."""
    all_items = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            items = extract_python_signatures(fpath)
            for item in items:
                item["file"] = rel
            all_items.extend(items)
    return all_items


def run(
    path: str = typer.Argument(".", help="Path to project root (default: current directory)"),
    output: str = typer.Option("DOCS.md", "--output", "-o", help="Output file name"),
    overwrite: bool = typer.Option(False, "--overwrite", "-y", help="Overwrite existing file without asking"),
):
    """Scan your Python project and generate documentation from functions and classes."""
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

    with console.status("[bold cyan]Scanning for functions and classes...[/bold cyan]"):
        items = scan_for_docs(root)

    if not items:
        rprint("[yellow]No Python functions or classes found.[/yellow]")
        raise typer.Exit()

    rprint(f"[cyan]Found {len(items)} functions/classes across your project.[/cyan]")

    # Format for API
    formatted = "\n".join([
        f"[{item['file']}] {item['type'].upper()}: {item['signature']}"
        + (f"\n  existing doc: {item['existing_doc']}" if item['existing_doc'] else "")
        for item in items[:60]  # Cap at 60 to stay within token limits
    ])

    with console.status("[bold cyan]Generating documentation...[/bold cyan]"):
        result = call("docs", {
            "items": formatted,
            "project_name": os.path.basename(root)
        })

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)

    console.print()
    console.print(Panel(f"[bold green]✔ Docs saved to {output}[/bold green]", style="green"))
