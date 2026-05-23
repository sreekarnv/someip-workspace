#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/services/api/openapi/v1.json"

mkdir -p "$(dirname "$OUT")"
PYTHONPATH="$ROOT/services/api" python3 - <<'PY' > "$OUT"
import json
from main import app

print(json.dumps(app.openapi(), indent=2))
PY

echo "Exported $OUT"
