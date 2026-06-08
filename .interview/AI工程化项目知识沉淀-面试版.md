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

LLM 是被编排的算子，不是编排者本身。下一步做什么、是否结束、走哪条分支，必须由确定性的代码、状态机或人来决定。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 主链路不是让模型自由发挥，而是 Commands → Agents → Skills → Rules 的受控执行环境。Agent 负责理解和生成，平台负责任务顺序、权限、门禁、恢复和审计。 |
| 前端测试域 | 测试是否通过不由模型口头宣布，而由 Playwright 执行结果、trace、截图、退出码和覆盖脚本判断。 |
| 应用生成智能体 | Router 先做轻量分流，复杂任务才进 Planner；Planner 生成 DAG 后由 Executor 执行，不让一个大模型调用从头黑盒跑到尾。 |
| OpsPilot | LangGraph 图由 builder 中的条件路由控制：critic 决定 PASS / NEED_MORE_EVIDENCE / REPLAN / CONTRADICTION，risk_gate 决定 BLOCKED / NEEDS_APPROVAL / executor，verify 决定 SUCCESS / RETRYABLE_FAILURE / FATAL_FAILURE。 |
| Vibe Dev Toolkit | task.json 状态机和任务选择算法控制恢复与派发，本地 demo 能把"控制权归系统"展示成可见文件状态。 |

面试锚点：我不会说"让 AI 自己判断做完没有"。我会把 AI 的输出视为候选结果，把流程推进权放在状态机、规则、测试和审批上。

### 2.2 约束前置，而非事后纠偏

约束必须在执行前生效，而不是等模型已经调错工具、改错文件、触发高风险动作之后再补救。

| 项目 | 体现 |
|---|---|
| 企业 Harness | Rules 层承载权限、目录边界、质量门禁、熔断和审批要求，平台统一治理，业务团队在边界内配置流程。 |
| 前端测试域 | AC、断言映射、覆盖校验先定义清楚，测试生成和测试通过都必须落到这些约束上。 |
| 应用生成智能体 | 简单请求不进入重 Planner，低相关度 RAG 不注入 Planner，生成阶段要求每步溯源到需求或范式。 |
| OpsPilot | risk_gate 在执行前判断动作风险；real 模式下不可用能力 fail-closed；高风险 rollback 进入 approval_interrupt。 |
| Vibe Dev Toolkit | 工具链内核不允许内嵌 hoo-desk / login / isForget 这类业务词，项目知识只能来自 profile 和 AC。 |

面试锚点：约束不是 prompt 里的"请注意"，而是运行时过不去的门禁。

### 2.3 契约优先于对话

Harness 里流动的应该是结构化产物，不是自然语言聊天记录。只要下游要机器消费，就必须有契约。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 需求、设计、任务、测试、交付都应输出标准化工程产物，而不是让 Agent 之间靠散文交接。 |
| 前端测试域 | AC 是结构化输入；每条断言要能回指 AC；覆盖报告能机器判断 MISSING / HOLLOW / ORPHAN。 |
| 应用生成智能体 | Router 输出结构化意图和命中的 scene→plan 范式，Planner 输出任务 DAG，Executor 按 DAG 执行。 |
| OpsPilot | IncidentAgentState、RootCauseCandidate、RemediationPlan、EvidenceItem 等结构化对象让节点之间可组合、可持久化、可测试。 |
| Vibe Dev Toolkit | 契约信封和 zod schema 让本地工具链可以校验输入输出，而不是靠模型"看起来写对了"。 |

面试锚点：契约的价值不是好看，而是让评测、回放、复用和定位错误都变成可能。

### 2.4 证据高于断言

LLM 最危险的不是会错，而是会自信地说"我做完了"。所以决策必须看证据，不看自我报告。

| 项目 | 体现 |
|---|---|
| 企业 Harness | 质量门禁看测试报告、执行记录、截图、trace 和缺陷记录，而不是看 Agent 的口头总结。 |
| 前端测试域 | 三防线专门对抗"没跑却说跑了""断言空洞""只测 happy path"。 |
| 应用生成智能体 | 生成质量不能只靠模型说代码没问题，需要 lint、typecheck、build、预览和用户返工率反馈。 |
| OpsPilot | evidence_fanout 收集工具证据，diagnose 产出候选根因，critic 复核，verify 用部署状态、健康状态、流量指标判断修复是否有效。 |
| Vibe Dev Toolkit | 本地 demo 用 Playwright 真跑结果和覆盖脚本给面试官看，不靠口头解释。 |

面试锚点：模型输出是 Claim，工具和测试产物是 Evidence，系统门禁基于 Evidence 做 Decision。

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

## 3. 王牌展开一：前端测试三防线

## 4. 王牌展开二：应用生成智能体

## 5. 王牌展开三：OpsPilot

## 6. Vibe Dev Toolkit：本地可演示复刻

## 7. 高频面试问法与回答锚点

## 8. 收口表达
