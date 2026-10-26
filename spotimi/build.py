"""The Spoti Mi build engine.

Orchestrates the complete transformation of an official Spotify APK into Spoti Mi:
1. Fast streaming zip inspection & signature stripping
2. Baking Gothic Accent into resources.arsc, AXML drawables, Lottie JSON, and PNGs
3. Full Dalvik/Compose token & hex string recoloring across all DEX files
4. Compiling injected Java mod classes (Updater, Settings, Hooks) to DEX via D8
5. Surgical bytecode patching of classes2.dex (Player Restrictions & MainActivity hook)
6. Repackaging and signing with Android V2/V3 signature
"""

from __future__ import annotations

import glob
import os
import shutil
import tempfile
import time
from typing import Dict, List, Optional

from . import accent, dexpatch, dexrecolour, palette
from .apkzip import Apk
from .arsc import Arsc
from .toolchain import Toolchain


def build(
    apk_in: str,
    apk_out: str,
    accent_hex: int = palette.DEFAULT_ACCENT_HEX,
    tools_dir: str = "tools",
    quiet: bool = False,
) -> None:
    start_time = time.time()

    def log(msg: str) -> None:
        if not quiet:
            print(msg)

    log(f"\n🌸 [Spoti Mi] Starting build from: {os.path.basename(apk_in)}")
    log(f"   Target accent: #{accent_hex:06X} (Gothic Blood Rose)")

    if not os.path.isfile(apk_in):
        raise FileNotFoundError(f"Input APK not found: {apk_in}")

    toolchain = Toolchain(tools_dir, quiet=quiet)
    smali_tool = dexpatch.Smali(
        jar=os.path.abspath(os.path.join(tools_dir, "smali.jar")),
        api=26,
        java_bin=toolchain._java_bin,
    )

    with tempfile.TemporaryDirectory(prefix="spotimi-build-") as work_dir:
        # 1. Unpack APK into memory / work streaming
        log("📦 Reading APK package entries...")
        apk = Apk(apk_in)
        dropped = apk.drop_signature()
        if dropped:
            log(f"   • Removed original signatures ({len(dropped)} entries)")

        # 2. Accent Baking in ARSC, AXML, Lottie JSON, and PNG drawables
        log("🎨 Repainting Spotify Green -> Gothic Accent in ARSC, XML, Lottie, and PNGs...")
        if "resources.arsc" in apk.names():
            arsc_data = apk.read("resources.arsc")
            arsc = Arsc(arsc_data)
            pairs: Dict[int, int] = {}
            reports = accent.bake(apk, arsc, old=palette.REFERENCE_HEX, new=accent_hex, pairs=pairs)
            for r in reports:
                log(f"   • {r}")
            apk.replace("resources.arsc", arsc.build())

        # 3. Find all DEX files in original APK
        dex_names = sorted([n for n in apk.names() if n.startswith("classes") and n.endswith(".dex")])
        log(f"🔍 Inspecting {len(dex_names)} DEX files in original APK")

        # 4. Full Dalvik/Compose token & hex string recoloring across all DEX files
        log("🔮 Scanning and recoloring Dalvik bytecode tokens & Jetpack Compose constants...")
        total_dex_recoloured = 0
        for dname in dex_names:
            dex_bytes = apk.read(dname)
            new_dex, rec_count = dexrecolour.recolour_dex_bytes(
                dex_bytes, old_hex=palette.REFERENCE_HEX, new_hex=accent_hex
            )
            if rec_count > 0:
                apk.replace(dname, new_dex)
                total_dex_recoloured += rec_count
        log(f"   • Replaced {total_dex_recoloured} Dalvik/Compose green tokens across DEX files")

        # 5. Compile injected Java classes into a new DEX file
        inject_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inject", "java")
        java_sources = glob.glob(os.path.join(inject_dir, "**", "*.java"), recursive=True)
        if java_sources:
            log(f"☕ Compiling {len(java_sources)} injected Spoti Mi Java sources...")
            mod_dex_path = toolchain.compile_java_to_dex(java_sources, work_dir)
            next_idx = len(dex_names) + 1
            mod_dex_name = f"classes{next_idx}.dex"
            with open(mod_dex_path, "rb") as f:
                apk.add(mod_dex_name, f.read())
            log(f"   • Injected mod DEX as {mod_dex_name} ({os.path.getsize(mod_dex_path)} bytes)")

        # 6. Surgical Smali patch for classes2.dex (Restrictions + MainActivity hook)
        for dname in dex_names:
            dex_bytes = apk.read(dname)
            if dexpatch.is_dex_interesting(dex_bytes):
                log(f"   🔧 Disassembling and patching {dname} (AutoValue_Restrictions & MainActivity)...")
                dex_file = os.path.join(work_dir, dname)
                with open(dex_file, "wb") as f:
                    f.write(dex_bytes)

                smali_dir = os.path.join(work_dir, f"smali_{dname}")
                smali_tool.disassemble(dex_file, smali_dir)

                stats = dexpatch.patch_smali_directory(smali_dir)
                total_patches = sum(stats.values())
                if total_patches > 0:
                    log(f"      - Skips: {stats['unlimited_skips']}, Seek/Repeat/On-Demand: {stats['on_demand_seeking']}, MainActivity hook: {stats['main_activity_hook']}")
                    smali_tool.assemble(smali_dir, dex_file)
                    with open(dex_file, "rb") as f:
                        apk.replace(dname, f.read())
                else:
                    log("      - No rewrite points in this DEX, skipping assembly")

        # 7. Write out patched APK
        log(f"💾 Saving patched APK to: {apk_out}...")
        os.makedirs(os.path.dirname(os.path.abspath(apk_out)), exist_ok=True)
        apk.write(apk_out)
        apk.close()

        # 8. Sign APK with Android V2/V3 signatures
        log("✍️  Signing APK with Android V2/V3 signature...")
        toolchain.sign(apk_out)

    elapsed = time.time() - start_time
    log(f"✨ [Spoti Mi] Build complete in {elapsed:.1f}s! File ready: {apk_out}\n")
