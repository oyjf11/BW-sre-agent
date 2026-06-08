#!/usr/bin/env bash

# --- 1. 寻找“真” Node (兼容 Windows) ---
resolve_node() {
    if command -v node.exe >/dev/null 2>&1; then echo "node.exe"; return; fi
    if command -v node >/dev/null 2>&1; then echo "node"; return; fi
    echo "ERROR_NO_NODE"
}
REAL_NODE="$(resolve_node)"

if [ "$REAL_NODE" == "ERROR_NO_NODE" ]; then
    echo "❌ [System Error] Critical: No compatible Node.js found."
    exit 1
fi

# --- 2. 路径解析 ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT_REL="./.opencode/skill/task-management/scripts/task-cli.cts" 

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

# --- 3. 寻找 ts-node 源码 ---
TS_NODE_ENTRY="./node_modules/ts-node/dist/bin.js"
if [ ! -f "$TS_NODE_ENTRY" ]; then
    echo "⚠️ Local ts-node not found. Auto-installing..."
    npm install -D ts-node typescript @types/node >/dev/null 2>&1
fi

# --- 4. 强制覆盖 Vite 配置 ---
TS_OPTS='{"module":"commonjs","moduleResolution":"node","esModuleInterop":true,"skipLibCheck":true}'

echo "📂 Context: $PROJECT_ROOT"
echo "🔧 Engine:  $($REAL_NODE -v) (via $REAL_NODE)"
echo "----------------------------------------"

# --- 5. 劫持执行 ---
"$REAL_NODE" "$TS_NODE_ENTRY" --compiler-options "$TS_OPTS" --transpile-only "$CLI_SCRIPT_REL" "$@"

EXIT_CODE=$?
echo "----------------------------------------"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ [SUCCESS] Command executed."
else
    echo "❌ [FAILURE] Exit code $EXIT_CODE"
    exit $EXIT_CODE
fi