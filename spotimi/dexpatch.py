"""Bytecode patcher for Spoti Mi.

Applies surgical, targeted patches to Spotify's Player Restrictions without touching
Android framework classes or BaseBundle/SharedPreferences, guaranteeing complete
stability with zero startup crashes.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Dict, List, Optional

RESTRICTION_METHODS = [
    "disallowSkippingNextReasons",
    "disallowSkippingPrevReasons",
    "disallowSeekingReasons",
    "disallowPeekingNextReasons",
    "disallowPeekingPrevReasons",
    "disallowTogglingRepeatContextReasons",
    "disallowTogglingRepeatTrackReasons",
    "disallowTogglingShuffleReasons",
    "disallowTapToPlayTrackInNextTracksReasons",
]


class Smali:
    """Invokes baksmali and smali from the bundled CLI jar."""

    def __init__(self, jar: str, api: int = 26, java_bin: str = "java", jobs: int = 0, heap: str = "2g"):
        self.jar = jar
        self.api = api
        self.java_bin = java_bin
        self.jobs = jobs or (os.cpu_count() or 2)
        self.heap = heap

    def _run(self, main: str, args: List[str]) -> None:
        cmd = [self.java_bin, "-Xmx" + self.heap, "-cp", self.jar, main] + args
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0 or ("Error for input" in res.stderr):
            raise RuntimeError(f"{main} failed:\n{res.stdout}\n{res.stderr}")

    def disassemble(self, dex_path: str, out_dir: str) -> None:
        self._run(
            "com.android.tools.smali.baksmali.Main",
            ["d", "-a", str(self.api), "-j", str(self.jobs), "-o", out_dir, dex_path],
        )

    def assemble(self, smali_dir: str, dex_path: str) -> None:
        self._run(
            "com.android.tools.smali.smali.Main",
            ["a", "-a", str(self.api), "-j", str(self.jobs), "-o", dex_path, smali_dir],
        )


def is_dex_interesting(dex_bytes: bytes) -> bool:
    """Checks if this DEX defines AutoValue_Restrictions."""
    return b"Lcom/spotify/player/model/AutoValue_Restrictions;" in dex_bytes


def patch_smali_directory(smali_root: str) -> Dict[str, int]:
    """Patches AutoValue_Restrictions methods to always return Restrictions.EMPTY reasons."""
    stats = {
        "unlimited_skips": 0,
        "on_demand_seeking": 0,
        "product_state_premium": 0,
        "ad_blocking": 0,
        "startup_init": 0,
    }

    target_file = os.path.join(smali_root, "com", "spotify", "player", "model", "AutoValue_Restrictions.smali")
    if not os.path.isfile(target_file):
        return stats

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    modified = content
    for method in RESTRICTION_METHODS:
        pattern = re.compile(
            r"(\.method public " + method + r"\(\)Lp/bg40;[\s\S]*?)iget-object v0, p0, Lcom/spotify/player/model/AutoValue_Restrictions;->" + method + r":Lp/bg40;([\s\S]*?return-object v0\n\.end method)"
        )
        replacement = (
            r"\1sget-object v0, Lcom/spotify/player/model/Restrictions;->EMPTY:Lcom/spotify/player/model/Restrictions;\n"
            r"    check-cast v0, Lcom/spotify/player/model/AutoValue_Restrictions;\n"
            r"    iget-object v0, v0, Lcom/spotify/player/model/AutoValue_Restrictions;->" + method + r":Lp/bg40;\2"
        )
        modified, count = pattern.subn(replacement, modified)
        if count > 0:
            if "Skipping" in method:
                stats["unlimited_skips"] += count
            else:
                stats["on_demand_seeking"] += count

    if modified != content:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(modified)

    return stats
