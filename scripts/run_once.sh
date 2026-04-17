#!/usr/bin/env bash
# Elite Research Pipeline — Run pipeline once
set -euo pipefail

echo "═══ Elite Research Pipeline — Running ═══"
echo

python3 -m pipeline "$@"
