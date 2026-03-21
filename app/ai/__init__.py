"""
AI integration layer for the ty app.

Provides a simple, unified interface for:
  - Text generation via Ollama (local LLM)
  - Image generation via a Stable Diffusion Web UI backend
  - Metadata suggestions for database rows

Typical usage
-------------
    from app.ai import generate_text, generate_image
    from app.ai import suggest_gratitude_metadata, suggest_affirmation, suggest_quote

    # Text
    reply = generate_text("Write a short gratitude note about coffee")

    # Image (returns raw PNG bytes)
    png_bytes = generate_image("A warm sunrise over a quiet forest")

    # Row metadata suggestions
    suggestion = suggest_gratitude_metadata("morning run")
    item = GratitudeItemCreate(
        title=suggestion.title or "Morning run",
        description=suggestion.description or "",
    )

Configuration
-------------
All backends are configured via environment variables (see app.ai.config).
No env vars are required; the defaults point to standard local ports.
"""

from app.ai.image_client import generate_image as generate_image
from app.ai.metadata import (
    AffirmationSuggestion as AffirmationSuggestion,
    GratitudeSuggestion as GratitudeSuggestion,
    QuoteSuggestion as QuoteSuggestion,
    suggest_affirmation as suggest_affirmation,
    suggest_gratitude_metadata as suggest_gratitude_metadata,
    suggest_quote as suggest_quote,
)
from app.ai.ollama_client import (
    chat as chat,
    generate_text as generate_text,
    generate_text_stream as generate_text_stream,
)

__all__ = [
    # Text
    "generate_text",
    "generate_text_stream",
    "chat",
    # Images
    "generate_image",
    # Metadata suggestions
    "suggest_gratitude_metadata",
    "suggest_affirmation",
    "suggest_quote",
    # Suggestion models
    "GratitudeSuggestion",
    "AffirmationSuggestion",
    "QuoteSuggestion",
]
