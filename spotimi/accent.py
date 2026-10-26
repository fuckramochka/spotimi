"""Bakes the Gothic Kawaii Pink accent into Spotify's compiled resources.

Most dynamic colours can be patched in bytecode, but vector drawables,
XML selectors, and shape solids are parsed natively by Android's AssetManager
directly from resources.arsc and compiled binary XML (AXML).

This module walks resources.arsc and every res/**/*.xml, detects Spotify's
green family (#1DB954, #1ED760, etc.) in Res_value typed entries, and maps
them to the requested Gothic Kawaii Pink (#FF2A85) while keeping alpha
and lightness shading intact.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .apkzip import Apk
from .arsc import Arsc
from .axml import Axml
from .palette import REFERENCE_HEX, DEFAULT_ACCENT_HEX, captures, map_colour

COLOUR_TYPES = (0x1C, 0x1D, 0x1E, 0x1F)


def bake(
    apk: Apk,
    arsc: Arsc,
    old: int = REFERENCE_HEX,
    new: int = DEFAULT_ACCENT_HEX,
    pairs: Dict[int, int] = None,
) -> List[str]:
    """Shifts Spotify's green family to the Gothic Kawaii Pink accent."""
    writing = old != new
    report = []
    if pairs is None:
        pairs = {}

    entries, shades = _walk_table(arsc, old, new, writing, pairs)

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

    if writing:
        report.append(f"ARSC resource entries updated: {entries}")
        report.append(f"Compiled XML vectors/drawables: {changes} colours in {files} files")
        report.append(f"{len(shades)} shades of Spotify Green transformed into Gothic Kawaii Pink")
    else:
        report.append("Stock Spotify green preserved, no accent transformation needed")

    return report


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
