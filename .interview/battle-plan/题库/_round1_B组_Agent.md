# B 组 Agent/Prompt 母题 · 完整答案

> 8 个核心母题，每题的展开遵循"为什么→怎么做→坑/边界→追问预判"四层递进。
> 项目印证优先引用 OpsPilot 的具体情节。

---

## M10 · Agent 核心组件

**Kernel**：四件套——规划(拆任务)+记忆(短期上下文/长期向量库)+工具调用(感知外部)+反思(自我纠错)。LLM 是大脑，工具是手脚，记忆是状态，编排是骨架。

**展开**：
### Layer 1 — 为什么 / 背景

Agent 不是 prompt 的简单延伸，它引入了一个范式跃迁：**从"模型一次回答"变成"模型主动使用外部工具、记住历史、自我纠偏的多轮闭环"**。单次 LLM 推理有天然上限：知识截止训练日期、无外部感知、长任务会漂移。Agent 的四个组件就是四个对症解药——工具补感知、记忆补遗忘、规划补复杂度、反思补错误。

### Layer 2 — 怎么做 / 机制

1. **规划（Planning）**：把"修这个故障"拆成"先查日志→再查指标→对比版本变更"的子任务序列。两种模式——Plan-and-Execute（先出完整计划再批量执行，省 token 但纠错弱）、ReAct（边做边规划，灵活但对模型推理要求高）。OpsPilot 采中间态：planner 出 Plan → 执行 → critic 打回可 replan。
2. **记忆（Memory）**：短期 = 对话上下文窗口内的历史（随时可能被顶出）；长期 = 向量库/知识库存历史经验，检索后注入当前窗口。关键设计：不是什么都要记——只记"故障类型+证据指纹+处置结果"的结构化摘要，而不是整段对话。
3. **工具调用（Tool Use）**：LLM 通过 function calling 选工具+填参数→执行→结果回灌。要害不在"能不能调"，在"调错了会怎样"——所以工具层要有 schema 校验、超时兜底、错误可读返回、幂等防护。
4. **反思（Reflection）**：执行完回头看「我刚才做得对吗？」——这是 Agent 从"能做事"到"能把事做对"的关键跃迁。Reflection 的结论写入 Memory，形成经验积累的正循环。

### Layer 3 — 坑 / 边界 / 追问预判

- **规划坑**：过度规划（细节推演三四层，执行时全错）vs 欠规划（两个模糊步骤，跑一半迷路）。解法：只规划当前可验证的一层，留 replanning 回路。
- **记忆坑**：上下文窗口有限，对话越长越容易忘早期约束。解法：阶段性总结 + 关键信息持久化到外部存储，而不是拼命塞更多上下文。
- **工具调用坑**：LLM 填的参数可能不合法（类型错、必填缺、取值范围外）；工具可能超时/500/返回垃圾。解法：网关层前置校验 + 结构化错误返回（不是"Something went wrong"，而是 `{error_code, retryable: true, suggestion}`）。
- **反思坑**：LLM 自我批判不总是有效——它可能"为自己的错误强行辩解"（自我合理化）。解法：Reflection 必须基于外部信号（工具返回的真实数据、跨源矛盾检测），而不是纯自省。

### Layer 4 — 同类变式

- **Shallow Agent**：只有工具调用，无规划/记忆/反思 → 简单任务够用，长任务崩溃（跑偏、重复、不知回头）。
- **Deep Agent**：四件套齐全 + 文件系统(卸上下文) + 子 Agent(隔离上下文) + HITL(关键步骤人审批)。OpsPilot 就是手搓的 deep agent：planner → 规划，evidence_fanout → 子 Agent，evidence 落 DB/OSS → 文件系统，risk_gate+approval → HITL，critic → 反思。

**项目印证**：
- **OpsPilot**：13 节点就是把四件套拆成可独立验证的确定性流程——planner 做规划、retrieve_memory+RAG 做长期记忆、evidence_fanout+tool gateway 做工具调用、critic 节点做反思（回边退回重查）。四个组件不是并列的模块，而是按故障生命线串起来的阶段工序。
- **应用生成平台**：意图识别系统里 Router/Planner 分层 = 规划+工具调用的落地；RAG 检索历史案例 = 长期记忆；执行完校验回退 Router = 反思闭环。
- **前端测试域**：自愈 agent 把"定位失效→查找新锚点→修→沙箱重跑验证"串成规划-执行-反思闭环，每步都有闸门校验防止作弊。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-opspilot全旅程主干.md、实战-2026-06-10-deepagents范式与项目对标.md
> 🏷️ 覆盖题号：Agent 核心组件 / 基础能力 / 规划记忆工具反思（~15 次）

---

## M11 · ReAct 框架

**Kernel**：Reasoning(想) + Acting(做)，交替循环。每次 Thought→Action→Observation 一个 token 不浪费。比纯 prompt 好在：错误可观察可纠正，不需要一口气猜到底。

**展开**：
### Layer 1 — 为什么 / 背景

纯 prompt 调 LLM 的致命缺陷：模型不知道外部世界当前状态，一次性生成全部回答，错了也无法中途纠正。ReAct 把推理和行动做成交替循环——**每想一步就出去看一眼，拿真实反馈校准下一步推理**。这解决了 AI 身上的核心悖论：它不会的东西让它自己发现、自己查、自己修正。

### Layer 2 — 怎么做 / 机制

标准 ReAct 循环三步：

