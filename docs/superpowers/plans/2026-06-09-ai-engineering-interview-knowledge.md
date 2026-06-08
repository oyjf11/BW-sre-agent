# AI Engineering Interview Knowledge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `.interview/AI工程化项目知识沉淀-面试版.md`, a defensible interview knowledge document that unifies enterprise Harness, frontend testing, app-generation agent, OpsPilot, and Vibe Dev Toolkit under seven AI engineering invariants.

**Architecture:** The document is a Markdown knowledge artifact, not a code feature. It front-loads contribution boundaries, then uses the seven invariant Harness principles as the main spine, with project evidence attached to each principle and interview-ready deep dives at the end.

**Tech Stack:** Markdown, local source materials under `.interview/`, OpsPilot source references under `backend/app/graph/`, shell validation with `rg`, `sed`, and `git`.

---

## File Structure

- Create: `.interview/AI工程化项目知识沉淀-面试版.md`
  - Responsibility: final interview-facing knowledge document.
  - Boundaries: separates enterprise background, owned testing domain, app-generation agent, OpsPilot SIT trial, and Vibe local demo.
- Reference only: `docs/superpowers/specs/2026-06-09-ai-engineering-interview-knowledge-design.md`
  - Responsibility: approved design source.
- Reference only: `.interview/harness-完整认知体系.md`
  - Responsibility: seven invariant principles and first-principles framing.
- Reference only: `.interview/AI应用生成平台-架构面试深聊.md`
  - Responsibility: app-generation agent architecture material.
- Reference only: `.interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md`
  - Responsibility: app-generation interview kernels and Q&A anchors.
- Reference only: `docs/superpowers/specs/2026-06-07-vibe-dev-toolkit-design.md`
  - Responsibility: Vibe local demo boundary and testing-domain details.
- Reference only: `backend/app/graph/builder.py`
  - Responsibility: OpsPilot graph node count, deterministic routing, retry and resume facts.
- Reference only: `backend/app/graph/nodes/__init__.py`
  - Responsibility: OpsPilot node behavior anchors for diagnose, critic, risk gate, verify, and RCA.

## Task 1: Create The Document Skeleton And Boundary Table

**Files:**
- Create: `.interview/AI工程化项目知识沉淀-面试版.md`
- Reference: `docs/superpowers/specs/2026-06-09-ai-engineering-interview-knowledge-design.md`

- [ ] **Step 1: Verify required source files exist**

Run:

```bash
for f in \
  docs/superpowers/specs/2026-06-09-ai-engineering-interview-knowledge-design.md \
  .interview/harness-完整认知体系.md \
  .interview/AI应用生成平台-架构面试深聊.md \
  .interview/battle-plan/实战-2026-06-08-AI应用生成平台架构深聊.md \
  docs/superpowers/specs/2026-06-07-vibe-dev-toolkit-design.md \
  backend/app/graph/builder.py \
  backend/app/graph/nodes/__init__.py; do
  test -f "$f" || { echo "missing: $f"; exit 1; }
done
```

Expected: exit code `0` and no `missing:` output.

- [ ] **Step 2: Create the initial Markdown file**

Use `apply_patch` to create `.interview/AI工程化项目知识沉淀-面试版.md` with this exact starting structure:

