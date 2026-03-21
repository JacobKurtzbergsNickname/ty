"""
Thin wrapper around the Ollama HTTP API.

Supported endpoints
-------------------
  POST /api/generate  – single-shot text completion
  POST /api/chat      – multi-turn chat completion

Public functions
----------------
  generate_text(prompt, *, model, system, config) -> str
  chat(messages, *, model, config) -> str
"""

from __future__ import annotations

from typing import Iterator

import httpx

from app.ai.config import AIConfig, load_ai_config
from app.ai.exceptions import OllamaError


def generate_text(
    prompt: str,
    *,
    model: str | None = None,
    system: str | None = None,
    config: AIConfig | None = None,
) -> str:
    """Send a prompt to Ollama and return the complete response text.

    Args:
        prompt: The user prompt to send.
        model: Override the default model from config.
        system: Optional system instruction prepended to the prompt.
        config: Override the default config (useful in tests).

    Returns:
        The model's response as a plain string.

    Raises:
        OllamaError: If the request fails or the API returns an error.
    """
    cfg = config or load_ai_config()
    resolved_model = model or cfg.ollama_text_model

    payload: dict[str, object] = {
        "model": resolved_model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    return _post_generate(cfg, payload)


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    config: AIConfig | None = None,
) -> str:
    """Send a list of chat messages to Ollama and return the assistant reply.

    Each message must be a dict with ``role`` (``"user"`` or ``"assistant"``)
    and ``content`` keys.

    Args:
        messages: Conversation history in OpenAI-style message format.
        model: Override the default model from config.
        config: Override the default config (useful in tests).

    Returns:
        The assistant's reply as a plain string.

    Raises:
        OllamaError: If the request fails or the API returns an error.
    """
    cfg = config or load_ai_config()
    resolved_model = model or cfg.ollama_text_model

    payload: dict[str, object] = {
        "model": resolved_model,
        "messages": messages,
        "stream": False,
    }

    try:
        with httpx.Client(timeout=cfg.timeout) as client:
            response = client.post(f"{cfg.ollama_base_url}/api/chat", json=payload)
    except httpx.RequestError as exc:
        raise OllamaError(f"Could not reach Ollama at {cfg.ollama_base_url}: {exc}") from exc

    if response.status_code != 200:
        raise OllamaError(
            f"Ollama /api/chat returned {response.status_code}: {response.text}",
            status_code=response.status_code,
        )

    data = response.json()
    try:
        return str(data["message"]["content"])
    except (KeyError, TypeError) as exc:
        raise OllamaError(f"Unexpected Ollama chat response shape: {data}") from exc


def generate_text_stream(
    prompt: str,
    *,
    model: str | None = None,
    system: str | None = None,
    config: AIConfig | None = None,
) -> Iterator[str]:
    """Stream tokens from Ollama one chunk at a time.

    Yields individual text fragments as they arrive.  Intended for future
    HTMX Server-Sent Events (SSE) support.

    Args:
        prompt: The user prompt to send.
        model: Override the default model from config.
        system: Optional system instruction.
        config: Override the default config (useful in tests).

    Yields:
        Text fragments from the model response stream.

    Raises:
        OllamaError: If the connection fails.
    """
    import json  # local import: only needed for streaming path

    cfg = config or load_ai_config()
    resolved_model = model or cfg.ollama_text_model

    payload: dict[str, object] = {
        "model": resolved_model,
        "prompt": prompt,
        "stream": True,
    }
    if system:
        payload["system"] = system

    try:
        with httpx.Client(timeout=cfg.timeout) as client:
            with client.stream("POST", f"{cfg.ollama_base_url}/api/generate", json=payload) as resp:
                if resp.status_code != 200:
                    raise OllamaError(
                        f"Ollama stream returned {resp.status_code}",
                        status_code=resp.status_code,
                    )
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if token := chunk.get("response"):
                        yield token
                    if chunk.get("done"):
                        break
    except httpx.RequestError as exc:
        raise OllamaError(f"Could not reach Ollama at {cfg.ollama_base_url}: {exc}") from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _post_generate(cfg: AIConfig, payload: dict[str, object]) -> str:
    """POST to /api/generate and return the response text."""
    try:
        with httpx.Client(timeout=cfg.timeout) as client:
            response = client.post(f"{cfg.ollama_base_url}/api/generate", json=payload)
    except httpx.RequestError as exc:
        raise OllamaError(f"Could not reach Ollama at {cfg.ollama_base_url}: {exc}") from exc

    if response.status_code != 200:
        raise OllamaError(
            f"Ollama /api/generate returned {response.status_code}: {response.text}",
            status_code=response.status_code,
        )

    data = response.json()
    try:
        return str(data["response"])
    except (KeyError, TypeError) as exc:
        raise OllamaError(f"Unexpected Ollama response shape: {data}") from exc
