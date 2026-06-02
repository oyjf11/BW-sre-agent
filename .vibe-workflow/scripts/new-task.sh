#!/usr/bin/env bash
set -euo pipefail

slug="${1:-new-task}"
date="$(date +%F)"
dir=".vibe-workflow/tasks/${date}-${slug}"
mkdir -p "$dir"
cp .vibe-workflow/templates/*.md "$dir"/
echo "Created $dir"