```markdown
# AI 工程化项目知识沉淀（面试版）

> 用途：面试时把企业级产研 Harness、前端自动化测试验证域、应用生成智能体、OpsPilot 和 Vibe Dev Toolkit 统一到一套 AI 工程化方法论中。  
> 主线：用确定、可信、可审计的 Harness，包裹概率性、会幻觉、不可靠的 LLM。  
> 使用方式：前 10 分钟讲项目边界和统一方法论；被追问时进入三段王牌展开和问答锚点。

## 0. 一句话定位

我近一年围绕 AI Agent 工程化落地，参与 / 推动了研发提效 Harness、应用生成智能体、运维智能体三类企业方向。其中，企业 Harness 的前端自动化测试验证域是我做得最深、最可防守的主战场；应用生成智能体体现我对产品化 Agent 平台的规划能力；OpsPilot 是团队基于 SRE 故障处置经验沉淀后的 SIT 试点；Vibe Dev Toolkit 是我为了面试演示做的本地可运行复刻。

## 1. 先把边界说清楚

| 项目 / 方向 | 项目状态 | 我的角色 | 可讲深度 | 面试可用锚点 | 不应夸大的边界 |
|---|---|---|---|---|---|
| 企业级产研 Harness | 企业级研发提效体系 | 参与体系建设，主战场在前端自动化测试验证域 | 能讲整体架构、治理逻辑和我负责域 | Commands / Agents / Skills / Rules、质量门禁、知识沉淀、测试三防线 | 不说自己主导整个企业级平台 |
| 前端自动化测试验证域 | 企业 Harness 中真实做深的能力域 | 我负责 / 主导做深 | 可展开到机制、执行证据、失败闭环 | AC 驱动 E2E、trace / 退出码 / 截图、AC↔断言双向映射、Bad Case 闭环 | 不把测试域扩大成整条研发链路都由我主导 |
| 应用生成智能体 | 企业轻应用生成方向，内部试点 / 架构推进 | 参与规划、架构设计和试点推进 | 能讲 Router / Planner、RAG、质量闭环、多租户 | scene→plan 场景化 RAG、Router / Planner / Executor、多租户隔离、SSO / RLS | 不说成独立完成大规模生产平台 |
| OpsPilot | 团队基于 SRE 经验沉淀后的运维智能体尝试，目前在 SIT 环境 | 团队试点核心参与 | 能讲 14 个功能节点、证据驱动、审批和 RCA | evidence_fanout、diagnose、critic、risk_gate、approval、verify、rca | 不夸大为全公司生产级 SRE 平台 |
| Vibe Dev Toolkit | 本地面试演示复刻 | 我为面试可视化演示做的同构复刻 | 能现场讲设计和演示价值 | task.json、AC 输入、E2E 真执行、coverage checker、Bad Case | 不包装成企业生产项目 |

## 2. 统一方法论：七个不变内核

## 3. 王牌展开一：前端测试三防线

## 4. 王牌展开二：应用生成智能体

## 5. 王牌展开三：OpsPilot

## 6. Vibe Dev Toolkit：本地可演示复刻

## 7. 高频面试问法与回答锚点

## 8. 收口表达
```

- [ ] **Step 3: Validate top-level structure**

Run:

```bash
rg -n "^## " .interview/AI工程化项目知识沉淀-面试版.md
```

Expected output contains these headings:

```text
## 0. 一句话定位
## 1. 先把边界说清楚
## 2. 统一方法论：七个不变内核
## 3. 王牌展开一：前端测试三防线
## 4. 王牌展开二：应用生成智能体
## 5. 王牌展开三：OpsPilot
## 6. Vibe Dev Toolkit：本地可演示复刻
## 7. 高频面试问法与回答锚点
## 8. 收口表达
```

- [ ] **Step 4: Commit skeleton**

Run:

```bash
git add .interview/AI工程化项目知识沉淀-面试版.md
git commit -m "docs: scaffold ai engineering interview knowledge"
```

Expected: commit succeeds and only `.interview/AI工程化项目知识沉淀-面试版.md` is included.

## Task 2: Fill The Seven Invariant Core Mapping

**Files:**
- Modify: `.interview/AI工程化项目知识沉淀-面试版.md`
- Reference: `.interview/harness-完整认知体系.md`

- [ ] **Step 1: Replace section 2 with the invariant overview**

Use `apply_patch` to replace the empty `## 2. 统一方法论：七个不变内核` section with this introduction and subsection list:

```markdown
## 2. 统一方法论：七个不变内核

所有项目其实都在解同一个方程：如何用一个确定、可信、可审计的系统，去包裹一个概率性、会幻觉、不可靠的 LLM。项目大小只改变吞吐、成本、租户、组织协作这些系数，不改变方程本身。

我会把这套方法论压成七句话：

| 内核 | 对抗的问题 | 面试里的项目证据 |
|---|---|---|
| 控制权永远归确定性系统 | LLM 概率性和无界循环 | Harness 编排、应用生成 Router/Planner、OpsPilot 条件路由、Vibe task.json |
| 约束前置，而非事后纠偏 | 工具越权、成本失控、生产风险 | 工具白名单、质量门禁、risk_gate、审批门禁 |
| 契约优先于对话 | 自然语言不可消费、不可评测 | AC JSON、结构化 plan、RootCauseCandidate、契约信封 |
| 证据高于断言 | LLM 自信幻觉 | trace / 截图 / 退出码、工具 evidence、verify 节点 |
| 分解胜于强提示 | 单次大 prompt 不可靠 | 研发链路拆分、Router/Planner/Executor、OpsPilot 14 节点 |
| 状态外置且可恢复 | LLM 无状态、任务会中断 | task.json、checkpoint、approval resume、事件日志 |
| 可观测与闭环内建 | 无法复盘、无法持续改进 | Bad Case、RCA、workflow report、成功 plan 回流 |

### 2.1 控制权永远归确定性系统

### 2.2 约束前置，而非事后纠偏

### 2.3 契约优先于对话

### 2.4 证据高于断言

### 2.5 分解胜于强提示

### 2.6 状态外置且可恢复

### 2.7 可观测与闭环内建
```

