import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Kommit Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


def ask(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()


# ---------- Request models ----------

class CommitRequest(BaseModel):
    diff: str

class ReadmeRequest(BaseModel):
    structure: str
    snippets: str
    project_name: str

class DocsRequest(BaseModel):
    items: str
    project_name: str


# ---------- Routes ----------

@app.get("/")
def root():
    return {"status": "Kommit backend running"}


@app.post("/commit")
def generate_commit(req: CommitRequest):
    if not req.diff.strip():
        raise HTTPException(400, "Empty diff")

    prompt = f"""You are an expert developer. Given the following git diff, generate exactly 3 concise, meaningful commit messages.

Rules:
- Use conventional commit format (feat:, fix:, refactor:, chore:, docs:, etc.)
- Each message should be on its own numbered line (1. 2. 3.)
- Max 72 characters each
- Be specific, not generic
- No explanation, just the 3 messages

Git diff:
{req.diff[:6000]}
"""
    result = ask(prompt)
    return {"result": result}


@app.post("/readme")
def generate_readme(req: ReadmeRequest):
    prompt = f"""You are a technical writer. Generate a clean, professional README.md for a project called "{req.project_name}".

Project structure:
{req.structure[:2000]}

Key code snippets:
{req.snippets[:5000]}

Include these sections:
- Project name and a one-line description
- Features (bullet points)
- Installation
- Usage with examples
- Configuration (if relevant)
- Contributing
- License (MIT)

Use proper markdown. Make it look great on GitHub. Do not add any preamble, output only the README content.
"""
    result = ask(prompt)
    return {"result": result}


@app.post("/docs")
def generate_docs(req: DocsRequest):
    prompt = f"""You are a technical writer. Generate clean markdown documentation for the following Python functions and classes from the project "{req.project_name}".

Functions and classes:
{req.items[:6000]}

For each item write:
- A heading with the function/class name
- A short description of what it does
- Parameters (if any can be inferred from the signature)
- Returns (if relevant)

Output only the markdown documentation, no preamble.
"""
    result = ask(prompt)
    return {"result": result}