```
Thought: 我需要先查这个服务的日志，时间窗口是最近30分钟
Action: query_logs(service="payment", time_range="-30m")
Observation: 返回 230 条错误日志，全是 "connection refused"
Thought: 连接拒绝说明下游依赖丢了，需要查 K8s pod 状态
Action: query_k8s_pods(namespace="payment", label="app=gateway")
Observation: 3/5 pods CrashLoopBackOff
Thought: Pod 崩溃+连接拒绝=发布回归，证据够了，可以下结论
```

关键设计：
- **Plan（推理文本）**：Thought 不是随便写，它包含"我想验证什么假设 + 期望看到什么"，Observation 回来能跟预期对比，偏差就是纠错信号。
- **Observation（工具返回）**：返回的不只是工具原始输出，还包括执行是否成功的状态码、耗时——方便 LLM 判断"是数据不对"还是"工具坏了"。
- **收敛条件**：不是无限循环到上下文耗尽，而是当"证据充分度 ≥ 阈值"或"最多 N 轮"时终止。

### Layer 3 — 坑 / 边界 / 追问预判

- **上下文联胀**：每轮 Observation 全量保留，很快撑爆窗口。解法：对 Observation 做摘要压缩，只保留关键发现和异常信号，扔掉冗余日志。
- **工具失败的自愈**：工具返回 500 或超时，LLM 不应直接放弃或换个工具乱试。需要结构化错误信息告诉它"这是可重试的还是一次性的"，以及替代工具建议。
- **ReAct 不是万能的**：对"需要完整事先规划"的任务（比如 SQL 生成需要先理解 schema→再写→再校验），ReAct 的单步推理不如 Plan-and-Execute。判据：任务的依赖图是线性的（ReAct 合适）还是需要全局视角规划（Plan-Execute 合适）。
- **死循环风险**：LLM 可能在证据不足时反复绕圈。必须设 max steps + loop guard，超限强制终止。

### Layer 4 — 同类变式

- **ReAct vs Plan-and-Execute**：ReAct 边想边做，纠错快但 token 消耗大（每步都要 Thought）；Plan-Execute 先出全部计划再批量执行，省 token 但计划一旦偏差无法中途修正。OpsPilot 证据扇出就是 Plan-Execute 的变体（先 planner 出 Plan → fanout 并行执行），而整个图级别的 critic 回边又提供了 ReAct 式的"执行后反思纠正"。
- **ReAct vs Tool-Only**：纯工具调用没有 Thought 推理步骤，LLM 直接输出 function call。适合确定性高、选工具本就够的场景，但缺了推理链的解释性和纠错能力。

**项目印证**：
- **OpsPilot**：evidence_fanout 节点内部每个专科 agent 就是 ReAct 循环——Thought（分析工单+制定查询计划）→ Action（调 tool gateway 查日志/K8s/指标）→ Observation（拿返回数据）→ 下一轮 Thought，直到出结论或被步数上限截断。截断惩罚（×0.9）直接反映在 critic 质量分里。critic 节点本身的 4 路裁决 + 回边构成了图级别的"外部 ReAct 循环"——evidence 不够 → 退回去再查 → 再评。
- **应用生成平台**：Router 决策"用户想干什么"→ Planner 规划修改步骤→执行验证，也是一层 Thought→Action 闭环。
- **前端测试域**：自愈 agent 本质是 ReAct：分析报错（Thought）→ 修改定位（Action）→ 沙箱重跑（Observation）→ 判断修对了没（下一轮 Thought）。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-critic仲裁打分机制.md、条件路由机制.md
> 🏷️ 覆盖题号：ReAct / Reasoning+Acting / Thought-Action-Observation / 比纯 prompt 强在哪（~15 次）

---

## M12 · CoT / ToT / GoT 推理策略

**Kernel**：CoT(链式，一步一推理)→ToT(树状，多分支探索+剪枝)→GoT(图状，分支可合并)。复杂度递增，CoT 够用 80% 场景。关键是让模型"show your work"而非直接给答案。

**展开**：
### Layer 1 — 为什么 / 背景

LLM 直接给答案的错误率远高于"一步步推理再给答案"。背后原理：复杂问题的中间步骤多，一次性生成时每一步都在前一步还没写出来的时候就"猜"，错误会被传播和放大。推理策略的本质是**把隐式思考显式化**——让模型在生成最终答案前，先把推理过程写出来，也就是"show your work"。

### Layer 2 — 怎么做 / 机制

三种策略复杂度递增：

1. **CoT（Chain-of-Thought，链式思维）**：prompt 里加一句"让我们一步步思考"，模型就会分步推理。最简单、最通用、80% 场景够用。例子：prompt 里给 few-shot 示例（问题→推理步骤→答案），让模型模仿这种分解-推理-汇总的模式。
2. **ToT（Tree-of-Thought，树状思维）**：不只要分步，还要在每一步**探索多个可能的分支**，然后用评估函数剪枝——保留最有希望的 2-3 条路径继续探索，砍掉低分的。适合需要"想到多个可能性再挑最优"的场景（如谜题、方案设计）。
3. **GoT（Graph-of-Thought，图状思维）**：ToT 的升级——不同分支的中间推理结果可以**合并复用**，而不只是分叉和剪枝。把推理建模成有向图，节点是中间结论，边是推理依赖。适合多个子问题共享中间推导的场景。

### Layer 3 — 坑 / 边界 / 追问预判