- [ ] **Step 2: Fill `2.1 控制权永远归确定性系统`**

Insert this content under `### 2.1 控制权永远归确定性系统`:

```markdown
LLM 是被编排的算子，不是编排者本身。下一步做什么、是否结束、走哪条分支，必须由确定性的代码、状态机或人来决定。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 主链路不是让模型自由发挥，而是 Commands → Agents → Skills → Rules 的受控执行环境。Agent 负责理解和生成，平台负责任务顺序、权限、门禁、恢复和审计。 |
| 前端测试域 | 测试是否通过不由模型口头宣布，而由 Playwright 执行结果、trace、截图、退出码和覆盖脚本判断。 |
| 应用生成智能体 | Router 先做轻量分流，复杂任务才进 Planner；Planner 生成 DAG 后由 Executor 执行，不让一个大模型调用从头黑盒跑到尾。 |
| OpsPilot | LangGraph 图由 builder 中的条件路由控制：critic 决定 PASS / NEED_MORE_EVIDENCE / REPLAN / CONTRADICTION，risk_gate 决定 BLOCKED / NEEDS_APPROVAL / executor，verify 决定 SUCCESS / RETRYABLE_FAILURE / FATAL_FAILURE。 |
| Vibe Dev Toolkit | task.json 状态机和任务选择算法控制恢复与派发，本地 demo 能把“控制权归系统”展示成可见文件状态。 |

面试锚点：我不会说“让 AI 自己判断做完没有”。我会把 AI 的输出视为候选结果，把流程推进权放在状态机、规则、测试和审批上。
```

- [ ] **Step 3: Fill `2.2 约束前置，而非事后纠偏`**

Insert this content under `### 2.2 约束前置，而非事后纠偏`:

```markdown
约束必须在执行前生效，而不是等模型已经调错工具、改错文件、触发高风险动作之后再补救。

| 项目 | 体现 |
|---|---|
| 企业 Harness | Rules 层承载权限、目录边界、质量门禁、熔断和审批要求，平台统一治理，业务团队在边界内配置流程。 |
| 前端测试域 | AC、断言映射、覆盖校验先定义清楚，测试生成和测试通过都必须落到这些约束上。 |
| 应用生成智能体 | 简单请求不进入重 Planner，低相关度 RAG 不注入 Planner，生成阶段要求每步溯源到需求或范式。 |
| OpsPilot | risk_gate 在执行前判断动作风险；real 模式下不可用能力 fail-closed；高风险 rollback 进入 approval_interrupt。 |
| Vibe Dev Toolkit | 工具链内核不允许内嵌 hoo-desk / login / isForget 这类业务词，项目知识只能来自 profile 和 AC。 |

面试锚点：约束不是 prompt 里的“请注意”，而是运行时过不去的门禁。
```

- [ ] **Step 4: Fill `2.3 契约优先于对话`**

Insert this content under `### 2.3 契约优先于对话`:

```markdown
Harness 里流动的应该是结构化产物，不是自然语言聊天记录。只要下游要机器消费，就必须有契约。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 需求、设计、任务、测试、交付都应输出标准化工程产物，而不是让 Agent 之间靠散文交接。 |
| 前端测试域 | AC 是结构化输入；每条断言要能回指 AC；覆盖报告能机器判断 MISSING / HOLLOW / ORPHAN。 |
| 应用生成智能体 | Router 输出结构化意图和命中的 scene→plan 范式，Planner 输出任务 DAG，Executor 按 DAG 执行。 |
| OpsPilot | IncidentAgentState、RootCauseCandidate、RemediationPlan、EvidenceItem 等结构化对象让节点之间可组合、可持久化、可测试。 |
| Vibe Dev Toolkit | 契约信封和 zod schema 让本地工具链可以校验输入输出，而不是靠模型“看起来写对了”。 |

面试锚点：契约的价值不是好看，而是让评测、回放、复用和定位错误都变成可能。
```

