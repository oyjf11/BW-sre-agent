---
description: 构建当前任务 context pack，提取关键信息而非复制大段源码。
agent: plan
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请执行以下步骤，构建 context pack：

1. 运行 `.vibe-workflow/scripts/vibe-build-context.sh` 生成初始 context-pack.md
2. 审阅生成的内容，补齐脚本未能提取的关键信息：
   - 核心需求（300 字内）
   - 关键设计决策（选择 + 理由）
   - 受影响的文件路径（不复制源码）
   - 禁止触碰的文件列表
   - 当前阻塞和下一步
3. 不要复制大段源码到 context pack 中，只引用文件路径
4. 输出最终 context pack 到 `.vibe-workflow/tasks/<task-dir>/context-pack.md`

$ARGUMENTS