- **CoT 不是银弹**：简单分类任务加 CoT 反而降低准确率（"过度思考"）。判定标准：任务需要 ≥3 步推理才需要 CoT。
- **ToT 的剪枝函数设计是核心难点**：剪枝太激进 → 正确答案被误杀；剪枝太保守 → 分支爆炸，token 消耗失控。通常用"LLM 自评 + 概率阈值"双轨，但 LLM 自评本身也会偏。
- **GoT 落地成本高**：需要定义"什么算可以合并的等价推理"——两个不同路径产生的"部署异常"标签，是同一个 root cause 的自然合并，还是两个不同原因的巧合同名？判断这件事本身可能比推理还难。
- **CoT 对幻觉无效**：CoT 只改变了推理顺序，不改变推理质量——模型在每一步仍然可能编造事实。所以你看到 CoT 里"检查日志发现 error rate 100%"，可能是纯编的。防幻觉要回到证据驱动（RAG 检索真数据 + 引用校验）。

### Layer 4 — 同类变式

- **Self-Consistency**：同一个问题跑 N 次 CoT，取多数答案——用统计代替单次推理的偶然性。相当于最朴素的"多跑几次选最优"，比 ToT 轻量但效果显著。
- **ReAct vs CoT**：CoT 是纯推理链（闭环在脑子里），ReAct 是推理+行动交替（伸手去摸外部世界）。CoT 适合知识推理型任务，ReAct 适合需要外部信息的环境交互型任务。

**项目印证**：
- **OpsPilot**：planner 节点的"出调查计划"本质是 CoT——先把故障分析逻辑写成计划文本，再交给证据扇出去执行。diagnose 节点的根因推断也是 CoT：基于证据+记忆逐步推理出根因假设链。critic 的 4 路裁决中，quality < 0.3 + 证据少的 REPLAN 分支可以类比 ToT 的剪枝——这条路径不行、退回去重来。
- **应用生成平台**：意图识别不用 LLM few-shot 推理，就是因为边界 case 下 CoT 会漂移——改用 RAG 召回相似历史案例更稳。这是 CoT 局限性的实战印证。
- **前端测试域**：自愈 agent 分析执行轨迹定位根因时，用的是"排除法 CoT"——先判断"页面真坏了"还是"只是定位过期"，再往下钻。不是所有推理都需要多分支，CoT 的线性推理在结构化的故障场景里正好够用。

> 📎 素材：题库/母题骨架-一页纸.md
> 🏷️ 覆盖题号：CoT / ToT / GoT / 提升规划能力 / Plan-and-Execute vs ReAct（~10 次）

---

## M13 · 单 Agent vs 多 Agent

**Kernel**：单 Agent = 一个 LLM 包揽全部，简单但长任务会漂移。多 Agent = 拆成独立角色并行/串行协作，各司其职但通信成本高。判据：任务能否自然拆成 2+ 独立子任务？子任务间依赖图是 DAG（可并行）还是 sequential？

**展开**：
### Layer 1 — 为什么 / 背景

业界有个常见的冲动：一上来就堆 5 个 agent 搞"圆桌辩论"，显得架构高级。但用"招人"的常识想一下——让五个人同时在一份 Word 里打字——你立刻知道这是疯子行为。单 vs 多 Agent 的本质是 Brooks 定律在 AI 时代的映射：加人越多，沟通成本平方增长；只有当"分工的收益"超过"沟通的额外成本"时，多 agent 才划算。

单 Agent 的天然优势：上下文不割裂、无需自然语言交接（不会在 agent 间用会丢失信息的语言转述）、决策链路可追溯。多 Agent 的存在理由只有一个：**单 Agent 的上下文窗口装不下、或子任务天然互不依赖可并行**。

### Layer 2 — 怎么做 / 机制

多 Agent 的三种协作模式：

1. **主从模式**（主 Agent 派活给子 Agent）：主 agent 负责拆任务+汇总结论，子 agent 只负责执行自己那块——只读、互不商量。这是多 agent 最安全可控的模式。例子：主 agent 拆出"查日志""查 K8s""查指标"三个子任务，三个子 agent 分头查，主 agent 汇总下结论。
2. **对等协作模式**（多个 agent 平等对话）：多个 agent 轮流发言、互相质疑、共同推进。好处是能覆盖更多视角，坏处是容易跑偏——一个说东一个说西，没裁判就永远不收敛。
3. **辩论/投票模式**（多个 agent 出方案→仲裁）：并行出多个方案，由一个仲裁者选出最优。前提：仲裁者有便宜可靠的评判手段，否则"让五个 AI 争论谁对"只是费 token。

### Layer 3 — 坑 / 边界 / 追问预判

- **关键澄清：OpsPilot 的 13 节点不是多 Agent 系统！** 这是一个最常见的混淆点。13 节点是**单 Agent 内部的确定性编排**——每个节点是 LangGraph 图上的一个函数节点，不是独立 agent。节点之间通过共享 state 传数据（不通过自然语言），路由由规则决定（不由 LLM），不存在 agent 间的"通信成本"和"结论冲突"。它更准确的名字是"Deep Agent"而非"Multi-Agent"。
- **真正多 Agent 的通信成本**：每次 agent 间交接都靠自然语言，信息在每次转述中必然丢失。人类团队靠多年默契省掉的沟通，AI 全要靠每次重新表达。这就是为什么"五个人同时改一份 Word"是疯子行为——而 AI 之间更糟，因为它们没有团队记忆。
- **判断何时上多 Agent 的两道灵魂拷问**：① 切开后，几份活之间需要互相商量吗？需要，就等于没切开，回去派一个人。② 改东西的权限需要分散吗？需要，就会互相冲突，回去派一个人。
- **OpsPilot 里真正像"多 Agent"的部分**：evidence_fanout 扇出并行取证——但这几个专科 agent 是**只读、互不依赖、不互相通信**的。它们不抢排他资源，不投票，只把各自的 EvidenceItem 汇总到 aggregate 节点揉成一个质量分。这就是最安全的"主从模式"——主（fanout）拆任务 → 子 agent 分头查 → 主（critic）审材料。

