# Harness 知识地图

> 用途：把 `.interview/interface` 下的 6 篇原始文章 + `.interview/battle-plan` 下的手册、批判文、实战沉淀，按"主题"摆在一张表里，看清楚每个主题现在有没有"原始素材→批判验证→项目落地"这条完整链路。这是一张持续更新的地图，不带日期；带日期的"实战沉淀"文章是地图上的具体节点。
>
> 三层来源的含义：
> - **A 原始素材**：第一次接触这个概念的地方，可能掺了营销话术，未经验证。
> - **B 批判/验证**：有人去核对过 A 里的说法，指出哪些是真的、哪些是吹的，或者提供了一个更扎实的替代框架。
> - **C 提炼结论/项目落地**：把 A/B 的内容收敛成一句话结论，并且/或者映射到 OpsPilot 真实代码。这一层是面试时真正能讲的"实战沉淀"。

---

## 主题1：Harness 是什么 / 三层架构 / Agent=Model+Harness（定义篇）

- **A**：`.interview/interface/harness核心定义和行业定位.md`（全篇）—— 核心定义、Prompt→Context→Harness 三代范式、信息层/执行层/反馈层三层架构、六大组件、Harness vs LLMOps。
  - 补充：`ai_harness_interview_handbook.md` §0（三十秒开场白）、§1（名词表里的 Harness 定义）—— 同一个核心结论的"人话版"。
- **B**：`实战-2026-06-15-Harness控制面vs写路径治理.md` —— 验证了"Agent=Model+Harness"这个**结论本身是对的**（harness=控制面），但白皮书那篇（见下）里六大组件的具体代码示例、92% 数字等是营销虚构。
  - `ai_harness_interview_handbook.md` §3（业界格局：Anthropic/OpenAI/LangChain 三个真实代表作各自的"招牌设计"）提供了"六大组件"的**真实版对照**，可以替代白皮书里那套虚构实现。
- **C**：推导链 `推导链-2026-06-15-什么是harness与怎么搭评测.md` Chain A 第一步（"模型本身不值钱，值钱的是包在模型外面那层工程"）+ handbook §0 是这个主题最浓缩的两句话。
  - **缺口**：没有把"三层架构/六组件"逐项映射到 OpsPilot 13 个节点的项目落地文章（对应母题骨架 M10 的项目锚点说明）。

---

## 主题2：Skills + CLI + Harness 金字塔 / 企业级落地（ICCR / 风险分级 / 标准化接入四步法）

- **A**：`.interview/interface/harness+skill+cli.md`（金字塔三层定位、9 步协同流程、架构全景图）
  - `.interview/interface/harness行业最佳实践与skill、cli.md`（ICCR 原则、风险分级表、Skills/CLI 标准化接入四步法、企业级规模化最佳实践、避坑指南）
- **B**：**暂无专门的批判/验证文章**。`ai_harness_interview_handbook.md` §5（企业级架构：四层架构/三个硬问题/华为特色）是一个更扎实的企业级框架，可以视为对这两篇"金字塔图"的**升级替代**，但没有逐条核对这两篇里的具体数字（如"准确率提升 40%+"、"成本降低 80%+"）。
- **C**：**无**。这两篇是纯知识介绍，没有映射到 OpsPilot 的实战沉淀。
  - **状态**：候选缺口，但 OpsPilot 本身不是"Skills 市场/CLI 网关"场景，这个主题更像是**背景知识储备**而非项目实战素材——是否值得单独写一篇 C 层文章，取决于面试是否会单独问"Skills 和 CLI 怎么接入"这类纯架构题。

---

## 主题3：Guides & Sensors / Computational vs Inferential / 三种 Harness 类型（Birgitta 独立框架）

- **A**：`.interview/interface/harness for code agent.md`（Birgitta Böckeler 精读全篇）—— Guides/Sensors、Computational/Inferential 检查、Maintainability/Architecture Fitness/Behaviour 三种 Harness、Steering Loop、Harnessability、Ambient Affordances、Harness Templates。
- **B**：这篇本身就是对 Martin Fowler 原文的精读转述，相对于"营销向"的白皮书（主题1的 A 层）来说，**它自己就是一个独立可信的框架**，不需要额外的批判文章。
- **C**：**无**。
  - **状态**：候选缺口。不过有一条潜在连接没被点破——Computational vs Inferential 这对概念，和评测体系里"能用代码判的绝不用模型判"（主题5 的核心原则）其实是**同一件事的两种说法**。目前没有文章把这两个主题串起来。这个连接本身可能就是一个不错的"加分项"，但不构成独立母题。

