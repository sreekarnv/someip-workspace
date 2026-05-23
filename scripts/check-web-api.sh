#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/generate-web-api.sh"

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$ROOT" diff --exit-code -- services/api/openapi/v1.json services/web/src/generated
else
    echo "Generated OpenAPI web artifacts. Skipping git staleness diff outside a git worktree."
fi