### Layer 4 — 同类变式

- **AI 多 Agent vs 人类团队**：Brooks 定律对人类团队和 AI 团队同样生效，但有一项变了——会计规则。AI 没有培训成本（复制一份上下文即可上岗）、可以被"用完就扔"（并行跑五份取最优，扔掉四份）。所以同样的 Brooks 定律约束下，AI 多 Agent 的场景更宽——只要"评判成本够便宜"。
- **Speculative Parallelism（投机并行）**：同一个任务并行跑 5 个 AI 实例，取最好的结果。对人类是管理灾难（雇五人干一活开掉四个），对 AI 是常规操作。这种模式下，"验证"成了新瓶颈——5 份方案，谁来判哪份对？

**项目印证**：
- **OpsPilot**：13 节点 = 单 Agent 的确定性编排，不是多 Agent——这是必须讲清的混淆点。evidence_fanout 的并行取证是最安全的多 Agent 子模式（只读+不通信），critic 的 4 路裁决替代了"多 Agent 投票"（不投票，材料不够就退回重查）。为什么不用多 Agent 辩论：SRE 诊断的每一条证据都要可追溯，多个 agent 各说各的、靠语言争论谁对，既不可控也不可审计。
- **应用生成平台**：Router + Planner 可以视为两层 Agent 的分工协作——Router 判断意图、Planner 制定修改计划，但两者之间传递的是结构化 Intent 对象而非自然语言，避开了多 Agent 的通信损耗。
- **前端测试域**：自愈 agent 是纯粹的单 Agent 模式——分析→定位→修改→验证，一个人在闭环里做完，不需要第二个 agent 来"审查"（闸门是代码做的，不是另一个 AI）。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-deepagents范式与项目对标.md、实战-2026-06-10-critic仲裁打分机制.md、ai_harness_interview_handbook.md §4
> 🏷️ 覆盖题号：多 Agent 协作 / Reflection / Memory / agent 冲突 / 单 vs 多 Agent（~12 次）

---

## M14 · Reflection + Memory 机制

**Kernel**：Reflection = Agent 执行完回头看「我刚才做得对吗？」，自我纠错。Memory = 短期(对话上下文窗口)+长期(向量库存历史经验)。两者协同：Reflection 的结论写入 Memory，未来同类任务直接调记忆避免重犯错。

**展开**：
### Layer 1 — 为什么 / 背景

单次 LLM 推理有一个根深蒂固的问题：它不知道自己对不对。它输出的每个 token 都是"在当前概率分布下最合理的下一个"，而不是"经得起检验的"。Reflection 给了 Agent 一个"后视镜"——执行完回头审视自己的推理链和结论，拿外部证据校准。Memory 让这个校准的成果不丢——下次同类任务，直接从记忆里调"上次怎么错的、后来怎么纠正的"，避免重复踩坑。

### Layer 2 — 怎么做 / 机制

**Reflection 的两种落地方式**：

1. **内省式（Self-Reflection）**：让同一个 LLM 对自己的输出做批判——"这个诊断哪里证据不足？有没有遗漏的检查？"。优点是轻量，缺点 LLM 可能"为自己的错误强行辩解"（自我合理化）。
2. **外部信号式（Critic/Verifier）**：给 LLM 的结论喂入结构化的矛盾信号和跨源证据，让 LLM 在"铁证如山"的情况下被迫纠错。OpsPilot 的 critic 节点就是这种——它自己不算分，读上游算好的质量分和矛盾信号，按阈值做裁决。

**Memory 的分层**：

- **短期 Memory**：当前对话上下文窗口内的历史。容量有限（典型的几十到几百 KB），对话越长越容易被顶出去。
- **工作 Memory（Working Memory）**：当前任务的状态快照（当前步数、已取到哪些证据、loop_count 到了几轮）。OpsPilot 里就是 IncidentAgentState 的 47 个字段——但随着节点推进持续被覆盖（LastValue），所以要靠 checkpoint 把关键状态持久化。
- **长期 Memory（Long-term Memory）**：向量库 + RAG 检索。把历史故障的"工单特征+证据指纹+最终根因+处置方案"embedding 入库，新故障进来先查"以前遇到过没"。关键：不是存整段对话，而是存结构化摘要——故障类型、环境、关键证据、采用的处置动作、结果。
- **Episodic Memory**：记载"事件序列"——不是只记结论，还记"排查过程中走了哪些弯路、哪些假设被证伪了"。这对诊断类 Agent 特别值钱：下次遇到类似信号，可以直接跳过已被证伪的假设。

### Layer 3 — 坑 / 边界 / 追问预判

- **Reflection 不总是有效的**：LLM 自我批判的输出质量和它被训练的方式强相关——它被训练成"迎合用户"，而非"质疑自己"。所以 Reflection 必须有外部锚点（工具返回的真实数据、跨源证据矛盾）约束，不能纯靠自省。
- **Memory 的关键取舍：存什么 vs 怎么检索 vs 记多久**。存太多 → 检索噪声大、相关记忆被淹没；存太少 → 漏关键经验。记太久 → 旧知识过时（环境、架构变了）；丢弃太快 → 低频但高价值的经验丢失。
- **Memory 更新需要触发机制**：不是每次执行都全量存——只在"执行结果出人意料"（验证失败、critic 裁决非 PASS、人工介入）时主动写入。日常的 PASS 只做微量更新（更新置信度、频率计数），避免存储膨胀。
- **Reflection 和 Memory 的正反馈风险**：错误 Reflection 结论写入 Memory → 未来类似任务被误导 → Reflection 在此误导下再次犯错 → 恶性循环。解法：Memory 里的每一条经验都标注"来源"（哪次 run、置信度），允许人工标注/纠错/降权。