- [ ] **Step 5: Fill `2.4 证据高于断言`**

Insert this content under `### 2.4 证据高于断言`:

```markdown
LLM 最危险的不是会错，而是会自信地说“我做完了”。所以决策必须看证据，不看自我报告。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 质量门禁看测试报告、执行记录、截图、trace 和缺陷记录，而不是看 Agent 的口头总结。 |
| 前端测试域 | 三防线专门对抗“没跑却说跑了”“断言空洞”“只测 happy path”。 |
| 应用生成智能体 | 生成质量不能只靠模型说代码没问题，需要 lint、typecheck、build、预览和用户返工率反馈。 |
| OpsPilot | evidence_fanout 收集工具证据，diagnose 产出候选根因，critic 复核，verify 用部署状态、健康状态、流量指标判断修复是否有效。 |
| Vibe Dev Toolkit | 本地 demo 用 Playwright 真跑结果和覆盖脚本给面试官看，不靠口头解释。 |

面试锚点：模型输出是 Claim，工具和测试产物是 Evidence，系统门禁基于 Evidence 做 Decision。
```

- [ ] **Step 6: Fill `2.5` through `2.7`**

Insert this content under the remaining subsections:

```markdown
### 2.5 分解胜于强提示

可靠性来自把任务拆成小的、可验证、可回退的步骤，而不是把 prompt 写得越来越长。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 产研链路被拆成需求分析、方案设计、任务拆分、开发、审查、系统测试、交付和知识沉淀。 |
| 前端测试域 | 测试生成、真实执行、覆盖校验、失败归因、Bad Case 沉淀分开做，每一步都有独立产物。 |
| 应用生成智能体 | Router / Planner / Executor 拆层后，简单请求走快车道，复杂请求才生成 DAG。 |
| OpsPilot | 14 个功能节点把故障处置拆成 intake、triage、retrieve_memory、planner、evidence、diagnose、critic、remediation、risk、approval / executor、verify、rca。 |
| Vibe Dev Toolkit | 先复刻脊柱和测试域，后续再补需求、开发、审查节点，避免一次性做成不可验证的大系统。 |

面试锚点：好的 Harness 用普通模型也能跑稳，因为可靠性主要来自结构。

### 2.6 状态外置且可恢复

LLM 的上下文窗口不是数据库。长任务、审批、中断、重试都要求状态外置。

| 项目 | 体现 |
|---|---|
| 企业 Harness | task.json、事件日志、workflow report、知识库让任务状态和产物离开模型上下文。 |
| 前端测试域 | 测试结果、覆盖报告、Bad Case 以文件或结构化记录沉淀，能复查、复跑、复用。 |
| 应用生成智能体 | 项目、应用、plan、生成记录、用户修改、成功范式需要沉淀，否则无法做持续优化。 |
| OpsPilot | checkpoint、run state、pending approval 和 resume 白名单让审批后可以从正确节点继续。 |
| Vibe Dev Toolkit | task.json 和 events.jsonl 是本地演示里最直观的状态外置证据。 |

面试锚点：状态外置不是大系统专属，一个能暂停等审批的小 agent 也需要同一套原则。

### 2.7 可观测与闭环内建

没有观测就无法治理，没有闭环就不会变好。Harness 的结果不应只是一段输出，还应留下可复盘资产。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 贯穿面的质量门禁、知识沉淀、compound / research 让组织经验回流。 |
| 前端测试域 | Bad Case 把失败样本转成下次生成和校验可用的经验。 |
| 应用生成智能体 | 成功 plan、失败修复、用户返工、预览错误可以回流到场景化 RAG 和评估体系。 |
| OpsPilot | RCA 节点把故障过程、证据、动作和后续预防沉淀下来。 |
| Vibe Dev Toolkit | 本地 reports、badcases 和 workflow 记录让面试官能看到闭环，不只是听概念。 |

面试锚点：模型能力会被拉平，真正的护城河是组织经验在 Harness 里的复利沉淀。
```

