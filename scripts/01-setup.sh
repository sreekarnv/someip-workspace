#!/bin/bash
# 01-setup.sh - Install system dependencies and clone library submodules
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Installing system dependencies ==="
sudo apt-get update -qq
sudo apt-get install -y -qq cmake g++ libboost-all-dev pkg-config python3 python3-pip python3-venv

echo "=== Installing Python dependencies ==="
cd "$ROOT/services/api"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true

echo "=== Cloning library sources ==="
mkdir -p "$ROOT/libs"
cd "$ROOT/libs"

clone_if_missing() {
  local url="$1"
  local dir="$2"
  local branch="${3:-master}"
  if [ ! -d "$dir/.git" ] && [ ! -d "$dir/src" ]; then
    echo "Cloning $dir..."
    git clone --depth 1 --branch "$branch" "$url" "$dir"
  else
    echo "$dir already present, skipping"
  fi
}

clone_if_missing "https://github.com/COVESA/vsomeip.git" "vsomeip" "master"
clone_if_missing "https://github.com/COVESA/capicxx-core-runtime.git" "capicxx-core-runtime" "master"
clone_if_missing "https://github.com/COVESA/capicxx-someip-runtime.git" "capicxx-someip-runtime" "master"

echo "=== Setup complete ==="
cmake --version | head -1
g++ --version | head -1