### Layer 4 — 同类变式

- **Reflection + Tool Use 的组合**：Reflection 不只看最终结论，也可以看中间步骤——"我选的这个工具对吗？参数对吗？返回结果符合预期吗？"这种"过程级 Reflection"比"结果级 Reflection"更有纠错价值。判断"预期 vs 实际"的偏差是纯代码能做的（不烧 token）。
- **Memory 的 RAG 退化**：如果 Memory 检索的 top-k 不够精准，Memory 就降级为"无关噪音"而不是"有用经验"。所以 Memory 检索的质量 = RAG 检索的质量——需要同样的 query 改写 + 混合检索 + rerank 机制。

**项目印证**：
- **OpsPilot**：critic 节点 = Reflection 的工程落地（不是纯内省，是拿 aggregate 算好的质量分+矛盾信号做裁决）。retrieve_memory 节点 = 长期 Memory（RAG 检索历史故障）。aggregator 的跨层差分定位表 = 过程级 Reflection——在取证阶段就发现"日志炸了但 K8s 健康→应用层故障"，而不等到 diagnose 输出后再反思。critic 的 4 路裁决中 CONTRADICTION 优先级最高——外部矛盾信号优先于自评的质量分，这正是"Reflection 需要外部锚点"的工程体现。Loop guard 防 Reflection 无限循环：2 圈摆不平就转人工 + 压低置信度，防止错误 Reflection 结论污染 Memory。
- **应用生成平台**：RAG 检索相似历史修改案例 = Memory 机制；Planner 执行后的校验回退 = Reflection。
- **前端测试域**：自愈 agent 修复后沙箱重跑 = Reflection（不靠自评"我觉得修好了"，靠"浏览器真的跑绿了"）。失败案例进题库 = Memory（下次改版脚本失效时，agent 知道"上次遇到类似结构问题是怎么修的"）。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-critic仲裁打分机制.md、实战-2026-06-10-deepagents范式与项目对标.md
> 🏷️ 覆盖题号：Reflection / Memory / agent 冲突 / 单 vs 多 Agent（~12 次）

---

## M15 · 工具调用链路

**Kernel**：用户指令→意图解析→工具选择(名称+参数 schema)→参数提取(LLM 填 JSON)→API 调用→结果解析→反馈给 LLM→决定下一步。关键设计：工具描述要精确(给 LLM 的 function definition)、错误要结构化返回、幂等防护。

**展开**：
### Layer 1 — 为什么 / 背景

工具调用是 Agent 从"能聊"到"能干"的质变——没工具，Agent 只能在训练数据的知识范围内推演；有工具，它能查真数据、改真系统。但这根链条上每一步都可能断：LLM 选错工具、填错参数、工具超时或报错、返回结果 LLM 无法解读、同一个动作被重复执行……工具调用链路的工程复杂度全在这些"出错以后怎么办"上，不在"正常流程"上。

### Layer 2 — 怎么做 / 机制

工具调用全链路 7 步：

1. **工具定义（Function Definition）**：给 LLM 的工具描述要精确到它能正确选型和填参——name、description（一句话说明用途 + 何时使用 + 何时不用）、parameters（JSON Schema，含 type/enum/required/constraints）。示例写得好不好，直接决定 LLM 填参质量。
2. **工具注册（Tool Registry）**：维护"工具名→实现函数+schema+权限等级+超时时间"的映射表。运行时动态注入给 LLM 的工具列表不是全量的——按当前场景（env/service/风险等级）裁剪，避免 LLM 在 50 个工具里选错。
3. **LLM 选工具+提参**：LLM 拿到工具定义列表和当前上下文，输出 function call（工具名 + JSON 参数）。这一步最耗 LLM——不是选对工具就行，参数要填对、取值范围要对、必填不能漏。
4. **网关校验（Tool Gateway）**：调用工具前的一道硬关卡。校验内容：工具名是否在注册表里（防幻觉工具名）、参数是否匹配 schema（类型/必填/枚举值）、权限是否满足（当前用户/env 能不能调这个工具）、是否超频（限流）、参数是否含敏感信息（脱敏）。校验失败 → 不调工具、返回结构化错误给 LLM 让它重填。
5. **幂等检查 + 执行**：写操作在执行前查幂等键——`idem_key = sha256(run_id + tool_name + params)`，如果同一键已执行过（返回过成功）→ 直接返回缓存结果，不重复执行。读操作跳过幂等检查。
6. **结果解析 + 审计**：工具返回的原始数据做标准化处理——截断过长内容、脱敏敏感字段、附加 `{success, elapsed_ms, error_code}` 元信息。每笔调用落审计日志（谁在哪次 run 调了什么工具、入参哈希、结果摘要）。
7. **结果回灌 + LLM 解读**：标准化的工具返回注入 LLM 的上下文，LLM 解读结果并决定下一步（继续调其他工具、输出结论、或声明信息不足需要补充）。

### Layer 3 — 坑 / 边界 / 追问预判

