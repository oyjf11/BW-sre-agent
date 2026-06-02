#!/usr/bin/env bash
set -euo pipefail

if [ -f package.json ]; then
  echo "== package scripts =="
  node -e "const p=require('./package.json'); console.log(p.scripts||{})"
fi

if command -v pnpm >/dev/null 2>&1; then
  pnpm lint || true
  pnpm typecheck || true
  pnpm test || true
  pnpm build || true
elif command -v npm >/dev/null 2>&1; then
  npm run lint --if-present || true
  npm run typecheck --if-present || true
  npm test --if-present || true
  npm run build --if-present || true
else
  echo "No pnpm/npm found."
fi
