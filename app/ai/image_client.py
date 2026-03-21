"""
Wrapper around a Stable Diffusion Web UI (Automatic1111) REST backend for
text-to-image generation.

The expected backend exposes the standard SD Web UI API:
  POST /sdapi/v1/txt2img  → JSON with a ``images`` list of base64-encoded PNGs

Public functions
----------------
  generate_image(prompt, *, negative_prompt, width, height, config) -> bytes
"""

from __future__ import annotations

import base64

import httpx

from app.ai.config import AIConfig, load_ai_config
from app.ai.exceptions import ImageGenError

# Stable Diffusion Web UI defaults
_DEFAULT_WIDTH = 512
_DEFAULT_HEIGHT = 512
_DEFAULT_STEPS = 20
_DEFAULT_CFG_SCALE = 7.0


def generate_image(
    prompt: str,
    *,
    negative_prompt: str = "",
    width: int = _DEFAULT_WIDTH,
    height: int = _DEFAULT_HEIGHT,
    steps: int = _DEFAULT_STEPS,
    cfg_scale: float = _DEFAULT_CFG_SCALE,
    config: AIConfig | None = None,
) -> bytes:
    """Generate an image from a text prompt and return raw PNG bytes.

    Calls the Stable Diffusion Web UI ``/sdapi/v1/txt2img`` endpoint.  The
    caller decides how to store or serve the result (write to disk, embed as
    base64 in HTML, etc.).

    Args:
        prompt: Positive text description of the desired image.
        negative_prompt: Things to exclude from the image.
        width: Output image width in pixels (default 512).
        height: Output image height in pixels (default 512).
        steps: Number of diffusion steps (default 20).
        cfg_scale: Classifier-free guidance scale (default 7.0).
        config: Override the default config (useful in tests).

    Returns:
        Raw PNG image data as bytes.

    Raises:
        ImageGenError: If the request fails, the backend is unreachable, or
            the response does not contain a valid image.
    """
    cfg = config or load_ai_config()

    payload: dict[str, object] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
    }
    if cfg.image_gen_model:
        payload["override_settings"] = {"sd_model_checkpoint": cfg.image_gen_model}

    try:
        with httpx.Client(timeout=cfg.timeout) as client:
            response = client.post(f"{cfg.image_gen_base_url}/sdapi/v1/txt2img", json=payload)
    except httpx.RequestError as exc:
        raise ImageGenError(
            f"Could not reach image-gen backend at {cfg.image_gen_base_url}: {exc}"
        ) from exc

    if response.status_code != 200:
        raise ImageGenError(
            f"Image-gen backend returned {response.status_code}: {response.text}",
            status_code=response.status_code,
        )

    data = response.json()
    images: list[str] | None = data.get("images")
    if not images:
        raise ImageGenError("Image-gen response contained no images")

    try:
        return base64.b64decode(images[0])
    except Exception as exc:
        raise ImageGenError(f"Failed to decode image data: {exc}") from exc