- **参数 schema 写得太简略是最大坑**：只写 `{"type": "string"}` 不够。必须写清楚：格式（ISO8601 时间/正则/mime type）、取值范围（1-100）、默认值、互斥关系（给 A 就不能给 B）。LLM 是"按示例模仿"，不是"按约束推理"——一个精心写的 example 胜过一段详细的 constraints 文字。
- **工具返回失败时 LLM 会怎么反应？** 如果返回是"Something went wrong"，LLM 可能放弃、可能换个工具乱试、可能编造结果。所以错误必须结构化：`{"error_code": "TIMEOUT", "retryable": true, "suggestion": "缩小时间窗口至 5 分钟重试"}`——让 LLM 知道"这是暂时的还是永久的""该重试还是换工具"。
- **幂等是写操作的命根子**：网络重试、resume 续跑、人工审批后重新执行——同一个动作可能在多个时机被触发。没有幂等 = 可能回滚两次、重启两次、建两份 MR。幂等键的粒度：太粗（按 run_id）→ 同一次 run 的不同步骤被当重复；太细（每次生成新 UUID）→ 失去去重作用。OpsPilot 的粒度是 `sha256(run_id + action_type + params)`。
- **工具返回内容过大**：日志查询返回 10 万行，全灌进 LLM 上下文 → 超大 token 消耗 + 关键信息被淹没。解法：工具层做预聚合（计数/TOP-N/时间分布），对长内容做滑动窗口摘要。

### Layer 4 — 同类变式

- **多工具路由选择**：当 LLM 面对 30+ 个工具时，先选工具、后填参数的两阶段比直接填参准确率高。可以加一层 Router/Classifier 把任务先分到"查日志/查指标/查 K8s/查部署历史"四个领域，再在领域内选具体工具。
- **工具调用的 HITL 分级**：只读工具 → 自动执行 + 审计；修改工具 → 自动执行 + 幂等 + 审计；高风险写操作 → 生成动作方案 → 卡人工审批 → 审批通过后才到网关+执行。OpsPilot 的 risk_gate 就是做这个分级。

**项目印证**：
- **OpsPilot**：完整实现了上述 7 步链路。Tool Gateway（`backend/app/tools/gateway.py`）做 schema 校验 + 重试 + 审计 + 脱敏——这是工具调用链的安全锚点。ControlledExecutor（`backend/app/services/executor.py`）做幂等执行 + 审计——同一动作 resume 两次不会重复执行。risk_gate 做工具调用前的风险分级——读操作放行、写操作分 LOW 自动/HIGH 审批/BLOCKED 拦截。evidence_fanout 的并行取证 = 一组只读工具并发调用（asyncio.gather），每路独立超时、失败不串扰。
- **应用生成平台**：Planner 生成的修改计划本质是"工具调用序列"——每一步对应一个代码修改操作，执行前有结构化校验，校验失败回退 Router 重新规划。
- **前端测试域**：自愈 agent 调用 Playwright 和代码编辑工具，每次修改定位后必须沙箱重跑——如果重跑变绿，工具调用才算成功；如果重跑失败，错误信息（具体哪个选择器找不到）结构化为下一轮 Thought 的锚点输入。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-opspilot全旅程主干.md、推导链-2026-06-15-什么是harness与怎么搭评测.md
> 🏷️ 覆盖题号：工具怎么定义注册调用 / function calling / 工具选择 / 调用安全（~12 次）

---

## M16 · LangChain vs LlamaIndex 对比

**Kernel**：LangChain = 通用 LLM 应用框架(Chain/Agent/Tool 抽象)，适合需要复杂编排的场景。LlamaIndex = 专注数据索引与检索(数据连接器+索引+查询引擎)，适合 RAG 为核心的系统。两者不互斥，常一起用。

**展开**：
### Layer 1 — 为什么 / 背景

2015 年 Fred Brooks 在《人月神话》中写道："软件工程的核心难题从没变过——让一群人对'什么算做对了'达成一致。"Agent 工程时代同样适用。框架选型的本质不是"哪个框架更好"，而是"你的系统复杂度分布在哪"——复杂度在编排 → LangChain/LangGraph；复杂度在检索 → LlamaIndex；两者都要 → 组合用。

### Layer 2 — 怎么做 / 机制

**三者的定位和核心差异**：

| 维度 | LangChain | LlamaIndex | LangGraph |
|------|-----------|------------|-----------|
| 核心抽象 | Chain/Agent/Tool（链式/代理/工具） | Data Connector + Index + Query Engine（数据连接器+索引+查询引擎） | StateGraph + Node + Edge（状态图+节点+边） |
| 适合场景 | 通用 LLM 应用（客服、分析、摘要） | RAG 为核心的系统（文档 QA、知识库） | 复杂有状态 Agent（多步推理、分支回退、HITL） |
| 编排模型 | DAG 链（线性/分支，无环） | — | 有向状态图（支持环、条件分支、并行） |
| 底层引擎 | LCEL (LangChain Expression Language) | — | Pregel/BSP（Bulk Synchronous Parallel） |
| RAG 能力 | 有但不深（通过社区集成） | 核心能力（分块策略/索引类型/检索模式一应俱全） | 不内置 RAG（需自己拼或接 LlamaIndex） |

**LangChain 的核心价值**：标准化了 LLM 应用开发的常用模式——Prompt Template、Chain（把多个步骤串成流水线）、Agent（选工具+调用的 ReAct 循环）、Memory。但它的 DAG 编排有天然限制——**不支持环**（无法从步骤 5 退回到步骤 2），所以复杂 Agent 需要 LangGraph。

