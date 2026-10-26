"""The Spoti Mi build engine.

Orchestrates the transformation of an official Spotify APK into Spoti Mi:
1. Fast streaming zip inspection
2. Baking Gothic Kawaii Pink (#FF2A85) into resources.arsc and binary XMLs
3. Compiling Java injected mod classes to DEX via D8
4. Surgical bytecode patching of DEX files with Baksmali/Smali
5. Injecting classes.dex and signing with debug keystore
"""

from __future__ import annotations

import glob
import os
import shutil
import tempfile
import time
from typing import Dict, List, Optional

from . import accent, dexpatch, palette
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
    log(f"   Target accent: #{accent_hex:06X} (Gothic Kawaii Pink)")

    if not os.path.isfile(apk_in):
        raise FileNotFoundError(f"Input APK not found: {apk_in}")

    toolchain = Toolchain(tools_dir, quiet=quiet)
    smali_tool = dexpatch.Smali(
        jar=os.path.join(tools_dir, "smali.jar"),
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

        # 2. Accent Baking in ARSC and Vector Drawables
        log("🎨 Repainting Spotify Green -> Gothic Kawaii Pink in ARSC and XML drawables...")
        if "resources.arsc" in apk.names():
            arsc_data = apk.read("resources.arsc")
            arsc = Arsc(arsc_data)
            pairs: Dict[int, int] = {}
            reports = accent.bake(apk, arsc, old=palette.REFERENCE_HEX, new=accent_hex, pairs=pairs)
            for r in reports:
                log(f"   • {r}")
            apk.replace("resources.arsc", arsc.build())

        # 3. Compile Java Injected Classes
        log("⚙️  Compiling Spoti Mi injected Java modules...")
        inject_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "inject", "java")
        )
        java_files = []
        for root, _, files in os.walk(inject_dir):
            for f in files:
                if f.endswith(".java"):
                    java_files.append(os.path.join(root, f))

        compile_dir = os.path.join(work_dir, "compile")
        mod_dex = toolchain.compile_java_to_dex(java_files, compile_dir, min_api=26)
        log("   • Mod classes compiled into DEX successfully")

        # 4. Find all DEX files in the APK
        dex_names = sorted([n for n in apk.names() if n.startswith("classes") and n.endswith(".dex")])
        log(f"🔍 Found {len(dex_names)} DEX files in original APK")

        # 5. Patch target DEX files
        patched_count = 0
        for dname in dex_names:
            dex_bytes = apk.read(dname)
            if dexpatch.is_dex_interesting(dex_bytes):
                log(f"   🔧 Disassembling and patching {dname}...")
                dex_file = os.path.join(work_dir, dname)
                with open(dex_file, "wb") as f:
                    f.write(dex_bytes)

                smali_dir = os.path.join(work_dir, f"smali_{dname}")
                smali_tool.disassemble(dex_file, smali_dir)

                stats = dexpatch.patch_smali_directory(smali_dir)
                total_patches = sum(stats.values())
                if total_patches > 0:
                    log(f"      - Skips: {stats['unlimited_skips']}, Seek/Repeat: {stats['on_demand_seeking']}, Flags: {stats['product_state_premium']}, Init: {stats['startup_init']}")
                    smali_tool.assemble(smali_dir, dex_file)
                    with open(dex_file, "rb") as f:
                        apk.replace(dname, f.read())
                    patched_count += 1
                else:
                    log("      - No rewrite points in this DEX, skipping assembly")

        # 6. Add Spoti Mi DEX as next classes{N}.dex
        next_dex_num = len(dex_names) + 1
        new_dex_name = f"classes{next_dex_num}.dex" if next_dex_num > 1 else "classes.dex"
        log(f"➕ Appending Spoti Mi engine as {new_dex_name}...")
        with open(mod_dex, "rb") as f:
            dex_data = f.read()
        if apk.has(new_dex_name):
            apk.replace(new_dex_name, dex_data)
        else:
            apk.add(new_dex_name, dex_data)

        # 7. Write out unaligned/aligned APK
        log(f"💾 Saving patched APK to: {apk_out}...")
        os.makedirs(os.path.dirname(os.path.abspath(apk_out)), exist_ok=True)
        apk.write(apk_out)
        apk.close()

        # 8. Sign APK
        log("✍️  Signing APK with Android V2/V3 signature...")
        toolchain.sign(apk_out)

    elapsed = time.time() - start_time
    log(f"✨ [Spoti Mi] Build complete in {elapsed:.1f}s! File ready: {apk_out}\n")