---

## 主题4：读路径 vs 写路径治理（幂等键 / 前置校验 / HITL / loop guard）

- **A**：`.interview/interface/harness demo.md`（SecurityGateway / COMMAND_WHITELIST 等代码雏形，个人 3 天 harness checklist）
  - `.interview/interface/AI Agent Harness Engineering 技术白皮书.md`（安全治理章节：`check_permission` 空壳、`detect_prompt_injection`——这篇后来被证实大部分是营销虚构）。
- **B**：`实战-2026-06-15-Harness控制面vs写路径治理.md`（核心文章）—— 完整批判白皮书（92%数字/OpenHarness/A_agent公式/进程内字典限流/hset覆盖bug/check_permission空壳均查无实据），提出读写路径框架，并逐条映射到 OpsPilot 真实代码：
  - `backend/app/services/executor.py:62,64-85,88,120`（幂等键查重 + 前置校验 + 审计）
  - `backend/app/graph/nodes/__init__.py:1074-1133`（critic 4路裁决 + loop guard max 2）
  - `backend/app/graph/nodes/__init__.py:1208`（risk_gate 审批门）
  - `backend/app/graph/nodes/__init__.py:1321`（approval_interrupt HITL 落库）
  - `backend/app/tools/gateway.py:840,860,1063,1082`（schema 校验/重试/audit/脱敏）
- **C**：推导链 Chain A 后半段（harness=控制面5件事 → 读路径只需限流/追踪/测试，写路径多4件事：幂等键/前置校验/HITL/loop guard）。
  - **状态**：覆盖**最完整**的主题之一。已在 `实战沉淀-索引.md` 标记为"新母题候选"，对应母题骨架 A6/A9。

---

## 主题5：Agent 评测体系方法论（题库 / gold set / 冻结世界 / 北极星向量）

- **A**：`ai_harness_interview_handbook.md` §7（评测体系：三层塔/金标集kappa/统计纪律/CI改造）+ §1 名词表里的评测相关术语（Eval/判卷器/金标集/Flaky/Goodhart/快照回放/变异测试）。
- **B**：`实战-2026-06-13-评测体系演示-前端测试能力域.md`（设计稿：编写/执行/修正/守护四段闭环、三层塔、E1/E2/E3消融实验验证了"冻结世界"和"自愈skill"的具体收益数字、CI评测门禁两道门）
  - `实战-2026-06-10-评测指标陷阱-命中率与margin.md`（验证了一个具体陷阱：命中率封顶后看不出优化效果，margin才是真信号；A/B/C消融 margin 0.21→0.31→0.51）
  - `e2e测试/何为自愈？.md`（"为什么需要自愈"的动机说明，是 E2 自愈消融实验 60%→83% 的前传：先讲清"红"分真红/假红——假红=定位过期非应用坏，45%夜间红灯是假红；自愈只清假红、绝不碰断言；"只许改定位、碰断言一律作废"是防作弊闸门。这一篇直接把"自愈agent"翻译成 handbook §7 的三类题：分诊准确率=业务题，不污染报告=行为题+防作弊闸门当判卷器，抗注入删断言=安全题）
- **C**：`实战-2026-06-14-如何评测一个agent方法论.md`（8步评测框架母本，带"面试速记+诚实边界"）
  - 推导链 Chain B（评测复杂度由"对错难判断"逼出来 → 需要裁判 → 主客观分离 → 三层裁判 → 题库 → gold set → 冻结世界 → 北极星向量）。
  - **状态**：覆盖**最完整**的主题。已在 `实战沉淀-索引.md` 标记为"新母题候选"，对应母题骨架 M18。

---

## 主题6：多 Agent 编排与反馈飞轮（critic 仲裁 / deepagents 范式 / 数据反馈飞轮）

