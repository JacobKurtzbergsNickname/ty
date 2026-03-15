"""
High-level helpers that use the Ollama text API to suggest metadata for
database rows.

Each function sends a structured prompt that requests JSON output, parses
the response, and returns a typed Pydantic model.  If the model returns
malformed JSON the function degrades gracefully by returning an empty
suggestion (no crash, no partial data leaking into the DB).

Public functions
----------------
  suggest_gratitude_metadata(seed, *, config) -> GratitudeSuggestion
  suggest_affirmation(topic, *, config)       -> AffirmationSuggestion
  suggest_quote(topic, *, config)             -> QuoteSuggestion
"""

from __future__ import annotations

import json
import logging

from pydantic import BaseModel

from app.ai.config import AIConfig
from app.ai.exceptions import OllamaError
from app.ai.ollama_client import generate_text

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Suggestion models
# ---------------------------------------------------------------------------


class GratitudeSuggestion(BaseModel):
    """Suggested field values for a GratitudeItem row."""

    title: str | None = None
    description: str | None = None


class AffirmationSuggestion(BaseModel):
    """Suggested field values for an Affirmation row."""

    text: str | None = None
    author: str | None = None


class QuoteSuggestion(BaseModel):
    """Suggested field values for a PositiveQuote row."""

    text: str | None = None
    author: str | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def suggest_gratitude_metadata(
    seed: str,
    *,
    config: AIConfig | None = None,
) -> GratitudeSuggestion:
    """Ask Ollama to suggest a gratitude title and description from a short seed.

    Args:
        seed: A short phrase or keyword the user wants to express gratitude for.
        config: Override the default AI config (useful in tests).

    Returns:
        A :class:`GratitudeSuggestion` with populated fields on success, or
        empty fields if the model response cannot be parsed.
    """
    prompt = (
        "You are a helpful journaling assistant.\n"
        "Given the following seed phrase, suggest a short gratitude journal entry.\n"
        f"Seed: {seed}\n\n"
        "Respond with ONLY valid JSON in this exact shape, no extra text:\n"
        '{"title": "<short title, max 100 chars>", "description": "<one or two sentences, max 500 chars>"}'
    )
    raw = _safe_generate(prompt, config=config)
    if raw is None:
        return GratitudeSuggestion()
    return _parse_suggestion(raw, GratitudeSuggestion)


def suggest_affirmation(
    topic: str | None = None,
    *,
    config: AIConfig | None = None,
) -> AffirmationSuggestion:
    """Ask Ollama to generate a positive affirmation.

    Args:
        topic: Optional theme or keyword to focus the affirmation on.
        config: Override the default AI config (useful in tests).

    Returns:
        An :class:`AffirmationSuggestion` with populated fields on success, or
        empty fields if the model response cannot be parsed.
    """
    topic_clause = f" about the topic: {topic}" if topic else ""
    prompt = (
        "You are a helpful journaling assistant.\n"
        f"Write a short, positive personal affirmation{topic_clause}.\n\n"
        "Respond with ONLY valid JSON in this exact shape, no extra text:\n"
        '{"text": "<the affirmation, max 300 chars>", "author": "<your name or leave empty>"}'
    )
    raw = _safe_generate(prompt, config=config)
    if raw is None:
        return AffirmationSuggestion()
    return _parse_suggestion(raw, AffirmationSuggestion)


def suggest_quote(
    topic: str | None = None,
    *,
    config: AIConfig | None = None,
) -> QuoteSuggestion:
    """Ask Ollama to suggest a positive, motivational quote.

    Args:
        topic: Optional theme or keyword to focus the quote on.
        config: Override the default AI config (useful in tests).

    Returns:
        A :class:`QuoteSuggestion` with populated fields on success, or
        empty fields if the model response cannot be parsed.
    """
    topic_clause = f" related to: {topic}" if topic else ""
    prompt = (
        "You are a helpful journaling assistant.\n"
        f"Suggest a well-known positive or motivational quote{topic_clause}.\n\n"
        "Respond with ONLY valid JSON in this exact shape, no extra text:\n"
        '{"text": "<the quote, max 300 chars>", "author": "<the author\'s name>"}'
    )
    raw = _safe_generate(prompt, config=config)
    if raw is None:
        return QuoteSuggestion()
    return _parse_suggestion(raw, QuoteSuggestion)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

type _SuggestionT = GratitudeSuggestion | AffirmationSuggestion | QuoteSuggestion


def _safe_generate(prompt: str, *, config: AIConfig | None) -> str | None:
    """Call generate_text and swallow OllamaError, returning None on failure."""
    try:
        return generate_text(prompt, config=config)
    except OllamaError as exc:
        _log.warning("Ollama request failed: %s", exc)
        return None


def _parse_suggestion(raw: str, model_cls: type[_SuggestionT]) -> _SuggestionT:
    """Parse a JSON string into a suggestion model, returning empty on failure."""
    cleaned = _extract_json(raw)
    try:
        data = json.loads(cleaned)
        return model_cls(**{k: v for k, v in data.items() if v is not None})
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        _log.warning("Could not parse suggestion JSON from model output: %s — %s", raw, exc)
        return model_cls()


def _extract_json(text: str) -> str:
    """Extract the first {...} block from text to handle models that add prose."""
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text
