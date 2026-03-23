# Kommit 🚀

> AI-powered developer toolkit — commit messages, READMEs, docs, and branch trees.

[![PyPI](https://img.shields.io/pypi/v/kommit)](https://pypi.org/project/kommit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What is Kommit?

Kommit is a CLI tool that uses AI to handle the boring parts of being a developer.

| Command | What it does |
|---|---|
| `kommit commit` | Reads your staged diff, suggests 3 commit messages, you pick one |
| `kommit readme` | Scans your project, generates a full README.md |
| `kommit docs` | Reads your functions and classes, generates DOCS.md |
| `kommit tree` | Beautiful git branch history visualizer in your terminal |

## Install

```bash
pip install kommit
```

## Quick Start

```bash
# Generate a commit message
git add .
kommit commit

# Generate a README for your project
cd your-project
kommit readme

# Visualize your branches
kommit tree
```

## Repo Structure

```
kommit/
├── cli/        # Python CLI package (published to PyPI)
├── backend/    # FastAPI backend (deployed on Render)
└── web/        # Web app (coming soon)
```

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

## License

MIT