- [ ] **Step 7: Validate invariant coverage**

Run:

```bash
rg -n "### 2\\.[1-7]|企业 Harness|前端测试域|应用生成智能体|OpsPilot|Vibe Dev Toolkit" .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: each `### 2.1` through `### 2.7` heading exists, and all five project names appear inside section 2.

- [ ] **Step 8: Commit invariant mapping**

Run:

```bash
git add .interview/AI工程化项目知识沉淀-面试版.md
git commit -m "docs: map ai engineering invariants to projects"
```

Expected: commit succeeds.

## Task 3: Write The Four Project Deep Dives

**Files:**
- Modify: `.interview/AI工程化项目知识沉淀-面试版.md`
- Reference: `docs/superpowers/specs/2026-06-07-vibe-dev-toolkit-design.md`
- Reference: `.interview/AI应用生成平台-架构面试深聊.md`
- Reference: `backend/app/graph/builder.py`

- [ ] **Step 1: Replace section 3 with frontend testing deep dive**

Use `apply_patch` to replace `## 3. 王牌展开一：前端测试三防线` with:

```markdown
## 3. 王牌展开一：前端测试三防线

这是我最可防守的主战场。面试官问“怎么避免大模型没测却说测了”“断言怎么写”“怎么避免只测 happy path”，都可以回到这套三防线。

| 幻觉层 | 典型问题 | 防线 | 机器证据 |
|---|---|---|---|
| 执行层 | 没跑却说跑了 | 真执行 + 机器证据 | Playwright trace、退出码、截图、测试报告 |
| 断言层 | 跑了但断言空洞 | AC 驱动断言 | 每条断言回指结构化 AC 的 expected |
| 覆盖层 | 只测 happy path | AC↔断言双向映射 | 确定性脚本判定 COVERED / MISSING / HOLLOW / ORPHAN |

我的表达重点不是“我会写 E2E”，而是“我把 LLM 测试生成的不可信，拆成三个可机器验证的问题”。

### 3.1 为什么三防线必要

只让模型生成测试，会有三类假阳性：

1. 它说跑了，但实际没跑。
2. 它真的跑了，但断言只是页面存在、按钮存在这种空洞断言。
3. 它覆盖了最顺的路径，却漏掉异常路径和状态切换。

所以防线必须覆盖执行、断言、覆盖三层。

### 3.2 Bad Case 闭环

失败不是结束，而是下次生成的训练材料。Bad Case 至少记录：

- 触发需求或 AC。
- 模型生成了什么测试。
- 真实执行产物是什么。
- 哪条防线抓住了问题。
- 下次应该注入什么规则或样例。

面试收口：我做测试域不是单纯提效，而是把“模型说测了”变成“系统证明测了”。
```

- [ ] **Step 2: Replace section 4 with app-generation deep dive**

Use `apply_patch` to replace `## 4. 王牌展开二：应用生成智能体` with:

```markdown
## 4. 王牌展开二：应用生成智能体

应用生成智能体可以按“企业内部 Lovable / Bolt”理解：业务人员用自然语言描述轻应用，系统生成可预览、可修改、可接入数据的应用原型。

### 4.1 Router / Planner / Executor 为什么拆开

| 层 | 职责 | 为什么不能合并 |
|---|---|---|
| Router | 意图识别、复杂度判断、轻重流程分流、RAG 检索 query 生成 | 简单请求不值得进入重 Planner；Router 的结构化意图是高质量检索 query |
| Planner | 融合需求、约束和 scene→plan 范式，生成任务 DAG | Planner 应该做规划，不应该耦合检索、执行和路由策略 |
| Executor | 按 DAG 执行代码生成、校验、预览、失败修复 | 执行需要重试、依赖拓扑和工具控制，不能让 Planner 黑盒完成 |

面试锚点：RAG 放在 Router 后、Planner 前，因为 Router 先把用户模糊需求变成结构化意图，RAG 才能检索到正确范式；RAG 的结果只是参考，Planner 有权否决低相关范式。

### 4.2 场景化 RAG

应用生成里的 RAG 不只是代码片段检索，而是检索 scene→plan 范式：

- 场景：CRM 客户跟进、审批流、库存台账、团队待办。
- 范式：表结构、页面结构、认证方式、权限隔离、关键交互。
- 元数据：适用技术栈、复杂度、历史成功率、常见失败点。

这能让 Planner 站在“已验证模式”上裁剪，而不是每次从零规划。

### 4.3 生成质量闭环

质量保障链路：

```text
生成前：需求结构化 + 范式检索 + 反幻觉溯源约束
生成中：按 DAG 分步生成，失败步骤可重试或回 Planner
生成后：lint / typecheck / build / 预览验证
回流：成功 plan、失败修复、用户返工 case 回到语料和评估体系
```

### 4.4 多租户和数据隔离

这类产品有两层租户：

1. 平台用户之间隔离。
2. 用户生成出来的 App 自身也有数据库、最终用户和权限边界。

面试金句：难点不是只隔离平台账号，而是隔离“租户的租户”。Supabase 开源版偏单项目设计，要做企业应用生成，需要补项目生命周期、密钥、路由、配额、休眠、分片这些控制平面能力。
```

