"""
Configuration for the AI integration layer.

All values are read from environment variables with safe defaults so the app
starts without any setup; operators can override by setting env vars.

  OLLAMA_BASE_URL      – Ollama API root          (default: http://localhost:11434)
  OLLAMA_TEXT_MODEL    – Default text model        (default: llama3)
  IMAGE_GEN_BASE_URL   – Image-gen API root        (default: http://localhost:7860)
  IMAGE_GEN_MODEL      – Optional model hint       (default: "")
  AI_TIMEOUT           – HTTP timeout in seconds   (default: 60)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    """Immutable snapshot of AI service configuration."""

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
