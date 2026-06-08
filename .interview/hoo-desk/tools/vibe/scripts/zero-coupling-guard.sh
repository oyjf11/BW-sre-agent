#!/usr/bin/env bash
# Fails if business-specific words leak into the toolchain core (adapters excluded).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HITS=$(grep -rniE 'hoo-desk|isForget|\blogin\b' "$ROOT/src" --include='*.ts' \
  | grep -v '/adapters/' || true)
if [ -n "$HITS" ]; then
  echo "❌ zero-coupling violation: business words found in tools/vibe/src:"
  echo "$HITS"
  exit 1
fi
echo "✅ zero-coupling guard passed"