- [ ] **Step 3: Replace section 5 with OpsPilot deep dive**

Use `apply_patch` to replace `## 5. 王牌展开三：OpsPilot` with:

```markdown
## 5. 王牌展开三：OpsPilot

OpsPilot 是团队基于 SRE 故障处置经验沉淀后的运维智能体尝试，目前在 SIT 环境。它的价值是证明同一套 Harness 内核可以迁移到故障处置：证据采集、诊断、反证、方案、风险门禁、审批、执行、验证、RCA。

### 5.1 14 个功能节点

OpsPilot 的功能节点可以这样讲：

```text
intake
→ triage
→ retrieve_memory
→ planner
→ evidence_fanout
→ evidence_aggregate
→ diagnose
→ critic
→ remediation
→ risk_gate
→ approval_interrupt / executor
→ verify_outcome
→ rca
```

补充说明：dispatcher 是入口路由 passthrough，不算业务功能节点；按功能节点讲是 14 个。

### 5.2 证据驱动故障处置

| 阶段 | 作用 |
|---|---|
| planner | 决定需要哪些证据 |
| evidence_fanout | 并行调用日志、指标、K8s、DB、SLB 等工具 |
| evidence_aggregate | 聚合证据，压缩噪声 |
| diagnose | 生成候选根因 |
| critic | 复核证据是否充分，必要时要更多证据或重规划 |
| remediation | 产出修复动作 |
| risk_gate | 判断能否执行、是否需要审批 |
| verify_outcome | 用真实状态和指标验证动作结果 |
| rca | 沉淀故障复盘和预防建议 |

### 5.3 风险门禁

OpsPilot 不追求“所有动作自动化”。低风险、能力可用、前置条件满足的动作可以受控执行；高风险动作进入审批；能力不可用时 fail-closed。

面试锚点：SRE 场景里，自动化的边界比生成能力本身更重要。删库、回滚、扩缩容这类动作不能让模型直接决定。
```

- [ ] **Step 4: Replace section 6 with Vibe positioning**

Use `apply_patch` to replace `## 6. Vibe Dev Toolkit：本地可演示复刻` with:

```markdown
## 6. Vibe Dev Toolkit：本地可演示复刻

Vibe Dev Toolkit 的定位很清楚：它不是企业生产项目，而是我为了面试官能在本地看到运行效果，做的同构复刻。

它证明三件事：

1. 我不是只会讲 Harness 理论，能把控制权、契约、状态、证据、闭环落成文件和脚本。
2. 我负责的测试域不是抽象概念，能用真实 Vue2 项目、Playwright、AC、覆盖检查跑出来。
3. 我知道如何控制复刻范围：脊柱和测试域做深，需求、开发、审查这些后续节点留接口，不在 demo 里无限扩张。

可演示链路：

```text
AC JSON
→ task.json 任务状态
→ test-generator 生成 Playwright 用例
→ Playwright 真执行
→ coverage-checker 做 AC↔断言双向映射
→ reports / badcases 沉淀
```

面试说法：企业 Harness 是真实背景，Vibe 是本地演示复刻。它的价值是让面试官看到我能把思想做成可运行的工程样机。
```

- [ ] **Step 5: Validate deep dive anchors**

Run:

```bash
rg -n "三防线|Router / Planner / Executor|scene→plan|14 个功能节点|SIT 环境|本地可演示复刻|不是企业生产项目" .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: each phrase appears at least once.

- [ ] **Step 6: Commit deep dives**

Run:

```bash
git add .interview/AI工程化项目知识沉淀-面试版.md
git commit -m "docs: add ai engineering project deep dives"
```

Expected: commit succeeds.

## Task 4: Add Interview Q&A And Closing Narrative

**Files:**
- Modify: `.interview/AI工程化项目知识沉淀-面试版.md`

- [ ] **Step 1: Replace section 7 with Q&A anchors**

Use `apply_patch` to replace `## 7. 高频面试问法与回答锚点` with:

```markdown
## 7. 高频面试问法与回答锚点

### Q1：你到底负责哪部分？

答法：我参与的是企业 AI 工程化落地，不是单点工具开发。最深的是企业 Harness 里的前端自动化测试验证域，我负责把 AC、E2E、机器证据、覆盖映射和 Bad Case 闭环做成可验证机制。应用生成智能体我参与规划和试点推进，重点在 Router / Planner、场景化 RAG、生成质量和多租户。OpsPilot 是团队 SRE 智能体 SIT 试点，我能讲清证据驱动、风险门禁和 RCA 闭环。

### Q2：这几个项目是什么关系？

答法：它们不是一个项目，而是同一套 AI 工程化内核在不同场景里的落地。企业 Harness 面向研发提效，应用生成面向轻应用生成，OpsPilot 面向 SRE 故障处置，Vibe 是本地可演示复刻。统一问题都是：怎么用确定性系统控制不确定的 LLM。

### Q3：怎么避免大模型没测却说测了？

答法：我不会相信模型的自我报告，而是用三防线。第一，真执行拿 trace、截图、退出码。第二，断言必须回指 AC 的 expected。第三，AC 和断言双向映射，抓 MISSING、HOLLOW、ORPHAN。这样“测没测、测了什么、漏了什么”都由机器证据回答。

### Q4：应用生成智能体为什么要拆 Router 和 Planner？

答法：Router 管分流和意图结构化，Planner 管复杂规划。简单请求不该进重 Planner；而 RAG 需要 Router 产出的结构化 query 才检索得准。RAG 检索的是 scene→plan 范式，给 Planner 参考，不直接变成执行指令。

### Q5：OpsPilot 怎么防止错误执行？

答法：OpsPilot 不让模型直接执行高风险动作。先通过 evidence 采集和 critic 复核形成诊断，再由 remediation 产出动作，risk_gate 判断风险和能力边界。高风险进入审批，能力不可用 fail-closed，执行后 verify_outcome 用真实指标验证。

### Q6：哪些是企业项目，哪些是演示？

答法：企业 Harness 是企业级研发提效背景，前端测试验证域是我做深的负责域；应用生成智能体是企业轻应用生成方向的规划和试点推进；OpsPilot 是团队 SRE 经验沉淀后的 SIT 试点；Vibe 是我为面试本地演示做的同构复刻，不包装成生产项目。
```

- [ ] **Step 2: Replace section 8 with closing narrative**

Use `apply_patch` to replace `## 8. 收口表达` with:

```markdown
## 8. 收口表达

我想表达的不是“我做过几个 AI 项目”，而是我在不同场景里反复处理同一组工程问题：

- 控制权不能交给模型，要交给状态机、规则、测试和人。
- 约束要前置，不能事后靠人肉擦屁股。
- 节点之间要靠契约交接，不能靠自然语言散文。
- 决策要看证据，不看模型自信声明。
- 复杂任务要拆成可验证、可回退的小步。
- 状态要外置，任务要能中断、恢复、审计。
- 失败经验要回流，否则系统不会越用越好。

这就是我对 AI 工程化的核心理解：模型能力会不断变强，但真正决定企业落地质量的，是外面这层 Harness 能不能把不确定能力变成可控、可验证、可规模化的工程系统。
```

- [ ] **Step 3: Validate Q&A count and closing**

Run:

