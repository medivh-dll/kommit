import typer
from kommit import commit, readme_gen, docs_gen, tree

app = typer.Typer(
    name="kommit",
    help="🚀 AI-powered developer toolkit — commit messages, READMEs, docs, and branch trees.",
    add_completion=False,
)

app.command("commit")(commit.run)
app.command("readme")(readme_gen.run)
app.command("docs")(docs_gen.run)
app.command("tree")(tree.run)

if __name__ == "__main__":
    app()
