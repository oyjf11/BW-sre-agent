# AI App Planner Executor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐 AI 应用生成平台面试材料里 Planner 到 Executor 的执行链路讲法，让它能回答后端面试官对幂等、状态恢复、调度、质量门禁和沙箱安全的追问。

**Architecture:** 这是纯 Markdown 文档改动。只修改目标 battle-plan 文件：顶部母题表增加一行速记，`<details>` 详细复盘中在“关键数字锚点”和“面试问答底稿”之间新增一个口述风格章节。所有新增内容保持面试话术风格，避免抽象概念堆叠。

**Tech Stack:** Markdown, shell verification (`sed`, `rg`, `git diff --check`), git.

---

## File Structure

- Modify: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`
  - Responsibility: 面试 battle-plan 主文档；新增 Planner→Executor 速记和详细追问底稿。
- Read-only reference: `docs/superpowers/specs/2026-06-13-ai-app-planner-executor-design.md`
  - Responsibility: 已确认的设计依据；执行时用来核对范围和验收标准。

No backend, frontend, dependency, lockfile, or unrelated interview files should be modified.

---

### Task 1: Confirm Current Target Document Shape

**Files:**
- Read: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`
- Read: `docs/superpowers/specs/2026-06-13-ai-app-planner-executor-design.md`

- [ ] **Step 1: Check the target table and details section**

Run:

```bash
nl -ba '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md' | sed -n '1,95p'
```

Expected:

```text
line 5 contains: ## 母题速记
line 7 contains the table header
line 9-11 contain the three existing rows
line 43 contains: ### 关键数字锚点
line 54 contains: ## 面试问答底稿
```

- [ ] **Step 2: Check the approved spec**

Run:

```bash
sed -n '1,220p' docs/superpowers/specs/2026-06-13-ai-app-planner-executor-design.md
```

Expected:

```text
The spec names the target file.
The spec requires one new mother-question table row.
The spec requires one new detailed section titled Planner 到 Executor：从“想清楚”到“稳稳做”.
```

- [ ] **Step 3: Confirm no unrelated files are staged**

Run:

```bash
git diff --cached --name-only
```

Expected:

```text
No output.
```

If there is output, unstage only unrelated files:

```bash
git restore --staged <path>
```

---

### Task 2: Add the Mother-Question Table Row

**Files:**
- Modify: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`

- [ ] **Step 1: Insert the new row after the Router/Planner row**

In `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`, add this row immediately after the existing row that starts with `| 为什么 Router 和 Planner 分开？ |`:

```md
| Planner 到 Executor 怎么衔接？ | Planner 不直接改代码，先把活拆成任务清单；Executor 先验清单，再按依赖执行，最后用真实构建和预览结果验收。失败了不全量重来，代码小错修当前步，计划拆错回 Planner。 | Planner 输出 DAG；Executor 做依赖校验、拓扑调度、单步重试、幂等恢复、lint/build/smoke test；本地 Mock 验证过分层并行、单步重试、失败传播。 | 幂等怎么做？执行状态落表，idempotency_key 唯一约束；已成功直接复用，RUNNING 看 heartbeat，FAILED 在重试上限内恢复。 |
```

- [ ] **Step 2: Verify the table still has four columns**

Run:

```bash
sed -n '5,14p' '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md'
```

Expected output includes these lines in order:

```text
| 触发（面试官会问） | kernel（背这句） | 项目锚点（这次具体改了/取舍了什么） | 可能追问 |
|---|---|---|---|
| 你们平台怎么保证 AI 生成质量？ |
| 为什么 Router 和 Planner 分开？ |
| Planner 到 Executor 怎么衔接？ |
| 多租户隔离怎么做？ |
```

---

### Task 3: Add the Detailed Planner-to-Executor Section

**Files:**
- Modify: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`

- [ ] **Step 1: Insert the new section after the key numbers table**

In `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`, insert the following content after the row:

```md
| 800 条 → 6000+ chunk | 语料库 → small-to-big 扩增 | 每范式 7-8 子块 |
```

and before:

```md
## 面试问答底稿
```

Insert this exact Markdown:

```md
### Planner 到 Executor：从“想清楚”到“稳稳做”

Planner 这一步我不会让它直接去改代码。它更像是先把活拆清楚：要建哪些表、要做哪些页面、要配哪些权限、每一步依赖谁、做完怎么验收。

Executor 拿到这份任务清单后，也不会自己猜需求。它第一步先检查清单能不能执行：任务 ID 有没有重复、依赖是不是都存在、会不会互相依赖成死循环、任务类型是不是平台支持的。比如 Planner 写了一个“配置支付回调”，但当前平台根本没接支付能力，那这一步就不能硬跑，要么回 Planner 重拆，要么提示用户确认范围。

检查通过以后，Executor 再按依赖关系跑。建表、认证、权限这种基础任务先做；页面、组件、接口如果互不依赖，就可以并行生成。每个任务执行完都会把结果写下来：生成了哪些文件、改了哪些配置、有没有 lint/build 报错、有没有通过验收。

失败时我不会默认整条链路推倒重来。TypeScript 报错、import 写错、字段没对上，这种代码小错就只修当前 task。Planner 漏了实体、依赖顺序拆错、权限任务没拆出来，这种就是计划问题，要带着失败证据回 Planner 重新拆。

幂等这里也不是靠模型“记住别重复执行”。每个任务开始前会算一个稳定的 `idempotency_key`，一般由 `project_id`、`plan_version`、`task_id`、`task_type` 和 `normalized_input_hash` 组成。这里最关键的是 `normalized_input_hash`：只放真正影响结果的输入，比如目标文件、schema 字段、依赖任务输出版本，不放时间戳、临时日志这类会抖动的东西。

执行记录会落到一张类似 `task_executions` 的表里，记录 `idempotency_key`、`status`、`attempt_count`、`input_hash`、`output_artifacts`、`error_message`、`started_at`、`finished_at`，并且给 `idempotency_key` 加唯一索引。任务开始时先插入 `RUNNING` 记录；插入成功说明我是第一个执行者；唯一键冲突就查已有记录：`SUCCEEDED` 直接复用产物，`RUNNING` 看 heartbeat 是否超时，`FAILED` 在重试上限内恢复。

文件生成也不会直接覆盖正式目录。先写到临时 workspace 或 artifact 区，lint、typecheck、build 过了，再提交 patch。数据库 migration 也会用稳定名称，执行前先查是否已经应用。外部 API 如果支持幂等键就透传；不支持就先查当前状态。对无法确认结果的高风险操作，不自动重试，转人工确认。

最后我不会相信模型说“生成好了”。Executor 要看真实产物：文件是否存在、路径有没有越界、TypeScript 能不能过、项目能不能 build、页面能不能打开、Console 有没有明显错误。检查结果会决定下一步：当前 task 局部修、上游任务补，还是回 Planner 重拆。

安全边界也要在 Executor 这一层收住。文件写入限制在 workspace 允许目录；命令执行走白名单，不给模型自由 shell；数据库和外部服务先 dry-run，高风险动作人工确认；生成代码放到临时 workspace 或沙箱里构建和预览，限制 CPU、内存、超时和网络访问。

一句话讲就是：Planner 负责把活拆清楚，Executor 负责先验清单、按依赖执行、用真实结果验收。中间每一步都有状态和产物，所以失败了能判断是代码没生成好，还是一开始计划就拆错了。
```

- [ ] **Step 2: Verify the new section is in the intended location**

Run:

```bash
rg -n "Planner 到 Executor|幂等这里|task_executions|安全边界|## 面试问答底稿" '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md'
```

Expected output includes:

```text
Planner 到 Executor 怎么衔接？
### Planner 到 Executor：从“想清楚”到“稳稳做”
幂等这里也不是靠模型
task_executions
安全边界也要在 Executor 这一层收住
## 面试问答底稿
```

The detailed section must appear before `## 面试问答底稿`.

---

### Task 4: Validate the Markdown Diff

**Files:**
- Verify: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`

- [ ] **Step 1: Inspect the exact diff**

Run:

```bash
git diff -- '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md'
```

Expected:

```text
Only one target file is shown.
The diff adds one row to the mother-question table.
The diff adds one detailed section after the key numbers table.
No existing interview content is deleted.
```

- [ ] **Step 2: Check Markdown whitespace**

Run:

```bash
git diff --check -- '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md'
```

Expected:

```text
No output.
```

- [ ] **Step 3: Check no unrelated files were changed by this task**

Run:

```bash
git status --short
```

Expected:

```text
The target file may appear as modified.
Existing unrelated dirty files may still appear.
No backend, frontend, lockfile, or unrelated docs should be newly modified by this implementation.
```

---

### Task 5: Commit the Documentation Update

**Files:**
- Stage: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`

- [ ] **Step 1: Stage only the target document**

Run:

```bash
git add '.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md'
git diff --cached --name-only
```

Expected:

```text
.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md
```

- [ ] **Step 2: Commit the target document update**

Run:

```bash
git commit -m "docs: expand planner executor interview notes"
```

Expected:

```text
[main <hash>] docs: expand planner executor interview notes
```

- [ ] **Step 3: Confirm unrelated worktree changes remain untouched**

Run:

```bash
git status --short
```

Expected:

```text
The committed target file no longer appears.
Pre-existing unrelated deleted or untracked files may still appear.
```
