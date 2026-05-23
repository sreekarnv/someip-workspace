#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/export-openapi.sh"
pnpm --dir "$ROOT/services/web" run generate:api