**LlamaIndex 的核心价值**：把 RAG 的每个环节都封装成了可配置模块——数据加载（20+ 数据源）、索引类型（向量索引/摘要索引/树索引/关键词索引等 8 种）、检索模式（混合检索、递归检索、agentic 检索）、后处理（rerank/去重/过滤）。如果你要做的事是"把一堆文档变成可问答的知识库"，LlamaIndex 是最高效的选择。

**LangGraph 的核心价值**：走底层精细控制路线。你的 StateGraph 被 `compile()` 编译成 Pregel 图——State 字段变 channel、节点变 actor、边变 channel 订阅关系——然后在 BSP 引擎上按 super-step 推进。它支持 LangChain 做不到的三样：**环（回边）、条件分支、并行扇出**。OpsPilot 的 critic 回边和 verify 重试环，正是这三样的直接体现。

### Layer 3 — 坑 / 边界 / 追问预判

- **LangChain 最大的坑：抽象层太厚**。Chain 套 Chain 套 Agent，一行代码背后调了 5 轮 LLM，Debug 时完全看不见它到底发了什么给模型。"任何把 prompt 藏起来的魔法封装都是债"——好的框架应该让你随时能看见最终发给模型的完整文本。
- **LlamaIndex 不是通用 Agent 框架**：它做检索是顶尖的，但做复杂编排（多步推理+工具调用+审批+回退）不是它的强项。别拿它做 LangGraph 的活。
- **选型口诀**：要**快速起步**→ LangChain；要**底层可控状态机**→ LangGraph；要**开箱即用的 RAG**→ LlamaIndex；要**自主跑复杂长任务**→ deepagents（LangChain 出的、建在 LangGraph 之上的高层 harness）。

### Layer 4 — 同类变式

- **LangGraph 底层 Pregel/BSP 模型**：三个铁律——① super-step N 的 channel 更新，只有 N+1 才能看到；② 一个 step 期间 channel 不可变；③ 更新只在 step 之间统一 apply。这意味着：并行节点读到同一份冻结快照，不存在"并发写冲突"——除非两个节点在同一步写同一个 LastValue channel（框架直接抛异常）。
- **为什么不用 deepagents 而用 LangGraph 手搓**：deepagents 是 opinionated harness（框架替你把规划/子代理/上下文管理做主了）。OpsPilot 要的是确定性编排 + 可控的自建 checkpoint/HITL（0.0.55 没原生 interrupt），所以选更底层的 LangGraph 自己编排——把"框架替我做主"换成"我逐节点掌控"。

**项目印证**：
- **OpsPilot**：选 LangGraph 核心理由——需要**环形图**（critic 退回到 evidence_fanout/planner）、**条件路由**（risk_gate 4 路、verify 3 路）、**HITL 中断续跑**（approval 挂起→resume 续跑）。LangChain 的 DAG 链做不到环和条件回退，LlamaIndex 的强项在检索不在编排。RAG 部分（retrieve_memory）在节点内部走两阶段检索（粗排+rerank），是 LangGraph 编排 + 自建检索的组合，没有引入 LlamaIndex。
- **应用生成平台**：RAG 检索相似案例时，可以考虑 LlamaIndex 做索引层——但实际走了更轻的方案（直接向量库 + rerank），没上 LlamaIndex 那套完整 ETL 管线。
- **前端测试域**：不需要 RAG 框架，编排靠 opencode 的 agent 命令 + skill 机制，属于平台级编排而非框架级编排。

> 📎 素材：题库/母题骨架-一页纸.md、langgraph底层-三层映射与Pregel.md、实战-2026-06-10-deepagents范式与项目对标.md
> 🏷️ 覆盖题号：LangChain vs LlamaIndex / LangGraph 优势 / 框架选型（~10 次）

---

## M17 · Prompt 设计方法论

**Kernel**：三板斧——角色设定(你是一个…)、任务指令(具体做什么/不做什么)、输出格式(JSON schema/模板)。高级技巧：few-shot(给 2-3 个示例)、CoT(加"让我们一步步思考")、constraint decoding。迭代方法：写→跑 10 case→看 badcase→改 prompt→再跑，直到稳定。

**展开**：
### Layer 1 — 为什么 / 背景

Prompt 是 AI 应用的"源代码"。和传统代码不同，它的行为不是确定性的——同样的 prompt 在不同时间、不同温度参数下输出不同。所以 prompt 工程的核心不是"写一次完美的 prompt"，而是**建立一套能持续度量和改进 prompt 的机制**。没有评测集的 prompt 优化是盲改——你不知道每次改动是变好了还是变坏了，还是只在这一个 case 上碰巧变好。

### Layer 2 — 怎么做 / 机制

**三板斧（每个 prompt 必须有的三层）**：

1. **角色设定（Role/Preamble）**：一句话定边界——"你是一个 SRE 故障诊断专家，擅长从日志、指标、部署历史中交叉定位根因"。角色设定不是随便写的，它影响模型的"默认行为分布"——专家角色会让它倾向于给出技术细节而非泛泛而谈。
2. **任务指令（Task）**：三个要素——**做什么**（"分析以下证据，给出最可能的根因假设"）、**不做什么**（"不要猜测你没有看到证据支撑的假设""如果信息不足，明确说需要补充什么信息，不要硬猜"）、**优先级**（"矛盾信号 > 置信度 > 覆盖度"）。"不做什么"比"做什么"更重要——约束住了，自由度再大也不闯祸。
3. **输出格式（Output Format）**：给 JSON Schema / Markdown 模板 / 枚举约束。生产级要上四层兜底——① prompt 给 schema+few-shot ② 约束解码/JSON mode（从源头保证合法）③ Logit Bias 限定 token（分类场景）④ 后处理校验+失败重试。

