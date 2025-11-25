"""Minimal FastAPI application serving a Hello World frontend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "templates" / "index.html"

app = FastAPI(title="Hello World App")

# Allow the frontend (and development tools) to reach this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello")
def read_hello() -> dict[str, str]:
    """Serve a simple JSON payload for the frontend to display."""
    return {"message": "Hello World"}


@app.get("/", response_class=HTMLResponse)
def serve_index() -> str:
    """Return the static frontend page."""
    return INDEX_HTML.read_text(encoding="utf-8")


def run() -> None:
    """Launch the FastAPI dev server with reload enabled."""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()