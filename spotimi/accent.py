"""Bakes the Gothic accent into Spotify's compiled resources and drawables.

Most dynamic colours can be patched in bytecode, but vector drawables,
XML selectors, shape solids, Lottie animations, and PNG drawables
are parsed by Android's AssetManager or Skia.

This module walks:
1. resources.arsc
2. Compiled binary XML (AXML) drawables & layouts
3. Lottie JSON animations
4. Raster PNG drawables
and maps all green tokens to the target Gothic accent.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .apkzip import Apk
from .arsc import Arsc
from .axml import Axml
from .palette import REFERENCE_HEX, DEFAULT_ACCENT_HEX, captures, map_colour
from . import png

COLOUR_TYPES = (0x1C, 0x1D, 0x1E, 0x1F)


def bake(
    apk: Apk,
    arsc: Arsc,
    old: int = REFERENCE_HEX,
    new: int = DEFAULT_ACCENT_HEX,
    pairs: Dict[int, int] = None,
) -> List[str]:
    """Shifts Spotify's green family to the Gothic accent."""
    writing = old != new
    report = []
    if pairs is None:
        pairs = {}

    # 1. ARSC
    entries, shades = _walk_table(arsc, old, new, writing, pairs)

    # 2. AXML drawables
    files = 0
    changes = 0
    for name in apk.names():
        if not (name.startswith("res/") and name.endswith(".xml")):
            continue
        try:
            axml = Axml.parse(apk.read(name))
        except Exception:
            continue
        here = 0
        for node in axml.nodes:
            for attribute in node.attributes:
                if attribute.kind in COLOUR_TYPES and captures(attribute.data, old):
                    shades.add(attribute.data)
                    if writing:
                        moved = map_colour(attribute.data, old, new)
                        pairs[moved] = attribute.data
                        attribute.data = moved
                    here += 1
        if here:
            if writing:
                apk.replace(name, axml.build())
            files += 1
            changes += here

    # 3. Lottie JSON animations
    json_changes = 0
    for name in apk.names():
        if name.endswith(".json") and name.startswith("res/"):
            data = apk.read(name)
            new_data = _recolour_json(data, old, new)
            if new_data != data:
                if writing:
                    apk.replace(name, new_data)
                json_changes += 1

    # 4. PNG drawables
    png_changes = 0
    for name in apk.names():
        if (name.endswith(".png") and not name.endswith(".9.png")) and "drawable" in name:
            data = apk.read(name)
            try:
                new_data = _recolour_png(data, old, new)
                if new_data != data:
                    if writing:
                        apk.replace(name, new_data)
                    png_changes += 1
            except Exception:
                pass

    if writing:
        report.append(f"ARSC resource entries updated: {entries}")
        report.append(f"Compiled XML vectors/drawables: {changes} colours in {files} files")
        if json_changes:
            report.append(f"Lottie animations recoloured: {json_changes} files")
        if png_changes:
            report.append(f"PNG drawables recoloured: {png_changes} files")
        report.append(f"{len(shades)} shades of Spotify Green transformed into Gothic Accent")
    else:
        report.append("Stock Spotify green preserved, no accent transformation needed")

    return report


def _recolour_json(data: bytes, old_hex: int, new_hex: int) -> bytes:
    text = data.decode("utf-8", errors="ignore")
    # Replace hex strings #1DB954, #1ED760
    old_s1 = f"{old_hex:06X}"
    new_s1 = f"{new_hex:06X}"
    old_s2 = "1ED760"
    new_s2 = f"{map_colour(0xFF1ED760, old_hex, new_hex) & 0xFFFFFF:06X}"

    changed = False
    for o, n in [(old_s1, new_s1), (old_s2, new_s2)]:
        pattern = re.compile(re.escape(o), re.IGNORECASE)
        if pattern.search(text):
            text = pattern.sub(n, text)
            changed = True
    return text.encode("utf-8") if changed else data


def _recolour_png(data: bytes, old_hex: int, new_hex: int) -> bytes:
    img = png.decode(data)
    pixels = img.pixels
    modified = False
    memo: Dict[int, int] = {}

    for i in range(0, len(pixels), 4):
        a = pixels[i + 3]
        if a < 20:
            continue
        argb = (a << 24) | (pixels[i] << 16) | (pixels[i + 1] << 8) | pixels[i + 2]
        now = memo.get(argb)
        if now is None:
            if captures(argb, old_hex):
                now = map_colour(argb, old_hex, new_hex)
            else:
                now = argb
            memo[argb] = now

        if now != argb:
            pixels[i] = (now >> 16) & 0xFF
            pixels[i + 1] = (now >> 8) & 0xFF
            pixels[i + 2] = now & 0xFF
            pixels[i + 3] = (now >> 24) & 0xFF
            modified = True

    return png.encode(img) if modified else data


def _walk_table(arsc: Arsc, old: int, new: int, writing: bool, pairs: Dict[int, int]):
    found = 0
    shades = set()
    for package in arsc.packages:
        for type_id in list(package.types):
            for entry in _entries(arsc, package, type_id):
                if entry.kind in COLOUR_TYPES and captures(entry.data, old):
                    shades.add(entry.data)
                    if writing:
                        moved = map_colour(entry.data, old, new)
                        pairs[moved] = entry.data
                        arsc.set_value(entry, entry.kind, moved)
                    found += 1
    return found, shades


def _entries(arsc: Arsc, package, type_id: int):
    for entry_id in range(_entry_count(arsc, package, type_id)):
        res_id = (package.id << 24) | (type_id << 16) | entry_id
        for value in arsc.values(res_id):
            yield value


def _entry_count(arsc: Arsc, package, type_id: int) -> int:
    import struct

    most = 0
    for chunk in package.types.get(type_id, []):
        count = struct.unpack_from("<I", arsc.data, chunk + 12)[0]
        most = max(most, count)
    return most
