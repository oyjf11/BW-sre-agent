#!/usr/bin/env bash
set -euo pipefail

if [ -f package.json ]; then
  if command -v pnpm >/dev/null 2>&1; then
    pnpm exec playwright test "$@"
  else
    npx playwright test "$@"
  fi
else
  echo "package.json not found. Run this from project root."
  exit 1
fi
