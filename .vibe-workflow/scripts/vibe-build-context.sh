#!/usr/bin/env bash
set -euo pipefail

# vibe-build-context.sh — 为当前任务构建 context pack
# 用法: ./vibe-build-context.sh <task-dir>  或自动发现最近任务

TASK_DIR="${1:-}"
if [ -z "$TASK_DIR" ]; then
  TASK_DIR=$(ls -dt .vibe-workflow/tasks/20*/ 2>/dev/null | head -1)
  if [ -z "$TASK_DIR" ]; then
    echo "❌ 未找到任务目录。请先执行 vibe-new-task.sh"
    exit 1
  fi
fi

OUTPUT="$TASK_DIR/context-pack.md"
TASK_SLUG=$(basename "$TASK_DIR" | sed 's/^[0-9-]*//' | sed 's/^-//')
TIMESTAMP=$(date -Iseconds)

echo "==> 构建 context pack: $TASK_SLUG"

mkdir -p "$TASK_DIR"

cat > "$OUTPUT" <<HEADER
# Context Pack: ${TASK_SLUG}

> 生成时间: ${TIMESTAMP} | 生成方式: vibe-build-context.sh
> 原则：只含任务必要信息，不复制大段源码。引用路径即可。

## 1. 任务标识

| 字段 | 值 |
|------|-----|
| task_id | $(basename "$TASK_DIR") |
| slug | ${TASK_SLUG} |
| artifact_dir | ${TASK_DIR} |
HEADER

# --- 2. 需求摘要：从 01-requirements-clarification.md 提取 ---
if [ -f "$TASK_DIR/01-requirements-clarification.md" ]; then
  echo "" >> "$OUTPUT"
  echo "## 2. 需求摘要" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  # 提取目标区域（尽量短）
  awk '/^## 核心目标/,/^## /{if(NF>0)print}' "$TASK_DIR/01-requirements-clarification.md" | head -30 >> "$OUTPUT" 2>/dev/null || echo "_（无法提取）_" >> "$OUTPUT"
else
  echo "_（缺失: 01-requirements-clarification.md）_" >> "$OUTPUT"
fi

# --- 3. 受影响文件：从 03-detailed-design.md 提取 ---
echo "" >> "$OUTPUT"
echo "## 3. 受影响文件" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if [ -f "$TASK_DIR/03-detailed-design.md" ]; then
  echo "### 需修改" >> "$OUTPUT"
  grep -iE '^- .*(src/|lib/|app/|backend/|frontend/|\.ts|\.tsx|\.py|\.js|\.go)' "$TASK_DIR/03-detailed-design.md" 2>/dev/null | head -30 >> "$OUTPUT" || echo "_（未找到文件清单）_" >> "$OUTPUT"
else
  # 从 git diff 获取
  echo "### 需修改（来自 git diff）" >> "$OUTPUT"
  git diff --name-only HEAD 2>/dev/null | head -30 >> "$OUTPUT" || echo "_（无变更）_" >> "$OUTPUT"
fi

# --- 4. 当前状态 ---
echo "" >> "$OUTPUT"
echo "## 4. 当前状态" >> "$OUTPUT"
echo "" >> "$OUTPUT"

for f in "$TASK_DIR"/*.md; do
  [ -f "$f" ] || continue
  fname=$(basename "$f")
  size=$(wc -c < "$f" | tr -d ' ')
  if [ "$size" -gt 0 ]; then
    echo "- [x] $fname (${size} bytes)" >> "$OUTPUT"
  else
    echo "- [ ] $fname (空)" >> "$OUTPUT"
  fi
done

# --- 5. 关键约束 ---
echo "" >> "$OUTPUT"
echo "## 5. 关键约束" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if [ -f "$TASK_DIR/01-requirements-clarification.md" ]; then
  grep -iE '非目标|禁止|不得|约束' "$TASK_DIR/01-requirements-clarification.md" 2>/dev/null | head -10 | sed 's/^/- /' >> "$OUTPUT" || echo "_（未声明约束）_" >> "$OUTPUT"
fi

# --- 6. 风险备忘 ---
echo "" >> "$OUTPUT"
echo "## 6. 风险备忘" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if [ -f "$TASK_DIR/03-detailed-design.md" ]; then
  echo "| 风险 | 等级 | 缓解 |" >> "$OUTPUT"
  echo "|------|------|------|" >> "$OUTPUT"
  # 尝试从详细设计提取风险表
  awk '/风险/,/^## /{if(/^\|/ && !/风险/)print}' "$TASK_DIR/03-detailed-design.md" 2>/dev/null | head -10 >> "$OUTPUT" || echo "| _（未提取风险）_ |||" >> "$OUTPUT"
fi

# --- summary ---
echo ""
echo "✅ Context pack 已生成: $OUTPUT"
echo "   大小: $(wc -c < "$OUTPUT" | tr -d ' ') bytes"
