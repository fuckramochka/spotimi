import os
import shutil
import tempfile
import unittest

from spotimi import dexpatch, palette
from spotimi.toolchain import Toolchain


class TestPalette(unittest.TestCase):
    def test_spotify_green_mapping(self):
        # Spotify Green #1DB954
        stock = 0xFF1DB954
        self.assertTrue(palette.captures(stock, palette.REFERENCE_HEX))

        mapped = palette.map_colour(stock, palette.REFERENCE_HEX, palette.DEFAULT_ACCENT_HEX)
        # Should be Gothic Blood Rose #B81B34 (Red=184, Green=27, Blue=52)
        alpha = (mapped >> 24) & 0xFF
        red = (mapped >> 16) & 0xFF
        green = (mapped >> 8) & 0xFF
        blue = mapped & 0xFF

        self.assertEqual(alpha, 0xFF)
        self.assertEqual(red, 0xB8)
        self.assertEqual(green, 0x1B)
        self.assertEqual(blue, 0x34)

    def test_neutrals_preserved(self):
        # Pure white, black, grey should not be repainted
        for neutral in (0xFFFFFFFF, 0xFF000000, 0xFF888888, 0xFF121212):
            self.assertFalse(palette.captures(neutral, palette.REFERENCE_HEX))
            self.assertEqual(palette.map_colour(neutral), neutral)

    def test_alpha_kept(self):
        # 50% opacity Spotify Green
        semi = 0x801DB954
        mapped = palette.map_colour(semi, palette.REFERENCE_HEX, palette.DEFAULT_ACCENT_HEX)
        self.assertEqual((mapped >> 24) & 0xFF, 0x80)


class TestDexPatch(unittest.TestCase):
    def test_is_dex_interesting(self):
        sample_dex = b"header...Lcom/spotify/player/model/AutoValue_Restrictions;...tail"
        self.assertTrue(dexpatch.is_dex_interesting(sample_dex))

        boring_dex = b"header...nothing_relevant...tail"
        self.assertFalse(dexpatch.is_dex_interesting(boring_dex))

    def test_smali_rewrite(self):
        sample_smali = """
.class public Lcom/spotify/player/model/AutoValue_Restrictions;
.super Lcom/spotify/player/model/Restrictions;

.method public disallowSkippingNextReasons()Lp/bg40;
    .registers 2
    iget-object v0, p0, Lcom/spotify/player/model/AutoValue_Restrictions;->disallowSkippingNextReasons:Lp/bg40;
    return-object v0
.end method

.method public disallowSeekingReasons()Lp/bg40;
    .registers 2
    iget-object v0, p0, Lcom/spotify/player/model/AutoValue_Restrictions;->disallowSeekingReasons:Lp/bg40;
    return-object v0
.end method
"""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = os.path.join(tmp, "com", "spotify", "player", "model")
            os.makedirs(pkg_dir)
            fpath = os.path.join(pkg_dir, "AutoValue_Restrictions.smali")
            with open(fpath, "w") as f:
                f.write(sample_smali)

            stats = dexpatch.patch_smali_directory(tmp)
            self.assertEqual(stats["unlimited_skips"], 1)
            self.assertEqual(stats["on_demand_seeking"], 1)

            with open(fpath, "r") as f:
                patched = f.read()

            self.assertIn("sget-object v0, Lcom/spotify/player/model/Restrictions;->EMPTY", patched)


class TestToolchainJava(unittest.TestCase):
    def test_java_compiles_cleanly(self):
        toolchain = Toolchain("tools", quiet=True)
        inject_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "inject", "java"))
        java_files = []
        for root, _, files in os.walk(inject_dir):
            for f in files:
                if f.endswith(".java"):
                    java_files.append(os.path.join(root, f))

        self.assertTrue(len(java_files) > 0)
        with tempfile.TemporaryDirectory() as tmp:
            dex_path = toolchain.compile_java_to_dex(java_files, tmp, min_api=26)
            self.assertTrue(os.path.isfile(dex_path))
            self.assertTrue(os.path.getsize(dex_path) > 1000)


class TestDexRecolour(unittest.TestCase):
    def test_recolour_dex_literals_and_strings(self):
        from spotimi.dexrecolour import recolour_dex_bytes, fix_dex_checksums
        import struct

        # Create dummy DEX header (112 bytes) + bytecode
        header = bytearray(112)
        header[0:8] = b"dex\n039\x00"

        # Bytecode with const v0, 0xff1db954 (14 00 54 b9 1d ff)
        # and const-wide/32 v1, 0xff1ed760 (18 01 60 d7 1e ff)
        # and raw string "1ED760"
        payload = bytearray()
        payload += b"\x14\x00\x54\xb9\x1d\xff"
        payload += b"\x18\x01\x60\xd7\x1e\xff"
        payload += b"Hello 1ED760 World"

        full_dex = fix_dex_checksums(header + payload)
        recoloured, count = recolour_dex_bytes(full_dex)

        self.assertGreaterEqual(count, 3)
        self.assertNotIn(b"\x54\xb9\x1d\xff", recoloured)
        self.assertNotIn(b"\x60\xd7\x1e\xff", recoloured)
        self.assertNotIn(b"1ED760", recoloured)


if __name__ == "__main__":
    unittest.main()
