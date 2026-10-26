"""Command-line entrypoint for Spoti Mi.

Usage:
    python3 -m spotimi path/to/spotify.apk [-o dist/SpotiMi.apk] [--accent FF2A85]
"""

from __future__ import annotations

import argparse
import os
import sys

from . import build, palette

BANNER = r"""
  ____                  _     _   __  __  _ 
 / ___|  _ __    ___   | |_  (_) |  \/  |(_)
 \___ \ | '_ \  / _ \  | __| | | | |\/| || |
  ___) || |_) || (_) | | |_  | | | |  | || |
 |____/ | .__/  \___/   \__| |_| |_|  |_||_|
        |_|     ★ Gothic Kawaii Edition ★
"""


def parse_color(val: str) -> int:
    val_clean = val.strip().lower()
    if val_clean in palette.PALETTES:
        return palette.PALETTES[val_clean]
    if val_clean.startswith("#"):
        val_clean = val_clean[1:]
    if val_clean.startswith("0x"):
        val_clean = val_clean[2:]
    try:
        return int(val_clean, 16)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid color format: {val}. Use hex (e.g. FF2A85) or palette name {list(palette.PALETTES.keys())}"
        )


def main() -> None:
    print(BANNER)
    parser = argparse.ArgumentParser(
        prog="spotimi",
        description="Spoti Mi — A Gothic Kawaii Spotify Mod Patcher for Android",
    )
    parser.add_argument(
        "apk",
        metavar="SPOTIFY_APK",
        help="Path to an official Spotify universal or arm64 APK",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="dist/SpotiMi.apk",
        help="Destination path for the modded APK (default: dist/SpotiMi.apk)",
    )
    parser.add_argument(
        "--accent",
        default="gothic_blood_rose",
        type=parse_color,
        help="Accent colour (hex B81B34 or preset: gothic_blood_rose, cherry_rose, gothic_crimson, dark_ruby)",
    )
    parser.add_argument(
        "--tools",
        default=os.path.join(os.path.dirname(__file__), "..", "tools"),
        help="Directory with build tools (R8, smali, android.jar)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress verbose build logs",
    )

    args = parser.parse_args()

    try:
        build.build(
            apk_in=args.apk,
            apk_out=args.output,
            accent_hex=args.accent,
            tools_dir=args.tools,
            quiet=args.quiet,
        )
    except Exception as e:
        print(f"\n❌ Build error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