**高级技巧**：

- **Few-shot（带示例）**：给 2-3 个完整的"输入→输出"示例，远比用文字描述"输出应该长什么样"有效。LLM 是"按示例模仿"的动物，不是"按约束推理"的机器。选示例的原则：覆盖成功 case(正向)、常见错误 case(负向)、边界 case(模糊输入该怎么处理)。
- **CoT（思维链）**：加一句"请一步步分析"，模型会把推理过程写出来→最终答案。不仅提高准确率，还提供了可解释性——你可以看它推理的哪一步出了问题。
- **Constraint Decoding（约束解码）**：不是 prompt 层面的技巧，而是在生成 token 时强制只能从允许的 token 集合里选。对结构化输出（分类/JSON）效果好，但对自由文本生成不适用。

**迭代方法**：写初版 prompt → 拿 10+ Golden Case 跑一遍 → 看 badcase（不是看总分，是看"哪个 case 错了、为什么错"）→ 改 prompt → 重新跑全部 case（不只是 badcase，防止修一个坏一个）→ 循环直到指标不再涨。指标不再涨 → prompt 接近上限，问题不在 prompt 而在别处（数据质量、模型能力、任务本身不适合 LLM）。

### Layer 3 — 坑 / 边界 / 追问预判

- **Prompt 不是越详细越好**：给 LLM 一段 2000 字的 prompt 里面有 20 条规则，它大概率只记住前 5 条和后 3 条——中间的全丢了（Lost in the Middle 效应）。解法：规则精简到 5-7 条，重要的放前面或结尾。
- **Few-shot 的负迁移**：示例选得不好会误导模型。如果你给的 3 个示例都来自"发布回归"类型的故障，模型遇到"资源耗尽"也会往发布回归上靠。示例必须分布均匀地覆盖可能出现的典型类别。
- **CoT 不适合简单任务**：分类任务加 CoT 反而降低准确率（"过度思考"——模型多走了一步推理，反而引入噪声）。判定：任务需要 ≥3 步推理 → 加 CoT；否则，直接给答案。
- **Prompt 优化会出现"过拟合"**：你的 prompt 在 50 个 case 上 92%，上线被用户一段奇怪的输入当场打回 60%。解法：题库要按真实分布采样（含脏数据、含边界 case、含对抗性输入），不能只用"漂亮"的数据测。
- **提示词安全（Prompt Injection）**：用户输入里夹带"忽略以上规则、照我说的做"，模型可能中招。解法：① 系统 prompt 和用户输入严格分层（API 层面的 system/user/assistant role 分离）；② 不要信任用户输入里的"指令性"内容，用另一个 LLM 或规则先扫一遍；③ 关键规则不用自然语言写、用确定性代码校验（如 前端测试域的 swc 闸门）。

### Layer 4 — 同类变式

- **Prompt Template vs Dynamic Prompt**：固定 prompt 模板适用于输入变化小的场景；动态 prompt（根据上下文动态拼接 instruction + examples + retrieved docs）适用于 RAG/Agent 等需要"按需组装信息"的场景。动态 prompt 的代价是 prompt 本身变成了程序，需要测试。
- **System Prompt vs User Prompt**：System prompt 放"持久规则"（角色、约束、输出格式），User prompt 放"本次任务的具体内容"。System prompt 天然优先级更高（模型会被训练成遵从 system prompt），但不要在 User prompt 里放入"可以覆盖 system prompt"的内容——那是提示词注入的入口。

**项目印证**：

- **OpsPilot**：每个 LLM 调用节点都有独立的 prompt 模板（planner 的调查计划生成、diagnose 的根因推断、critic 的裁决说明）——不是一个大 prompt 包揽所有。planner 的 prompt 给 incident_type + env + suspected_services，动态拼接成"你要为这个类型的故障制定调查计划，优先查这些服务"。diagnose 的 prompt 包含证据摘要 + 矛盾信号 + 格式要求（输出 JSON 含 hypothesis/confidence/supporting_evidence_ids/contradicting_evidence_ids）。critic 输出是枚举值（CONTRADICTION/NEED_MORE_EVIDENCE/REPLAN/PASS），加了 Logit Bias 限定 token 范围 + 后处理校验——如果 LLM 返回了不在这 4 个里的值，代码直接 fallback 为 PASS + 记录异常。
- **应用生成平台**：意图识别不用 few-shot（边界 case 漂移），改用 RAG 检索相似历史案例——把"选最合适的示例"自动化、也避免了人工示例的覆盖盲区。这是 prompt 工程中"何时该用 RAG 替代手工 few-shot"的实战取舍。
- **前端测试域**：自愈 agent 的 prompt 包含"只改定位、不改断言"的死规矩——但这条规矩没只放在 prompt 里（prompt 软、模型想绕就绕），而是同时做成 swc 语法树校验闸门——提交前必须过。**"约束要在执行前生效，不能只靠 prompt"**——这是 prompt 工程最重要的边界认知。

> 📎 素材：题库/母题骨架-一页纸.md、实战-2026-06-10-critic仲裁打分机制.md、ai_harness_interview_handbook.md §8
> 🏷️ 覆盖题号：prompt 设计原则 / 优化技巧 / few-shot 何时用 / 怎么判断 prompt 到上限（~15 次）
