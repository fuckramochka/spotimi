"""Toolchain for Spoti Mi.

Finds and coordinates JDK 17+, R8/D8, android.jar, and apksigner.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from typing import List, Optional

R8_JAR_URL = "https://dl.google.com/dl/android/maven2/com/android/tools/r8/8.7.18/r8-8.7.18.jar"
PLATFORM_ZIP = "https://dl.google.com/android/repository/platform-35_r02.zip"
PLATFORM_MEMBER = "android-35/android.jar"
SIGNER_JAR_URL = (
    "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/"
    "uber-apk-signer-1.3.0.jar"
)


class Toolchain:
    def __init__(self, directory: str, quiet: bool = False):
        self.directory = os.path.abspath(directory)
        self.quiet = quiet
        os.makedirs(self.directory, exist_ok=True)
        self._java_bin = self._find_java()
        self._javac_bin = self._find_javac()
        self._keytool_bin = self._find_keytool()
        self._apksigner_bin = self._find_apksigner()

    def _say(self, msg: str) -> None:
        if not self.quiet:
            print(msg)

    def _find_java(self) -> str:
        # Check standard PATH
        found = shutil.which("java")
        if found:
            return found
        # Check Gradle JDKs
        candidates = glob.glob(os.path.expanduser("~/.gradle/jdks/*/bin/java"))
        if candidates:
            return sorted(candidates)[-1]
        # Check Android Studio / SDK
        sdk_candidates = glob.glob(os.path.expanduser("~/android-sdk/jbr/bin/java"))
        if sdk_candidates:
            return sdk_candidates[0]
        return "java"

    def _find_javac(self) -> str:
        found = shutil.which("javac")
        if found:
            return found
        java_dir = os.path.dirname(self._java_bin)
        beside = os.path.join(java_dir, "javac")
        if os.path.isfile(beside):
            return beside
        candidates = glob.glob(os.path.expanduser("~/.gradle/jdks/*/bin/javac"))
        if candidates:
            return sorted(candidates)[-1]
        return "javac"

    def _find_keytool(self) -> str:
        found = shutil.which("keytool")
        if found:
            return found
        java_dir = os.path.dirname(self._java_bin)
        beside = os.path.join(java_dir, "keytool")
        if os.path.isfile(beside):
            return beside
        candidates = glob.glob(os.path.expanduser("~/.gradle/jdks/*/bin/keytool"))
        if candidates:
            return sorted(candidates)[-1]
        return "keytool"

    def _find_apksigner(self) -> Optional[str]:
        candidates = glob.glob(os.path.expanduser("~/android-sdk/build-tools/*/lib/apksigner.jar"))
        if candidates:
            return sorted(candidates)[-1]
        found = shutil.which("apksigner")
        if found:
            return found
        return None

    def _fetch(self, url: str, name: str) -> str:
        path = os.path.join(self.directory, name)
        if os.path.exists(path):
            return path
        self._say(f"  fetching {name}...")
        temp = path + ".part"
        with urllib.request.urlopen(url) as resp, open(temp, "wb") as out:
            shutil.copyfileobj(resp, out)
        os.replace(temp, path)
        return path

    @property
    def r8(self) -> str:
        # Check if local symlink/file exists
        local = os.path.join(self.directory, "r8.jar")
        if os.path.isfile(local):
            return local
        # Check TikTokMi tools
        other = os.path.expanduser("~/TikTokMi/tools/r8.jar")
        if os.path.isfile(other):
            os.symlink(other, local)
            return local
        return self._fetch(R8_JAR_URL, "r8.jar")

    @property
    def android_jar(self) -> str:
        local = os.path.join(self.directory, "android.jar")
        if os.path.isfile(local):
            return local
        other = os.path.expanduser("~/TikTokMi/tools/android.jar")
        if os.path.isfile(other):
            os.symlink(other, local)
            return local
        archive = self._fetch(PLATFORM_ZIP, "platform.zip")
        self._say("  extracting android.jar...")
        with zipfile.ZipFile(archive) as zf, open(local, "wb") as out:
            shutil.copyfileobj(zf.open(PLATFORM_MEMBER), out)
        os.remove(archive)
        return local

    @property
    def signer(self) -> str:
        local = os.path.join(self.directory, "uber-apk-signer.jar")
        if os.path.isfile(local):
            return local
        return self._fetch(SIGNER_JAR_URL, "uber-apk-signer.jar")

    def compile_java_to_dex(
        self,
        java_sources: List[str],
        out_dir: str,
        min_api: int = 26,
    ) -> str:
        """Compiles Java sources into classes.dex via javac and D8."""
        os.makedirs(out_dir, exist_ok=True)
        classes_dir = os.path.join(out_dir, "classes")
        os.makedirs(classes_dir, exist_ok=True)

        # 1. javac
        javac_cmd = [
            self._javac_bin,
            "-encoding", "UTF-8",
            "-cp", self.android_jar,
            "-d", classes_dir,
        ] + java_sources
        self._run(javac_cmd)

        # 2. Package classes into temporary jar
        classes_jar = os.path.join(out_dir, "compiled_mod.jar")
        with zipfile.ZipFile(classes_jar, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(classes_dir):
                for f in files:
                    if f.endswith(".class"):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, classes_dir).replace(os.sep, "/")
                        zf.write(abs_p, rel_p)

        # 3. D8
        dex_out_dir = os.path.join(out_dir, "dex")
        os.makedirs(dex_out_dir, exist_ok=True)
        d8_cmd = [
            self._java_bin,
            "-cp", self.r8,
            "com.android.tools.r8.D8",
            "--release",
            "--min-api", str(min_api),
            "--lib", self.android_jar,
            "--output", dex_out_dir,
            classes_jar,
        ]
        self._run(d8_cmd)

        out_dex = os.path.join(dex_out_dir, "classes.dex")
        if not os.path.isfile(out_dex):
            raise RuntimeError(f"D8 did not produce classes.dex in {dex_out_dir}")
        return out_dex

    def sign(self, apk_path: str, keystore: Optional[str] = None) -> None:
        """Signs the APK using apksigner or debug key."""
        keystore_path = keystore or os.path.join(self.directory, "debug.keystore")
        if not os.path.isfile(keystore_path):
            self._say("  generating debug keystore...")
            gen_cmd = [
                self._keytool_bin,
                "-genkeypair",
                "-v",
                "-keystore", keystore_path,
                "-storepass", "android",
                "-alias", "androiddebugkey",
                "-keypass", "android",
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=SpotiMi,OU=Kawaii,O=SpotiMi,C=UA",
            ]
            self._run(gen_cmd)

        if self._apksigner_bin and os.path.isfile(self._apksigner_bin):
            if self._apksigner_bin.endswith(".jar"):
                sign_cmd = [
                    self._java_bin,
                    "-jar", self._apksigner_bin,
                    "sign",
                    "--ks", keystore_path,
                    "--ks-pass", "pass:android",
                    "--ks-key-alias", "androiddebugkey",
                    "--key-pass", "pass:android",
                    apk_path,
                ]
            else:
                sign_cmd = [
                    self._apksigner_bin,
                    "sign",
                    "--ks", keystore_path,
                    "--ks-pass", "pass:android",
                    "--ks-key-alias", "androiddebugkey",
                    "--key-pass", "pass:android",
                    apk_path,
                ]
            self._run(sign_cmd)
        else:
            signer_jar = self.signer
            sign_cmd = [
                self._java_bin,
                "-jar", signer_jar,
                "-a", apk_path,
                "--allowResign",
                "--overwrite",
                "--ks", keystore_path,
                "--ksAlias", "androiddebugkey",
                "--ksPass", "android",
                "--ksKeyPass", "android",
            ]
            self._run(sign_cmd)

    def _run(self, cmd: List[str]) -> None:
        env = dict(os.environ)
        java_dir = os.path.dirname(self._java_bin)
        env["PATH"] = java_dir + os.pathsep + env.get("PATH", "")
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if res.returncode != 0:
            sys.stderr.write(res.stdout + res.stderr)
            raise RuntimeError(f"Command failed: {os.path.basename(cmd[0])}")
