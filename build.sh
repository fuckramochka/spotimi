#!/usr/bin/env bash
# Build Spoti Mi from an official Spotify apk.
#
#   ./build.sh path/to/spotify.apk
#   ./build.sh path/to/spotify.apk --accent gothic_kawaii_pink
#
# Requires: Python 3 and Java 17+ (or ~/.gradle JDKs)

set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m spotimi "$@"
