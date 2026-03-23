import httpx
import sys

BACKEND_URL = "https://kommit-backend.onrender.com"  # Update after Render deploy

def call(endpoint: str, payload: dict) -> str:
    """Send a request to the Kommit backend and return the text response."""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/{endpoint}",
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result", "")
    except httpx.ConnectError:
        print("[red]Could not connect to Kommit backend. Is it running?[/red]")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"[red]Backend error: {e.response.status_code}[/red]")
        sys.exit(1)
    except Exception as e:
        print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
