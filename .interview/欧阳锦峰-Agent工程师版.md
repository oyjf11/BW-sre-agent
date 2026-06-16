# 欧阳锦峰

**男**｜**生日：**1996/04｜**手机：**13266847690｜**微信：**13266847690｜**邮箱：**Oyjf_@hotmail.com

## 个人优势

7 年软件研发及企业级系统建设经验，具备前端 / 全栈研发背景，近一年重点投入 AI Coding、Agent Workflow、SRE Agent 与企业级智能体工程化落地，能够把 AI 能力从 PoC 验证推进到内部试点、流程闭环和持续迭代。

核心判断：Agent 的可靠性不来自模型本身，来自 Harness——用确定性编排包裹非确定性推理，用结构化契约替代自然语言交接，用证据驱动的质量门控替代 LLM 的自我报告。在 AI Coding、企业应用生成、SRE 故障处置三个方向中，将这套认知从产品设计层落实到代码实现层。

理解 AI 产品落地的关键是围绕真实业务构建可控的任务编排、工具接入、质量验证与反馈迭代机制。参与过 Harness Engineering 体系从"能力工具化"到"流程编排化"再到"治理与评测"的完整建设路径，具备对 Context / Capability / Constraint 三层分离、能力原子化、状态外置与可恢复、证据链、质量门控和离线评测的实践理解。

兼具复杂中后台、低代码平台与 AI 工具链建设经验，能够将抽象能力沉淀为可复用的平台模块、流程规范和交付范式，推动 AI 产品在多团队试点中形成可验证结果。

## 工作经历

### 华为技术有限公司（科锐OD）

**2023-05 - 至今**
**AI Agent 工程方向核心参与者 / 前端开发工程师（OD）**

- 围绕企业内部 AI Agent 工程化与研发提效场景，参与 AI 智能体应用平台、AI 辅助研发工具链及低代码平台建设，负责 / 参与 Agent 工作流设计、Harness 体系建设、核心能力抽象、前端与平台能力落地及跨团队推进。
- 重点推动 AI Coding 工程化、企业轻应用生成、SRE 运维故障诊断与低代码平台智能化升级等方向从 PoC 验证走向内部试点和产品化演进。
- 长期承担复杂中后台、低代码平台和内部工具类系统的前端架构、组件抽象和交付体验优化工作。

### 爱问医联（深圳）有限公司

**2023-03 - 2023-05**
**前端开发工程师**

负责企业内部中台及小程序相关功能开发与维护，参与 React 中后台、小程序、旧系统迁移、组件封装与上线交付。

### 明源云科技有限公司

**2021-06 - 2022-11**
**前端开发工程师**

负责商业中心管理后台及会员端小程序相关功能开发与维护，参与 React 中后台、小程序、旧系统迁移、组件封装与上线交付。

### 云翰教育科技有限公司

**2019-06 - 2021-06**
**前端开发工程师**

负责家校管理后台、家校小程序、拼团小程序等业务系统开发与迭代，参与 Vue 中后台、移动端小程序、组件封装与性能优化。

## 项目经历

### AI 辅助研发提效工具包｜将 AI Coding 从个人提效升级为团队级工程化流程

**2025-03 - 至今**
**核心参与者**

- 面向产研团队在需求设计、编码、测试、代码检视、交付等环节中存在的流程割裂、重复工作多、AI 使用方式分散等问题，参与规划基于内部 OpenCode 的智能研发套件，推动 AI Coding 从个人提效工具升级为团队级研发基础设施。
- 参与产品能力拆解与流程设计，将研发全流程抽象为 Commands 任务入口、Agents 角色分工、Skills 标准能力、Rules 行为约束四层体系，覆盖需求解析、任务拆解、代码生成、Bug 修复、测试验证、Code Review、MR / CI/CD 与知识沉淀。
- **主导前端验证与证据能力域建设**：围绕前端 Bug 修复场景，将"前端验证"拆成测试范围识别、用例生成、环境准备、Playwright 执行、证据采集（截图/Console/Network/Trace）、失败归因（代码/环境/数据/用例/Flaky 五分类）、缺陷流转、修复复测 8 个原子节点；核心设计原则是证据高于断言——执行结果落成 evidence pack 而非 Agent 口头报告，LLM 可以撒谎，浏览器截图不会。
- 参与建设质量门禁、Plugin 观测和 Bad Case 迭代机制，将 Git Diff、越界修改检查、规范检查、问题分级、执行数据与用户反馈纳入闭环，持续反推规则、Skill、测试集和流程优化。
- 在典型后台功能试点中将前置研发环节耗时由约 2.2 天缩短至约 4 小时，试点覆盖 10+ 业务团队，通过测试验证与代码审查门禁保障交付质量。

### AI 智能体应用生成平台｜自然语言驱动的企业轻应用生成工具

**2025-05 - 至今**
**核心参与者**

