# Contributing to Kommit

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/yourusername/kommit
cd kommit/cli
pip install -e ".[dev]"
```

## Project Structure

```
cli/kommit/
├── main.py       # CLI entry point and command registration
├── api.py        # Backend API client (swap API here if needed)
├── commit.py     # kommit commit command
├── readme_gen.py # kommit readme command
├── docs_gen.py   # kommit docs command
└── tree.py       # kommit tree command
```

## Adding a New Command

1. Create a new file in `cli/kommit/`
2. Define a `run()` function with Typer decorators
3. Register it in `main.py` with `app.command("name")(yourmodule.run)`
4. Add a corresponding route in `backend/main.py`

## Backend

The backend is a FastAPI app. To run it locally:

```bash
cd backend
pip install -r requirements.txt
GEMINI_API_KEY=your_key uvicorn main:app --reload
```

Then point the CLI at it by changing `BACKEND_URL` in `cli/kommit/api.py` to `http://localhost:8000`.

## Pull Requests

- Keep PRs focused on one thing
- Add a clear description of what changed and why
- Make sure the CLI still works end to end before submitting