- **A**：`ai_harness_interview_handbook.md` §4（架构怎么选：用"招人"常识，0-4级分级表）+ §2（理论根基：Brooks定律、"多agent是不是悖论"的完整答案）。
- **B**：`实战-2026-06-10-deepagents范式与项目对标.md`（验证 OpsPilot 是手搓的 deep agent：Planning→planner节点、Sub-agents→evidence_fanout、File system→evidence持久化、HITL→risk_gate+approval_interrupt、Long-term memory→retrieve_memory+RAG、自我纠错→critic回边）
- **C**：`实战-2026-06-10-critic仲裁打分机制.md`（critic 4路裁决 + 质量分公式 avg×penalty×coverage，对应 M16 Reflection）
  - `实战-2026-06-10-数据反馈飞轮.md`（四层飞轮：写回闭环/在线人工打分/LLM-as-Judge补覆盖/离线Golden Set防回退）
  - **状态**：覆盖**最完整**的主题。已在 `实战沉淀-索引.md` 标记为"新母题候选"，对应母题骨架 M16/M17。

---

## 缺口诊断（对照 `题库/母题骨架-一页纸.md`）

### 结论先说：之前猜的"缺口在主题4/5"猜错了方向

主题4（读写路径治理）和主题5（评测方法论）反而是**覆盖最完整**的两个主题——A/B/C 三层都有扎实的文章，而且都已经在 `实战沉淀-索引.md` 里被标记为"新母题候选"。这点不奇怪：这两个主题都是"动作性"很强的话题（怎么管控写操作、怎么搭评测），天然会在做 OpsPilot 项目的过程中被逼出实战沉淀。

### 真正的缺口：主题1/2/3 停在"知识介绍"层，没有 C 层项目落地

| 主题 | A层 | B层 | C层（项目落地） |
|------|-----|-----|----------------|
| 1. Harness定义/三层架构 | ✅ 完整 | ✅ 有真实版对照 | ⚠️ 只有一句话结论，没有逐项映射到13节点 |
| 2. Skills+CLI金字塔/企业落地 | ✅ 完整 | ⚠️ 只有升级替代，无逐条核对 | ❌ 无 |
| 3. Birgitta独立框架 | ✅ 完整（本身已是B层质量） | — | ❌ 无 |
| 4. 读写路径治理 | ✅ | ✅ | ✅ 完整，已是候选母题 |
| 5. 评测方法论 | ✅ | ✅ | ✅ 完整，已是候选母题 |
| 6. 多Agent编排/反馈飞轮 | ✅ | ✅ | ✅ 完整，已是候选母题 |

### 对母题骨架（A6/A9/M10/M16/M17/M18）的具体核对

- **A6/A9**（LangGraph 0.0.55 自建 checkpoint/HITL）：主题4 已覆盖 HITL/approval_interrupt 部分，但 A6/A9 强调的"**自建 vs 原生**"这个对比角度，主题4的文章里没有专门点出来——patch 时需要补这一句。
- **M10**（核心组件锚点 OpsPilot 13节点）：主题1 是这个母题的"理论背景"，但目前没有逐项映射表（六大组件 ↔ 13节点）。这是一个可以快速补的小缺口，不需要新母题，补进 M10 的"知识基础"引用即可。
- **M16**（多Agent系统/Reflection）：主题6 覆盖良好，`critic仲裁打分机制.md` 已经是现成的 Reflection 案例。
- **M17**（框架对比/LangGraph选型）：主题1/2 里"为什么是 LangGraph 而不是其他框架"这个角度，目前**没有专门文章**——候选缺口，但也可能是面试中较低频的问题，优先级排后。
- **M18**（RAG/Agent评估体系）：主题5 覆盖最充分，是三个候选母题里素材最厚的。

### Step 2 建议（patch 母题骨架，留给下一步）

1. **三个已标记的候选母题**（"如何评测一个agent"对应M18、"Harness控制面vs写路径治理"对应A6/A9、"deep agent harness范式"对应M16/M17）是优先级最高的——素材已经齐了，只是还没有正式写进骨架。
2. 主题1（三层架构/六组件）**不单独成母题**，而是作为这三个候选母题共同的"理论背景锚点"，在骨架里加一条引用即可（例如 M10 的知识基础部分补一句"六组件↔13节点对照"）。
3. 主题2/3（Skills+CLI金字塔、Birgitta三种Harness类型）**暂不patch**——它们是背景知识储备，不构成 OpsPilot 项目的实战母题候选。除非面试明确会单独问"Skills/CLI企业接入"或"Maintainability/Architecture Fitness/Behaviour Harness怎么分类"这类纯概念题，否则优先级最低。
