#!/bin/bash
# 03-download-generators.sh - Download pre-built CommonAPI generators
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools/generators"

mkdir -p "$TOOLS"
cd "$TOOLS"

echo "=== Downloading CommonAPI Core generator ==="
curl -L -o commonapi_core_generator.zip \
  "https://github.com/COVESA/capicxx-core-tools/releases/download/3.2.15/commonapi_core_generator.zip"

echo "=== Downloading CommonAPI SOME/IP generator ==="
curl -L -o commonapi_someip_generator.zip \
  "https://github.com/COVESA/capicxx-someip-tools/releases/download/3.2.15/commonapi_someip_generator.zip"

echo "=== Extracting generators ==="
unzip -o commonapi_core_generator.zip
unzip -o commonapi_someip_generator.zip

echo "=== Cleaning up zip files ==="
rm -f commonapi_core_generator.zip commonapi_someip_generator.zip

echo "=== Generators ready ==="
ls -la commonapi-core-generator-linux-x86_64
ls -la commonapi-someip-generator-linux-x86_64
