"""
Exceptions raised by the AI integration layer.
"""


class AIError(Exception):
    """Base class for all AI service errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class OllamaError(AIError):
    """Raised when the Ollama API returns an error or is unreachable."""


class ImageGenError(AIError):
    """Raised when the image-generation backend returns an error or is unreachable."""