```bash
rg -n "^### Q[1-6]|这就是我对 AI 工程化的核心理解" .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: six Q&A headings plus the closing sentence appear.

- [ ] **Step 4: Commit Q&A and closing**

Run:

```bash
git add .interview/AI工程化项目知识沉淀-面试版.md
git commit -m "docs: add interview qa anchors"
```

Expected: commit succeeds.

## Task 5: Final Review, Validation, And Knowledge Capture

**Files:**
- Modify: `.interview/AI工程化项目知识沉淀-面试版.md`

- [ ] **Step 1: Run boundary-risk scan**

Run:

```bash
rg -n "个人项目|个人复刻|我主导整个|全链路主导|企业生产项目|大规模生产级|TB[D]|TO[D]O|待[定]|占[位]" .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: no output. If there is output, edit the line to use the approved boundary wording:

```text
OpsPilot：团队 SIT 试点
Vibe Dev Toolkit：本地面试演示复刻
应用生成智能体：参与规划 / 试点推进 / 架构设计锚点
企业 Harness：企业级背景，前端测试验证域是我做深的负责域
```

- [ ] **Step 2: Run required anchor coverage scan**

Run:

```bash
for term in \
  "企业级产研 Harness" \
  "前端自动化测试验证域" \
  "应用生成智能体" \
  "OpsPilot" \
  "Vibe Dev Toolkit" \
  "控制权永远归确定性系统" \
  "约束前置" \
  "契约优先" \
  "证据高于断言" \
  "分解胜于强提示" \
  "状态外置" \
  "可观测与闭环"; do
  rg -q "$term" .interview/AI工程化项目知识沉淀-面试版.md || { echo "missing anchor: $term"; exit 1; }
done
```

Expected: exit code `0` and no `missing anchor:` output.

- [ ] **Step 3: Append knowledge capture**

Append this section to the end of `.interview/AI工程化项目知识沉淀-面试版.md`:

```markdown
## 9. 知识沉淀

### 本次关键设计决策

- 用七个不变内核做主线，而不是按项目流水账展开。
- 把前端测试域作为最强个人贡献锚点。
- 把应用生成智能体作为产品化 Agent 平台锚点。
- 把 OpsPilot 作为 SRE 场景团队 SIT 试点锚点。
- 把 Vibe Dev Toolkit 明确定位为本地演示复刻。

### 踩坑提醒

- 不要把 Vibe 包装成企业生产项目。
- 不要把 OpsPilot 夸大成全公司生产级平台。
- 不要把应用生成智能体的参与规划说成独立完成。
- 不要把企业 Harness 全景讲成个人全链路主导。

### 下次可复用检查清单

- 先写项目边界，再写能力亮点。
- 每个抽象原则都必须绑定项目证据。
- 每个项目亮点都要能回答“证据是什么”。
- 每个面试说法都要有可退守的诚实边界。

### 应写入长期规则

- 面试知识库中的项目材料必须区分企业背景、负责域、团队试点、本地演示和架构推演。
- 所有“AI 工程化”叙事都应尽量落到控制、契约、证据、状态、闭环五类可追问锚点上。
```

- [ ] **Step 4: Show final diff**

Run:

```bash
git diff -- .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: diff only touches `.interview/AI工程化项目知识沉淀-面试版.md`.

- [ ] **Step 5: Commit final review changes**

Run:

```bash
git add .interview/AI工程化项目知识沉淀-面试版.md
git commit -m "docs: finalize ai engineering interview knowledge"
```

Expected: commit succeeds.

- [ ] **Step 6: Confirm final state**

Run:

```bash
git log --oneline -5
git status --short .interview/AI工程化项目知识沉淀-面试版.md
```

Expected: recent commits include the document commits, and there is no status output for `.interview/AI工程化项目知识沉淀-面试版.md`.

## Self-Review

Spec coverage:

- Project boundary table: Task 1.
- Seven invariant structure: Task 2.
- Frontend testing deep dive: Task 3 Step 1.
- App-generation agent deep dive: Task 3 Step 2.
- OpsPilot SIT deep dive: Task 3 Step 3.
- Vibe local demo positioning: Task 3 Step 4.
- Interview Q&A anchors: Task 4.
- Knowledge capture and validation: Task 5.

Placeholder scan command for the plan itself:

```bash
rg -n "TB[D]|TO[D]O|待[定]|占[位]|similar t[o]|implement late[r]|fill in detail[s]" docs/superpowers/plans/2026-06-09-ai-engineering-interview-knowledge.md
```

Expected: no output.
