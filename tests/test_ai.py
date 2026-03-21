"""
Tests for the app/ai/ integration layer.

All tests monkeypatch httpx so no real network calls are made.
"""

from __future__ import annotations

import base64
import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.ai.config import AIConfig
from app.ai.exceptions import ImageGenError, OllamaError
from app.ai.image_client import generate_image
from app.ai.metadata import (
    AffirmationSuggestion,
    GratitudeSuggestion,
    QuoteSuggestion,
    suggest_affirmation,
    suggest_gratitude_metadata,
    suggest_quote,
)
from app.ai.ollama_client import chat, generate_text

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TEST_CONFIG = AIConfig(
    ollama_base_url="http://test-ollama:11434",
    ollama_text_model="test-model",
    image_gen_base_url="http://test-sd:7860",
    image_gen_model="",
    timeout=5,
)


def _mock_response(status_code: int, body: Any) -> MagicMock:
    """Build a fake httpx.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = body
    mock.text = json.dumps(body)
    return mock


# ---------------------------------------------------------------------------
# generate_text
# ---------------------------------------------------------------------------


class TestGenerateText:
    def test_happy_path(self) -> None:
        response = _mock_response(200, {"response": "Hello, world!"})
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            result = generate_text("Say hello", config=TEST_CONFIG)
        assert result == "Hello, world!"

    def test_passes_system_prompt(self) -> None:
        response = _mock_response(200, {"response": "ok"})
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = response
            generate_text("Hi", system="You are terse.", config=TEST_CONFIG)
            call_kwargs = mock_post.call_args
            assert call_kwargs.kwargs["json"]["system"] == "You are terse."

    def test_non_200_raises_ollama_error(self) -> None:
        response = _mock_response(500, {"error": "internal error"})
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            with pytest.raises(OllamaError) as exc_info:
                generate_text("Hi", config=TEST_CONFIG)
        assert exc_info.value.status_code == 500

    def test_connection_error_raises_ollama_error(self) -> None:
        import httpx as _httpx

        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.side_effect = (
                _httpx.ConnectError("refused")
            )
            with pytest.raises(OllamaError, match="Could not reach Ollama"):
                generate_text("Hi", config=TEST_CONFIG)

    def test_unexpected_response_shape_raises_ollama_error(self) -> None:
        response = _mock_response(200, {"not_response": "oops"})
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            with pytest.raises(OllamaError, match="Unexpected"):
                generate_text("Hi", config=TEST_CONFIG)


# ---------------------------------------------------------------------------
# chat
# ---------------------------------------------------------------------------


class TestChat:
    def test_happy_path(self) -> None:
        body = {"message": {"role": "assistant", "content": "Hi there!"}}
        response = _mock_response(200, body)
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            result = chat([{"role": "user", "content": "Hello"}], config=TEST_CONFIG)
        assert result == "Hi there!"

    def test_non_200_raises_ollama_error(self) -> None:
        response = _mock_response(404, {"error": "model not found"})
        with patch("app.ai.ollama_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            with pytest.raises(OllamaError) as exc_info:
                chat([], config=TEST_CONFIG)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# generate_image
# ---------------------------------------------------------------------------


class TestGenerateImage:
    def test_happy_path(self) -> None:
        fake_png = b"\x89PNG\r\n"
        encoded = base64.b64encode(fake_png).decode()
        response = _mock_response(200, {"images": [encoded]})
        with patch("app.ai.image_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            result = generate_image("a sunny day", config=TEST_CONFIG)
        assert result == fake_png

    def test_non_200_raises_image_gen_error(self) -> None:
        response = _mock_response(503, {"error": "unavailable"})
        with patch("app.ai.image_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            with pytest.raises(ImageGenError) as exc_info:
                generate_image("anything", config=TEST_CONFIG)
        assert exc_info.value.status_code == 503

    def test_empty_images_list_raises_image_gen_error(self) -> None:
        response = _mock_response(200, {"images": []})
        with patch("app.ai.image_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = response
            with pytest.raises(ImageGenError, match="no images"):
                generate_image("anything", config=TEST_CONFIG)

    def test_connection_error_raises_image_gen_error(self) -> None:
        import httpx as _httpx

        with patch("app.ai.image_client.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.side_effect = (
                _httpx.ConnectError("refused")
            )
            with pytest.raises(ImageGenError, match="Could not reach"):
                generate_image("anything", config=TEST_CONFIG)


# ---------------------------------------------------------------------------
# suggest_gratitude_metadata
# ---------------------------------------------------------------------------


class TestSuggestGratitudeMetadata:
    def _patch_generate(self, text: str) -> Any:
        return patch("app.ai.metadata.generate_text", return_value=text)

    def test_happy_path(self) -> None:
        payload = json.dumps({"title": "Morning coffee", "description": "I love mornings."})
        with self._patch_generate(payload):
            result = suggest_gratitude_metadata("coffee")
        assert isinstance(result, GratitudeSuggestion)
        assert result.title == "Morning coffee"
        assert result.description == "I love mornings."

    def test_json_wrapped_in_prose(self) -> None:
        payload = 'Sure! Here you go: {"title": "Sunshine", "description": "Warm day."} Hope that helps!'
        with self._patch_generate(payload):
            result = suggest_gratitude_metadata("sun")
        assert result.title == "Sunshine"

    def test_bad_json_returns_empty_suggestion(self) -> None:
        with self._patch_generate("I cannot help with that."):
            result = suggest_gratitude_metadata("anything")
        assert isinstance(result, GratitudeSuggestion)
        assert result.title is None
        assert result.description is None

    def test_ollama_error_returns_empty_suggestion(self) -> None:
        with patch("app.ai.metadata.generate_text", side_effect=OllamaError("down")):
            result = suggest_gratitude_metadata("anything")
        assert isinstance(result, GratitudeSuggestion)
        assert result.title is None


# ---------------------------------------------------------------------------
# suggest_affirmation
# ---------------------------------------------------------------------------


class TestSuggestAffirmation:
    def test_happy_path(self) -> None:
        payload = json.dumps({"text": "I am capable.", "author": ""})
        with patch("app.ai.metadata.generate_text", return_value=payload):
            result = suggest_affirmation()
        assert isinstance(result, AffirmationSuggestion)
        assert result.text == "I am capable."

    def test_with_topic(self) -> None:
        payload = json.dumps({"text": "I am resilient.", "author": ""})
        with patch("app.ai.metadata.generate_text", return_value=payload) as mock_gen:
            suggest_affirmation(topic="resilience")
            call_prompt: str = mock_gen.call_args[0][0]
        assert "resilience" in call_prompt

    def test_bad_json_returns_empty(self) -> None:
        with patch("app.ai.metadata.generate_text", return_value="nope"):
            result = suggest_affirmation()
        assert result == AffirmationSuggestion()


# ---------------------------------------------------------------------------
# suggest_quote
# ---------------------------------------------------------------------------


class TestSuggestQuote:
    def test_happy_path(self) -> None:
        payload = json.dumps({"text": "Be the change.", "author": "Gandhi"})
        with patch("app.ai.metadata.generate_text", return_value=payload):
            result = suggest_quote()
        assert isinstance(result, QuoteSuggestion)
        assert result.author == "Gandhi"

    def test_bad_json_returns_empty(self) -> None:
        with patch("app.ai.metadata.generate_text", return_value="???"):
            result = suggest_quote()
        assert result == QuoteSuggestion()
