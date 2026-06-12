# AI 应用生成平台 Planner 到 Executor 补充设计

## 任务理解

目标是在 `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`
中补齐 Planner 到 Executor 的讲法。现有文档已经讲清楚 Router、RAG 和 Planner 输出
DAG，但 Planner 之后怎么稳妥执行还偏薄，容易被后端面试官追问到幂等、状态恢复、
并发调度、质量门禁和沙箱安全。

本次补充要服务面试表达，不写成抽象白皮书。语言尽量贴近日常口述：先说真实流程，
再补必要术语；少用泛化概念，多讲具体怎么做。

## 修改计划

1. 在顶部“母题速记”表格中新增一行，主题为“Planner 到 Executor 怎么衔接”。
2. 在详细复盘中新增一节，位置放在 Planner 输出 DAG 之后、本地实测要点之前。
3. 新增正文围绕一条主线展开：Planner 先把活拆成任务清单，Executor 先验清单，
   再按依赖执行，最后用真实构建和预览结果验收。
4. 重点补齐后端追问：幂等怎么实现、任务怎么调度、执行状态怎么恢复、失败怎么分类、
   质量门禁怎么落地、安全边界怎么控制。

## 修改文件清单

- 计划修改：
  - `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`
- 本 spec 文件：
  - `docs/superpowers/specs/2026-06-13-ai-app-planner-executor-design.md`
- 明确不改：
  - 后端、前端业务代码
  - 依赖锁文件
  - 其他 interview 文档
  - 当前工作区里已有的删除文件和未跟踪文件

## 正文设计

### 顶部速记新增行

在“母题速记”表格中新增一行：

```md
| Planner 到 Executor 怎么衔接？ | Planner 不直接改代码，先把活拆成任务清单；Executor 先验清单，再按依赖执行，最后用真实构建和预览结果验收。失败了不全量重来，代码小错修当前步，计划拆错回 Planner。 | Planner 输出 DAG；Executor 做依赖校验、拓扑调度、单步重试、幂等恢复、lint/build/smoke test；本地 Mock 验证过分层并行、单步重试、失败传播。 | 幂等怎么做？执行状态落表，idempotency_key 唯一约束；已成功直接复用，RUNNING 看 heartbeat，FAILED 在重试上限内恢复。 |
```

### 详细复盘新增节

新增章节标题：

```md
## Planner 到 Executor：从“想清楚”到“稳稳做”
```

章节内容采用口述风格，覆盖以下要点：

1. Planner 不直接改代码，而是拆任务清单：表、页面、权限、依赖、验收方式。
2. Executor 不猜需求，先做清单检查：任务 ID、依赖、环、平台能力。
3. 检查通过后按依赖执行：基础任务先跑，无关页面和组件可并行。
4. 每个任务写下结果：生成文件、配置变更、lint/build 结果、验收状态。
5. 失败不默认全量重来：
   - TypeScript 报错、import 错、字段不匹配，修当前 task。
   - 漏实体、依赖顺序错、权限任务没拆出来，带证据回 Planner。
   - 平台能力不支持，执行前拦截，不跑到一半才失败。
   - 高风险变更先 dry-run 或人工确认。
6. 幂等实现讲清楚：
   - `idempotency_key = project_id + plan_version + task_id + task_type + normalized_input_hash`
   - `normalized_input_hash` 只包含影响执行结果的输入，不包含时间戳、日志等抖动信息。
   - `task_executions` 表记录状态、attempt、输入 hash、产物、错误和时间。
   - `idempotency_key` 加唯一索引，唯一键冲突后按状态处理。
7. 状态恢复讲清楚：
   - 任务状态包括 `PENDING / READY / RUNNING / SUCCEEDED / FAILED / SKIPPED`。
   - 已成功的任务恢复时直接跳过。
   - `RUNNING` 但 heartbeat 超时的任务标记为可恢复。
   - 无法确认外部结果的高风险操作不自动重试。
8. 质量门禁讲清楚：
   - 产物检查：文件是否生成、路径是否越界、有没有改到不该改的地方。
   - 静态检查：格式化、ESLint、TypeScript。
   - 构建检查：全项目 build。
   - 轻量运行检查：预览页面、Console、smoke test 或 migration dry-run。
9. 安全边界讲清楚：
   - 文件写入限制在 workspace 允许目录。
   - 命令执行走白名单，不给模型自由 shell。
   - 数据库和外部服务先 dry-run，高风险动作人工确认。
   - 生成代码在临时 workspace 或沙箱里构建和预览。

### 面试收口句

正文最后保留一句短收口：

```md
一句话讲就是：Planner 负责把活拆清楚，Executor 负责先验清单、按依赖执行、用真实结果验收。中间每一步都有状态和产物，所以失败了能判断是代码没生成好，还是一开始计划就拆错了。
```

## 验收方式

1. Markdown 表格格式不破坏，新增母题行能正常阅读。
2. 新增章节位置合理，不打断原有 Router/RAG/Planner 到本地实测的叙事。
3. 文风贴近面试口述，不使用大段 AI 味概念描述。
4. 后端追问有具体实现抓手，尤其是幂等、状态表、唯一约束、heartbeat、dry-run 和沙箱。
5. 不修改无关文件。

## 测试方式

这是文档修改，不需要跑后端或前端测试。实际修改后需要做：

1. `sed` 抽查目标文档新增位置。
2. `rg` 检查新增关键字是否存在。
3. `git diff --check` 检查 Markdown 是否有尾随空格等基础问题。

## 风险说明

1. 最大风险是把材料写得太“平台化”或太抽象，导致不像面试现场回答。
2. 幂等和沙箱部分如果写得过深，会偏离 AI 应用生成平台主题；需要控制篇幅，让它服务
   Planner 到 Executor 的主线。
3. 目标文档是面试材料，不应承诺真实生产已经完整落地；本地 Mock 验证和工程化设计要
   区分清楚。
