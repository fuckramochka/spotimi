"""Surgical bytecode constant and string literal recoloring for DEX files.

Spotify's Jetpack Compose design tokens (Encore) and Kotlin components
hardcode 32-bit and 64-bit color constants directly into Dalvik bytecode:
- const vAA, #+BBBBBBBB (0x14)
- const-wide/32 vAA, #+BBBBBBBB (0x18)
- Hex string tokens: b"1ED760", b"#1ED760", b"1DB954"

This module walks every DEX file in the APK, identifies all green tokens,
shifts them to the target accent color in-place without changing file offsets,
and updates the SHA-1 and Adler32 checksums in the DEX header.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from typing import Tuple

from .palette import captures, map_colour, DEFAULT_ACCENT_HEX, REFERENCE_HEX


def fix_dex_checksums(data: bytearray) -> bytearray:
    """Updates SHA-1 signature and Adler-32 checksum in the DEX header."""
    sha1 = hashlib.sha1(data[32:]).digest()
    data[12:32] = sha1
    adler = zlib.adler32(data[12:]) & 0xFFFFFFFF
    data[8:12] = struct.pack("<I", adler)
    return data


def recolour_dex_bytes(
    data: bytes,
    old_hex: int = REFERENCE_HEX,
    new_hex: int = DEFAULT_ACCENT_HEX,
) -> Tuple[bytes, int]:
    """Recolours all Dalvik const/const-wide instructions and hex strings in a DEX file."""
    barray = bytearray(data)
    changes = 0
    n = len(barray)

    # 1. Dalvik opcode scan for 32-bit & 64-bit color literals
    i = 0
    while i < n - 6:
        op = barray[i]
        # const vAA, #+BBBBBBBB (14 AA BB BB BB BB)
        # const-wide/32 vAA, #+BBBBBBBB (18 AA BB BB BB BB)
        if op in (0x14, 0x18):
            val = struct.unpack_from("<I", barray, i + 2)[0]
            if (val >> 24) == 0xFF and captures(val, old_hex):
                new_val = map_colour(val, old_hex, new_hex)
                struct.pack_into("<I", barray, i + 2, new_val)
                changes += 1
                i += 6
                continue
        i += 2

    # 2. String literal replacements (exact byte length preservation)
    old_hex_str = f"{old_hex:06X}".encode("ascii")
    new_hex_str = f"{new_hex:06X}".encode("ascii")

    # Spotify bright green (1ED760)
    bright_old = b"1ED760"
    bright_target = f"{map_colour(0xFF1ED760, old_hex, new_hex) & 0xFFFFFF:06X}".encode("ascii")

    for src, dst in [(old_hex_str, new_hex_str), (bright_old, bright_target)]:
        if src == dst:
            continue
        idx = 0
        while True:
            idx = barray.find(src, idx)
            if idx == -1:
                break
            barray[idx : idx + len(src)] = dst
            changes += 1
            idx += len(src)

    if changes > 0:
        fix_dex_checksums(barray)
        return bytes(barray), changes

    return data, 0
