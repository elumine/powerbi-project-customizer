from __future__ import annotations

import colorsys
import hashlib


def stable_color(seed: str, saturation: float = 0.46, lightness: float = 0.48) -> str:
    """Generate a deterministic UI color from stable text."""

    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    hue = int.from_bytes(digest[:2], "big") / 65535
    sat = _clamp(saturation + (digest[2] / 255 - 0.5) * 0.12)
    light = _clamp(lightness + (digest[3] / 255 - 0.5) * 0.10)
    red, green, blue = colorsys.hls_to_rgb(hue, light, sat)
    return f"#{round(red * 255):02x}{round(green * 255):02x}{round(blue * 255):02x}"


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}.{digest}"


def _clamp(value: float, minimum: float = 0.25, maximum: float = 0.72) -> float:
    return max(minimum, min(maximum, value))
