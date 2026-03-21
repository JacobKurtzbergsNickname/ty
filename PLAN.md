# Plan: Ollama + Image-Gen Integration

## Goal
Provide a simple, composable `app/ai/` module that the rest of the app can call for:
1. **Text generation** via Ollama (local LLM)
2. **Image generation** via a separate image-gen backend (e.g. Stable Diffusion / Automatic1111 REST API)
3. **DB-row metadata generation** — convenience wrappers that take an existing Pydantic schema and return suggested field values

---

## New files

### `app/ai/__init__.py`
Re-exports the public API so callers only need:
```python
from app.ai import generate_text, generate_image, suggest_metadata
```

---

### `app/ai/config.py`
Reads env vars with safe defaults. No side-effects on import.

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API root |
| `OLLAMA_TEXT_MODEL` | `llama3` | Default chat/completion model |
| `IMAGE_GEN_BASE_URL` | `http://localhost:7860` | SD / img-gen API root |
| `IMAGE_GEN_MODEL` | `(empty)` | Optional model hint |
| `AI_TIMEOUT` | `60` | HTTP timeout in seconds |

```python
# app/ai/config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AIConfig:
    ollama_base_url: str
    ollama_text_model: str
    image_gen_base_url: str
    image_gen_model: str
    timeout: int

def load_ai_config() -> AIConfig:
    """Load AI service configuration from environment variables."""
    return AIConfig(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_text_model=os.getenv("OLLAMA_TEXT_MODEL", "llama3"),
        image_gen_base_url=os.getenv("IMAGE_GEN_BASE_URL", "http://localhost:7860"),
        image_gen_model=os.getenv("IMAGE_GEN_MODEL", ""),
        timeout=int(os.getenv("AI_TIMEOUT", "60")),
    )
```

---

### `app/ai/ollama_client.py`
Thin wrapper around Ollama's `/api/generate` and `/api/chat` HTTP endpoints.
Uses the stdlib `urllib.request` (no extra dep) or, preferably, `httpx` if already present.
Since neither is in the current deps, we add `httpx` for clean sync HTTP.

```python
def generate_text(prompt: str, *, model: str | None = None, system: str | None = None) -> str:
    """Send a prompt to Ollama and return the complete text response."""

def generate_text_stream(prompt: str, ...) -> Iterator[str]:
    """Stream tokens from Ollama (for future HTMX SSE use)."""
```

**Error handling:** raises a single `OllamaError(message, status_code)` so callers can catch one type.

---

### `app/ai/image_client.py`
Wrapper around the Stable Diffusion Web UI REST API (`/sdapi/v1/txt2img`).

```python
def generate_image(prompt: str, *, negative_prompt: str = "", width: int = 512, height: int = 512) -> bytes:
    """Generate an image and return raw PNG bytes."""
```

Returns `bytes` so the caller decides how to store or serve it (base64 for inline HTML, file on disk, etc.).

**Error handling:** raises `ImageGenError(message, status_code)`.

---

### `app/ai/metadata.py`
High-level helpers that compose `generate_text` to produce structured suggestions for each DB model.
Returns Pydantic models with `Optional` fields so partial results are safe to use.

```python
class GratitudeSuggestion(BaseModel):
    title: str | None = None
    description: str | None = None

class AffirmationSuggestion(BaseModel):
    text: str | None = None
    author: str | None = None

class QuoteSuggestion(BaseModel):
    text: str | None = None
    author: str | None = None

def suggest_gratitude_metadata(seed: str) -> GratitudeSuggestion:
    """Given a short user seed, ask Ollama to suggest a gratitude title + description."""

def suggest_affirmation(topic: str | None = None) -> AffirmationSuggestion:
    """Ask Ollama to generate an affirmation, optionally on a topic."""

def suggest_quote(topic: str | None = None) -> QuoteSuggestion:
    """Ask Ollama to suggest a positive quote."""
```

Each function builds a structured prompt with a JSON-output instruction, parses the response with `json.loads`, and maps it into the suggestion model.  If parsing fails it returns an empty suggestion (no crash).

---

### `app/ai/exceptions.py`
```python
class AIError(Exception): ...
class OllamaError(AIError): ...
class ImageGenError(AIError): ...
```

---

## Changed files

### `pyproject.toml`
Add `httpx>=0.27` to `[project.dependencies]`.

---

## New test file

### `tests/test_ai.py`
- Monkeypatches `httpx.Client.post` to return canned responses
- Tests `generate_text` happy path and error path
- Tests `suggest_gratitude_metadata` JSON-parse success and graceful degradation on bad JSON

---

## Data flow diagram

```
View (FastHTML route)
  │
  ├─ app.ai.generate_text(prompt)  ──►  ollama_client  ──►  Ollama :11434
  │
  ├─ app.ai.generate_image(prompt) ──►  image_client   ──►  SD API :7860
  │
  └─ app.ai.suggest_metadata(seed) ──►  metadata       ──►  ollama_client ──► Ollama
```

---

## What is NOT in scope
- Async/streaming UI (HTMX SSE) — kept as a stub for later
- Storing generated images in the DB — left to the caller
- Model management (pull/list models) — out of scope, use Ollama CLI
