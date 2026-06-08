---
name: task-management
description: 任务管理工具。用于在项目中初始化任务清单、查看任务状态、领取下一任务、以及在每个步骤完成后强制标记完成并校验状态再继续。
---

#!/usr/bin/env bash

# Bootstrap: 路由代理（入口仅负责把执行交给 router.sh）
# 注意：真正的工作流约束在下方「Task Management Protocol」中定义

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTER_PATH="$SKILL_ROOT/router.sh"

if [ -f "$ROUTER_PATH" ]; then
  chmod +x "$ROUTER_PATH"
  "$ROUTER_PATH" "$@"
else
  echo "❌ Critical Error: router.sh not found"
  exit 1
fi
exit $?

################################################################################
# Task Management Protocol (For Agent)
################################################################################

## 0) CRITICAL：唯一合法调用方式（Git 根目录定位法）

你必须使用 Git 根目录定位法来调用此脚本（禁止相对路径猜测）：
`<PROJECT_ROOT>/.opencode/skill/task-management/router.sh <command>`

其中 `<PROJECT_ROOT>` 为项目根目录（执行 `git rev-parse --show-toplevel` 获取）

下文所有命令均默认采用该前缀。

---

## 1) CRITICAL：两条硬性“闸门规则”（Gating Rules）

### Rule A — 未初始化任务时，必须先初始化（强制）
在执行 `status / next / complete` 之前，你必须先判断任务系统是否已初始化。

**判定方法（强制顺序）：**
1. 先执行：`.../router.sh status`
2. 如果输出中出现任意一种“未初始化信号”（示例：`NOT_INITIALIZED` / `no tasks` / `missing task index` / `please run create` 等）
   - 你必须立刻执行：`.../router.sh create <feature> <name> <subtask1> [subtask2] ...`
   - 然后再次执行：`.../router.sh status`
   - 只有当 status 表明“已初始化”时，才允许进入后续动作

> 解释：任何后续命令都依赖初始化后的任务索引与状态文件；未初始化时继续执行等同于无效操作。

### Rule B — 每一步完成后，必须先“标记完成 + 校验状态”才能继续（强制）
当你完成某个任务（feature/seq）对应的工作后：

**强制动作链：**
1. `.../router.sh complete <feature> <seq> "<summary>"`
2. 立刻执行：`.../router.sh status`
3. 校验：该任务在 status 中已从 `TODO/IN_PROGRESS` 变为 `DONE/COMPLETED`
4. 只有校验通过后，才允许继续调用 `next` 领取下一任务

> 解释：这条规则用于防止“做完不落账/状态漂移”，确保任务链可追踪、可恢复。

---

## 2) 命令清单（Commands）

### 2.1 初始化任务（Initialize）
`.../router.sh create <feature> <name> <subtask1> [subtask2] ...`

用途：
- 创建任务索引与状态（首次使用必需）
- 参数：feature(功能名) name(任务名) subtask1...（子任务描述）

### 2.2 查看状态（Status）
`.../router.sh status`

用途：
- 输出当前任务初始化状态、待办/进行中/已完成概览
- **这是所有动作的前置检查入口（强制）**

### 2.3 获取下一任务（Next）
`.../router.sh next`

用途：
- 返回“依赖已满足”的下一条可执行任务
- **前置条件：必须已初始化（Rule A）**
- **前置条件：上一条任务若已完成，必须已 complete 并通过 status 校验（Rule B）**

### 2.4 标记完成（Complete）
`.../router.sh complete <feature> <seq> "<summary>"`

用途：
- 将指定任务标为完成，并记录简要总结
- **执行后必须立刻 status 校验（Rule B）**

---

## 3) 标准执行流程（Agent 必须严格遵循）

### 3.1 第一次进入项目 / 或不确定是否初始化过
1. `.../router.sh status`
2. 若未初始化 → `.../router.sh create <feature> <name> <subtask1> [subtask2] ...`
3. `.../router.sh status`（确认已初始化）
4. `.../router.sh next`（领取下一任务）

### 3.2 执行某个任务（单步闭环）
假设 `next` 给出任务：`<feature=X, seq=3>`

你必须按如下闭环执行：
1. 执行任务本身的工作（实现/修改/验证等）
2. `.../router.sh complete X 3 "一句话总结本次完成内容（包含关键改动点）"`
3. `.../router.sh status`（确认 X-3 已完成）
4. 仅在确认完成后：`.../router.sh next`（领取下一任务）

---

## 4) 常见错误与纠偏（Troubleshooting）

### 4.1 “next 没返回 / 报错 / 空结果”
处理顺序（强制）：
1. 先 `status` 判断是否未初始化 → 若是，先 `create`
2. 若已初始化，检查是否存在“上一任务未 complete”的提示
3. 若提示上一任务未完成：
   - 你必须回到上一任务，完成后执行 `complete` + `status` 校验，再 `next`

### 4.2 “我做完了但忘了 complete”
这会导致任务系统认为你仍停留在上一任务，从而：
- `next` 可能返回同一任务
- 或依赖判断失败

纠偏动作：
1. 找到对应 `<feature, seq>`
2. 执行 `complete ...`
3. `status` 校验
4. 再继续 `next`

---

## 5) 输出与记录规范（Summary 写法）

`complete` 的 summary 必须满足：
- 一句话（可包含 1-2 个分号）
- 必须包含：**改动对象 + 改动目的/结果**
- 示例：
  - `"完成登录页表单校验：修正 v-model 字段映射并补充错误提示"`
  - `"新增租户隔离策略：RLS policy 增加 tenant_id 条件并通过冒烟验证"`

---

## 6) 最小可用示例（Copy & Run）

# 进入任何 git 项目目录后：
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh status

# 若未初始化（必须带参数）：
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh create myfeature "我的任务" "子任务1" "子任务2" "子任务3"
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh status

# 领取下一任务：
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh next

# 完成后必须落账：
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh complete featureA 1 "完成 xxx：yyy"
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh status
<PROJECT_ROOT>/.opencode/skill/task-management/router.sh next