- 面向企业内部轻应用搭建中配置成本高、定制开发周期长、业务人员上手门槛高等问题，参与规划 AI 智能体应用生成平台，推动原低代码平台从配置式搭建升级为自然语言驱动的生成式应用创建与修改流程。
- **主导 Router / Planner 分层 Agent 工作流设计与意图识别机制**：将自然语言需求拆解为意图识别、任务规划、页面生成、Schema 生成、SQL 建表 / 迁移、数据接入、预览验证、增量修改等阶段；设计场景化 RAG 意图增强机制，围绕历史修改场景、任务类型样例和平台执行规则沉淀语料，解决修改阶段意图识别不稳定问题（"把按钮改成红色" vs "加一个红色提交按钮"是两种不同 Planner 路径）。
- 推动结构化中间产物机制落地，将模型输出拆解为页面代码、字段 Schema、SQL 建表语句、路由配置、数据绑定逻辑等可承接产物，打通从需求输入到可运行页面渲染的核心闭环。
- 参与推进内部 UI 组件库、样式设计规范、构建规范、代码规范与沙箱依赖 GA 版本接入生成链路，基于 opencode service API 与 MCP 工具能力对齐内部平台标准。
- 负责 Sandpack 在线预览与调试体验建设，支持生成代码实时预览、错误反馈、热更新渲染和长代码调试。
- 推动项目从基础 Demo 演进至内部灰度试点，打通需求输入、应用生成、建表接入、预览调试、打包部署的 PoC 闭环；试点覆盖 10+ 个业务团队，累计生成 30+ 个应用原型，典型轻应用原型从需求描述到可预览耗时由约 1～2 天缩短至 30～60 分钟。

### AI SRE 运维智能体｜生产级故障诊断与处置 Agent Harness

**2025-10 - 至今**
**核心设计参与者（基于公司内部 SRE 场景的工程化实践项目）**

- 参与公司 AI 运维智能体方向的调研与方案设计，并基于相同 SRE 故障处置场景独立实现完整的 Harness 工程化验证项目，覆盖工单接入、故障定性、只读取证、根因诊断、质量门控、人工审批、受控执行、验证和 RCA 归档的端到端闭环。
- **设计并实现 14 节点 LangGraph Harness**：intake → triage → retrieve_memory → planner → evidence_fanout → evidence_aggregate → diagnose → critic → remediation → risk_gate → approval_interrupt / executor → verify → rca。拆分原则是单一职责、输入输出明确、读写隔离、失败可独立重试、节点可单独评测。
- **主导取证与质量门控链路设计**：将核心诊断段拆成 `planner → evidence_fanout → evidence_aggregate → diagnose → critic`。planner 基于结构化 `TriageResult` 和故障类型模板确定查什么，不让 LLM 临场决定关键路由；fanout 派出 logs / metrics / k8s / db / deployments 等 specialist agent 并行只读取证；aggregate 将多专家结果合成全局证据包并计算质量分；diagnose 只在证据约束下生成 2-3 个候选根因；critic 根据质量分、矛盾信号、候选置信度和 loop guard 决定 PASS、补证、重规划或转人工。
- **建设证据质量评估机制**：质量分不看单次工具是否返回，而综合专家覆盖度、专家置信度、降级惩罚和截断惩罚，避免"单点高置信"伪装成全局可靠；aggregate 同时输出 `cross_agent_causal_chains` 和 `contradiction_signals`，例如 logs/metrics 异常但 K8s 正常时，将其作为应用层故障约束，而不是直接阻断诊断。
- **实现 Tool Gateway 与多源只读适配体系**：围绕 MySQL、K8s、SLB、CMS 指标、OSS 等数据源收口工具调用，统一 schema 校验、超时重试、风险等级、审计落库、敏感字段脱敏和 tracing；支持 mock / real 双模适配器，real 模式下未接入真实适配器时 fail-closed，显式返回失败并影响证据覆盖度，避免 mock 数据污染生产诊断。
- **补齐可靠性与安全控制点**：GraphRunner 在每个节点完成后保存 checkpoint、持久化 evidence、写事件，支持中断恢复和前端进度追踪；approval_interrupt 通过 LangGraph `interrupt()` 暂停高风险动作，审批后用 `Command(resume=)` 恢复；ControlledExecutor 使用 call_id / action_id 幂等约束，避免恢复或重试导致重复执行；critic 默认最多"首轮取证 + 一次纠偏"，循环耗尽写入结构化终止原因并转人工。
- **建设离线评测框架**：通过 fixture 在 Tool Gateway 入口短路注入固定证据集，避免 mock 随机数据影响回归；采用确定性评分器（枚举等值比对而非 LLM-as-judge）和 Precision / Recall / F1 指标验证标准故障场景下的诊断稳定性；已完成 Phase 8 离线评测框架和真实 DeepSeek 单 case smoke 报告。
- 技术栈：Python / FastAPI / LangGraph / SQLite（开发）/ PostgreSQL（生产） / SSE / Docker / K8s（阿里云 ACK）

## 教育经历

### 深圳大学

**2014-09 - 2018-06**
核工程与核物理 · 本科 · 全日制

大学英语四级 / 六级

## 掌握技能

- **AI Agent 工程**：LangGraph（Python/TS）、Agent Workflow 设计、Harness Engineering、Human-in-the-loop、Checkpoint 持久化、Tool Gateway、幂等执行、证据链、质量门控、Loop Guard、Bad Case 管理、离线评测体系
- **AI Coding / Vibe Coding**：OpenCode、Claude Code、Codex、Skills / SubAgent、MCP、Prompt Engineering、Spec Driven Development、Harness Engineering、CLI / Runner
- **后端开发**：Python、FastAPI、asyncio、SQLAlchemy、PostgreSQL、Redis、Docker、K8s、SSE、后台任务、审计日志
- **前端开发**：JavaScript、TypeScript、Vue3、React、Node.js、Playwright、E2E 测试、Sandpack
- **平台与数据**：Supabase、PostgreSQL / RLS、多租户、SSO 鉴权、Schema 设计、SQL、低代码平台
- **可观测性**：LangSmith、Langfuse、结构化 Tracing、离线评测
