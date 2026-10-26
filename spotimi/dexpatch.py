"""Bytecode patcher for Spoti Mi.

Disassembles only DEX files containing relevant Spotify signatures (PlayerRestrictions,
ProductState, Ads, MainActivity), performs exact regex-based smali opcode rewrites,
and reassembles them using Smali/Baksmali.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

HOOK_PLAYER = "Lmi/spotimi/PlayerHooks;"
HOOK_PRODUCT = "Lmi/spotimi/ProductStateHooks;"
HOOK_AD = "Lmi/spotimi/AdBlocker;"
HOOK_CORE = "Lmi/spotimi/SpotiMi;"
HOOK_UI = "Lmi/spotimi/ui/ViewCleaner;"

# Signatures to identify candidate DEX files
INTERESTING_STRINGS = [
    b"disallowSkippingNextReasons",
    b"disallowSeekingReasons",
    b"streaming-rules",
    b"canvaz.enabled",
    b"lyrics.feature-enabled",
    b"com/spotify/music/MainActivity",
    b"com/spotify/music/SpotifyApplication",
    b"spotify:ad:",
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
        if res.returncode != 0:
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
    """Checks if a DEX file contains any target Spotify symbols."""
    for s in INTERESTING_STRINGS:
        if s in dex_bytes:
            return True
    return False


def patch_smali_directory(smali_root: str) -> Dict[str, int]:
    """Walks disassembled smali files and applies surgical bytecode redirects."""
    stats = {
        "unlimited_skips": 0,
        "on_demand_seeking": 0,
        "product_state_premium": 0,
        "ad_blocking": 0,
        "startup_init": 0,
    }

    re_skip_next = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowSkippingNextReasons\(\)Ljava/util/Set;"
    )
    re_skip_prev = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowSkippingPrevReasons\(\)Ljava/util/Set;"
    )
    re_seek = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowSeekingReasons\(\)Ljava/util/Set;"
    )
    re_repeat_track = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowRepeatingTrackReasons\(\)Ljava/util/Set;"
    )
    re_repeat_context = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowRepeatingContextReasons\(\)Ljava/util/Set;"
    )
    re_peek_next = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^}]+)\},\s*L[^;]+;->disallowPeekingNextReasons\(\)Ljava/util/Set;"
    )

    re_prod_get2 = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^,]+),\s*([^,]+),\s*([^}]+)\},\s*L[^;]+;->get\(Ljava/lang/String;Ljava/lang/String;\)Ljava/lang/String;"
    )
    re_prod_bool = re.compile(
        r"invoke-(?:virtual|interface)\s*\{([^,]+),\s*([^,]+),\s*([^}]+)\},\s*L[^;]+;->getBoolean\(Ljava/lang/String;Z\)Z"
    )

    re_main_activity = re.compile(
        r"(\.method protected onCreate\(Landroid/os/Bundle;\)V[\s\S]*?invoke-super \{[^\}]+\}, L[^\;]+;->onCreate\(Landroid/os/Bundle;\)V)"
    )

    for dirpath, _, filenames in os.walk(smali_root):
        for fname in filenames:
            if not fname.endswith(".smali"):
                continue

            path = os.path.join(dirpath, fname)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            modified = content

            # 1. Unlimited Skips
            if "disallowSkippingNextReasons" in modified:
                modified, count = re_skip_next.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowSkippingNextReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["unlimited_skips"] += count

            if "disallowSkippingPrevReasons" in modified:
                modified, count = re_skip_prev.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowSkippingPrevReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["unlimited_skips"] += count

            # 2. Free Seeking & Repeat & On-Demand
            if "disallowSeekingReasons" in modified:
                modified, count = re_seek.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowSeekingReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["on_demand_seeking"] += count

            if "disallowRepeatingTrackReasons" in modified:
                modified, count = re_repeat_track.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowRepeatingTrackReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["on_demand_seeking"] += count

            if "disallowRepeatingContextReasons" in modified:
                modified, count = re_repeat_context.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowRepeatingContextReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["on_demand_seeking"] += count

            if "disallowPeekingNextReasons" in modified:
                modified, count = re_peek_next.subn(
                    f"invoke-static {{\\1}}, {HOOK_PLAYER}->getDisallowPeekingNextReasons(Ljava/lang/Object;)Ljava/util/Set;",
                    modified,
                )
                stats["on_demand_seeking"] += count

            # 3. ProductState Hooks (Premium status & rules)
            if "->get(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in modified:
                modified, count = re_prod_get2.subn(
                    f"invoke-static {{\\1, \\2, \\3}}, {HOOK_PRODUCT}->get(Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                    modified,
                )
                stats["product_state_premium"] += count

            if "->getBoolean(Ljava/lang/String;Z)Z" in modified:
                modified, count = re_prod_bool.subn(
                    f"invoke-static {{\\1, \\2, \\3}}, {HOOK_PRODUCT}->getBoolean(Ljava/lang/Object;Ljava/lang/String;Z)Z;",
                    modified,
                )
                stats["product_state_premium"] += count

            # 4. Startup Init Hook in MainActivity
            if "MainActivity" in fname and "onCreate(Landroid/os/Bundle;)V" in modified:
                if "SpotiMi;->init" not in modified:
                    modified, count = re_main_activity.subn(
                        f"\\1\n    invoke-static {{p0}}, {HOOK_CORE}->init(Landroid/content/Context;)V",
                        modified,
                    )
                    stats["startup_init"] += count

            if modified != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(modified)

    return stats
