"""Which colours the accent takes over, and what it turns them into.

Spoti Mi repaints Spotify's brand green family (#1DB954, #1ED760, etc.)
into a striking Gothic Kawaii Pink (#FF2A85), giving the app a unique
dark anime / Kuromi aesthetic while preserving full contrast on OLED black.

The rule maps colours in HSV space:
* Any colour with a hue within 35 degrees of Spotify Green (141.2 deg)
  that has enough saturation and value to not be grey/white/black.
* It shifts the hue, saturation, and brightness by the exact delta between
  Spotify Green and Gothic Kawaii Pink, so gradients and alpha stay smooth.
"""

from __future__ import annotations

import colorsys
from typing import Tuple

# Spotify Green reference
REFERENCE_HEX = 0x1DB954

# Default target: Gothic Kawaii Pink (#FF2A85)
DEFAULT_ACCENT_HEX = 0xFF2A85

# Alternative palettes
PALETTES = {
    "gothic_kawaii_pink": 0xFF2A85,  # Kuromi / Dark Kawaii Hot Pink
    "sweet_sakura": 0xFF70A6,        # Pastel Sakura Pink
    "cyber_magenta": 0xE056FD,       # Cyberpunk Neon Magenta
    "blood_rose": 0xE8175D,          # Gothic Crimson Rose
    "midnight_orchid": 0xBD00FF,     # Dark Anime Violet
    "spotify_green": 0x1DB954,       # Stock Green
}

# How far from the reference hue still counts as the same family (in degrees).
HUE_TOLERANCE = 35.0

MIN_SATURATION = 0.25
MIN_VALUE = 0.20


def _split(colour: int) -> Tuple[int, float, float, float]:
    alpha = (colour >> 24) & 0xFF
    red = ((colour >> 16) & 0xFF) / 255.0
    green = ((colour >> 8) & 0xFF) / 255.0
    blue = (colour & 0xFF) / 255.0
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    return alpha, hue, saturation, value


def _join(alpha: int, hue: float, saturation: float, value: float) -> int:
    red, green, blue = colorsys.hsv_to_rgb(hue % 1.0, _clamp(saturation), _clamp(value))
    return (
        ((alpha & 0xFF) << 24)
        | (int(round(red * 255)) << 16)
        | (int(round(green * 255)) << 8)
        | int(round(blue * 255))
    )


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def captures(colour: int, reference: int = REFERENCE_HEX) -> bool:
    """Returns True if the colour belongs to the Spotify green family."""
    _, ref_h, _, _ = _split(reference)
    _, h, s, v = _split(colour)

    if s < MIN_SATURATION or v < MIN_VALUE:
        return False

    diff = abs(h - ref_h)
    if diff > 0.5:
        diff = 1.0 - diff
    return (diff * 360.0) <= HUE_TOLERANCE


def map_colour(colour: int, reference: int = REFERENCE_HEX, target: int = DEFAULT_ACCENT_HEX) -> int:
    """Maps a green-family colour into the target gothic kawaii pink."""
    if not captures(colour, reference):
        return colour

    alpha, h, s, v = _split(colour)
    _, ref_h, ref_s, ref_v = _split(reference)
    _, tgt_h, tgt_s, tgt_v = _split(target)

    # Shift hue
    delta_h = (tgt_h - ref_h) % 1.0
    new_h = (h + delta_h) % 1.0

    # Scale saturation & value proportionally
    scale_s = tgt_s / ref_s if ref_s > 0 else 1.0
    scale_v = tgt_v / ref_v if ref_v > 0 else 1.0

    new_s = _clamp(s * scale_s)
    new_v = _clamp(v * scale_v)

    return _join(alpha, new_h, new_s, new_v)
