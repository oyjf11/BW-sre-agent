# round2 · RAG + Agent 结合（🅰️ 组重点题 · 9 题）

> 每题标注 📚 Agent 项目配套。项目印证具体到代码/架构细节。

---

### Q1 如何定义智能体（Agent）的「基础能力」？核心要素及依赖关系与评估标准

**一句核心**：四个核心——规划拆任务、记忆存长短期上下文、工具调用感知外部、反思自我纠错，LLM 是大脑、工具是手脚、记忆是状态、编排是骨架。

**展开**：
- **规划（Planning）**：把复杂目标拆成子任务 DAG。Plan-and-Execute（省 token 但纠错弱）vs ReAct（边做边规划，灵活但消耗大）。OpsPilot 取中间态：planner 出计划→执行→critic 打回可 replan。
- **记忆（Memory）**：短期 = 对话窗口内历史（易被顶出）；长期 = 向量库存结构化摘要。关键设计：不是什么都记，只记「故障类型+证据指纹+处置结果」。
- **工具调用（Tool Use）**：LLM 通过 function calling 选工具+填参→执行→结果回灌。要害不在能不能调，在调错了会怎样——需要 schema 校验、超时兜底、幂等防护。
- **反思（Reflection）**：执行完回头看「我刚才做得对吗」。必须基于外部信号（工具返回真实数据、跨源矛盾），不能纯靠 LLM 自省（会自我合理化）。
- **依赖关系**：规划产出交给工具执行→工具返回喂入记忆→反思校准记忆→规划下次避坑。四者不是并列模块，是按故障生命线串起的阶段工序。

**项目印证**：OpsPilot 13 节点把四件套拆成确定性流程——`planner` 做规划、`retrieve_memory`+RAG 做长期记忆、`evidence_fanout`+Tool Gateway 做工具调用（`backend/app/tools/gateway.py` 做 schema+重试+审计+脱敏）、`critic` 节点做反思（回边退回重查）。4 路裁决中 `CONTRADICTION` 优先级最高——外部矛盾信号优先于自评质量分，正是「Reflection 需外部锚点」的工程落地。

> 🏷️ M10
> 📎 素材：`实战-2026-06-10-opspilot全旅程主干.md`、`实战-2026-06-10-critic仲裁打分机制.md`

---

### Q2 如何设计 Agent 内部组件间的连接路径与通信机制？常见架构模式及优缺点

**一句核心**：组件间通过共享 State 传递结构化数据（非自然语言），编排靠条件路由而非 LLM 决策——确定性编排 > LLM 自由对话。

**展开**：
- **三种架构模式**：① 主从模式——主 Agent 拆任务，子 Agent 只读、互不商量（最安全可控）；② 对等协作——多 Agent 平等对话，跑偏不收敛风险极高；③ 辩论/投票——多出方案仲裁，前提是评判便宜可靠。
- **通信机制设计的两条铁律**：① 能走结构化数据就别走自然语言——每次 NL 传递必有信息丢失；② 子任务只读、互不依赖才可并行——改东西需要排他权限的，回去派一个人。
- **LangGraph 的 StateGraph 模型**：节点之间通过共享 State 传数据，路由由条件函数决定（不由 LLM 决定）。Pregel/BSP 底层三个保障：super-step N 的更新只有 N+1 能读到、step 期间 channel 不可变、并行节点读同一冻结快照无并发写冲突。
- **单 vs 多 Agent 的本质判据**：Brooks 定律——加人越多、沟通成本平方增长。只有当分工收益 > 沟通额外成本时才值。关键澄清：OpsPilot 的 13 节点不是多 Agent，是单 Agent 内部的确定性编排——节点间走共享 state，路由走规则不是 LLM。

**项目印证**：OpsPilot 选 LangGraph 而非 LangChain DAG 的原因——需要**环形图**（critic 退回到 evidence_fanout/planner）、**条件路由**（risk_gate 4 路、verify 3 路）、**HITL 中断续跑**（approval 挂起→resume）。节点不直接调用，全靠向 `IncidentAgentState` 的 47 个字段写 key、下游读 key 传递。5 个条件路由器是物理上的「可退回重来」实现。evidence_fanout 的并行取证是最安全的多 Agent 子模式——只读、互不通信、互不抢资源。

> 🏷️ M10 / M13 / M21
> 📎 素材：`实战-2026-06-10-deepagents范式与项目对标.md`、`langgraph底层-三层映射与Pregel.md`

---

### Q3 如何设计和实现可供 Agent 调用的外部工具？工具定义格式、注册机制与调用安全控制

**一句核心**：7 步全链路——JSON Schema 定义→注册表映射→LLM 选填→网关校验→幂等检查→执行→结果回灌，安全 = schema+重试+审计+脱敏+高危审批。

**展开**：
- **工具定义（Function Definition）**：给 LLM 的描述必须精确到能正确选型和填参——name、description（何时用 + 何时不用）、parameters（JSON Schema 含 type/enum/required/default/互斥约束）。一个精心写的 example 胜过一段详细的 constraints 文字。
- **注册机制（Tool Registry）**：维护「工具名→实现函数+schema+权限等级+超时」映射表。运行时注入 LLM 的工具列表不是全量的——按当前 scene/service/风险等级裁剪，防止 LLM 在 50 个工具里选错。
- **网关卡（Tool Gateway）**：调用前硬校验——工具名是否在册（防幻觉）、参数是否匹配 schema、权限是否满足、是否超频、参数是否含敏感信息需脱敏。校验失败→不调工具，返回结构化错误让 LLM 重填。
- **安全控制三级**：① 只读工具→自动执行+审计；② 修改工具→自动执行+幂等（`idem_key = sha256(run_id + tool_name + params)`）+审计；③ 高风险写操作→生成方案→卡人工审批→通过后才到网关+执行。
- **结构化错误返回**：不是 "Something went wrong"，而是 `{error_code, retryable: true/false, suggestion: "缩小时间窗口至5分钟重试"}`——让 LLM 判断是重试还是换工具。

**项目印证**：OpsPilot 完整实现了上述 7 步——Tool Gateway（`backend/app/tools/gateway.py`）做 schema 校验+重试+审计+脱敏，是整条链路的安全锚点。ControlledExecutor（`backend/app/services/executor.py`）做幂等执行+审计，同一动作 resume 两次不重复执行。risk_gate 做调用前风险分级——`LOW_ONLY` 放行 / `NEEDS_APPROVAL` 卡审批 / `BLOCKED` 拦截。evidence_fanout 的 4 路并行取证 = asyncio.gather 并发只读调用，每路独立超时、失败不串扰。

> 🏷️ M15
> 📎 素材：`实战-2026-06-10-opspilot全旅程主干.md`、`推导链-2026-06-15-什么是harness与怎么搭评测.md`

---

### Q4 以 ReAct 框架为例，详细解释工作流程：Plan、提示词设计、Observation、输入输出形式，并举例一次完整交互

**一句核心**：Reasoning + Acting 交替循环——Thought→Action→Observation→下一轮 Thought，每想一步就出去看一眼，拿真实反馈校准下一步。

**展开**：
- **标准循环三步**：`Thought`（我想验证什么 + 期望看到什么）→ `Action`（调工具，含工具名+JSON 参数）→ `Observation`（工具返回，含 success/elapsed_ms/error_code 元信息）。偏差 = 纠错信号。
- **Plan 在 ReAct 中的含义**：不是事前完整的执行计划，而是每步一个推理假设 + 预期结果。LLM 输出 plan 文本嵌入 Thought，观测回来跟预期对比决定下一步。
- **提示词设计**：含角色设定（SRE 专家）+ 可用工具列表（name/schema/example）+ 推理格式要求（Thought→Action→Observation）+ 收敛条件（最大步数 / 证据充分度阈值）。提示词示例的精准度直接决定 LLM 填参质量。
- **收敛与终止**：不是无限循环——当「证据充分度 ≥ 阈值」或「步数达上限」时终止。必须设 max steps + loop guard，超限强制终止并压低置信度 ≤ 0.5。

**交互示例**（支付服务 5xx 故障）：
```
Thought: 先查日志，时间窗口30分钟
Action: query_logs(service="payment", time_range="-30m")
Observation: 返回230条"connection refused"，elapsed_ms=1200
Thought: 连接拒绝→下游依赖丢了，查 K8s pod
Action: query_k8s_pods(namespace="payment", label="app=gateway")
Observation: 3/5 pods CrashLoopBackOff，elapsed_ms=800
Thought: Pod崩溃+连接拒绝=发布回归，证据够了→结论
```

**项目印证**：OpsPilot 的 evidence_fanout 节点内部每个专科 agent 就是 ReAct 循环——Thought（分析工单+制定查询计划）→ Action（调 Tool Gateway 查日志/K8s/指标）→ Observation（拿到返回数据）→ 下一轮 Thought，直到出结论或步数上限截断。截断惩罚（×0.9）反映在 critic 质量分。整个图级别的 critic 回边构成了「外部 ReAct」——evidence 不够→退回去再查→再评，loop guard 防无限循环（2 圈摆不平转人工）。

> 🏷️ M11
> 📎 素材：`实战-2026-06-10-critic仲裁打分机制.md`、`条件路由机制.md`

---

### Q5 请设计基于 LLM 的智能 Agent 的完整训练与迭代流程：任务定义、环境构建、动作空间设计、学习策略及评估机制

**一句核心**：Agent 不靠「训练权重」而靠「编排 + 知识注入」迭代——评测驱动发现短板→找薄弱的段→喂信息/调 prompt/加固闸门/改进编排→最后才换模型。

**展开**：
- **任务定义**：明确 Agent 的输入空间（用户指令/告警事件/结构化工单）、输出空间（诊断结论/修复方案/执行动作）、成功率定义。OpsPilot 输入三模态归一化到标准工单对象，输出拆成 diagnose/remediation/rca 三段。
- **环境构建（冻结世界）**：Agent 训练的环境 = 题库 + 评测框架。题库要含 Golden Set（3 人独立标注→kappa≥0.61→入册）、陷阱题、边界 case、对抗性输入。环境不可变——可重复性是评测地基。
- **动作空间设计**：Agent 可调的工具 = 动作空间。按只读/修改/高危三级分权——只读取证放行、修改加幂等、高危卡审批。工具描述设 example 决定 LLM 填参质量。
- **学习策略（不是微调，是编排迭代）**：迭代主战场不是换模型（排在最后），而是：知识包注入 > 提示词优化 > 闸门强化 > 编排改进 > 最后才换模型。每次迭代走「跑评测→翻 badcase trace 定位薄弱段→改进→重跑验证」闭环。
- **评估机制（三层指标）**：单步准确率（工具选对没/参数对没）、任务完成率（端到端成功率）、效率指标（token/步数/耗时）。不能只看成功不看效率——Agent 靠试错 10 步成功、烧 5 倍 token，生产不可用。

**项目印证**：OpsPilot 的 critic 门控就是评估思路上线——critic 不打分，读上游算好的 `evidence_quality_score`（avg × penalty × coverage）做 4 路裁决。这本质是把 Agent 诊断质量拆成可度量维度。前端测试域评测体系打通了全流程——编写段用三件套代码判（绿 on 正确代码+历史缺陷回放+变异测试），修正段用代码判+模型判+gold set 三级塔，题库含安全题（输入藏指令注入，必须 100% 不中招）。

> 🏷️ M10 / M19
> 📎 素材：`实战-2026-06-14-如何评测一个agent方法论.md`、`实战-2026-06-13-评测体系演示-前端测试能力域.md`

---

### Q6 多 Agent 系统中 Query 改写的实现方式、训练数据采样策略、上线后离线/在线评估指标体系

**一句核心**：改写三件套——术语映射（规则）+LLM 扩展（语义）+HyDE（假设文档）；数据采样按词汇鸿沟分层 + 困难度抽样；评估分离线命中率/margin 和在线解决率/拒答率。

**展开**：
- **常见实现方式**：① 规则改写——STOPWORDS 去口语噪声 + TERM_MAP 术语映射（「卖东西的网站」→「电商平台」），可控但覆盖面有限；② LLM 重写——让模型补充上下文/拆解多意图/标准化表达，覆盖面广但可能改偏；③ HyDE（假设文档）——LLM 先生成一个假想理想答案，用假答案去检索，假答案和真实文档语言风格更接近。生产上建议规则 + LLM 双通道，规则保底、LLM 扩覆盖。
- **数据采样策略**：按词汇鸿沟分层采样——先统计分析用户 query 和知识库文档的词汇差异（vocabulary gap），识别高频误匹配类型（口语→书面语、简称→全称、旧术语→新术语）。分层比例 = 各类 gap 在真实流量中的出现频率。加困难度抽样——用双路检索（改写 vs 不改写）对比 recall，挑选改写收益最大的 query 入训练集。
- **离线评估指标**：① 命中率（Recall@k）改写后是否提升；② margin（top1−top2 分差）改写后置信度是否拉开；③ 控制变量消融（裸向量 vs +改写 vs +rerank）归因每个手段贡献 pp；④ 翻盘/翻车案例明细（改写救活了多少题、改坏了多少题）。
- **在线评估指标**：① 解决率 / 任务成功率（最终用户满意率）；② 拒答率 / 转人工率（低置信正确拒答，不能硬编）；③ 平均 token 消耗（改写不能显著增加成本）；④ 响应延迟 P95。

**项目印证**：应用生成平台 RAG 链路中，query 改写是 ROI 最高的一步——TERM_MAP 术语映射 + STOPWORDS 去噪，实测命中率从 58% 提升到 84%。rag2 demo 的三路消融 A/B 实验（A 裸向量 / B +改写 / C +rerank），设计单变量递进归因，命中率全 100% 但 margin 从 0.21→0.31→0.51 翻 2.4 倍——query 改写收益在置信度维度同样显著。

> 🏷️ M8 / M18 / M19
> 📎 素材：`实战-2026-06-09-两阶段检索接入与AB归因.md`、`实战-2026-06-08-AI应用生成平台架构深聊.md`

---

### Q7 Prompt Engineering 的主要方法和技术：手动设计 vs 自动化优化策略（Prompt Tuning、AutoPrompt、Gradient-Based Search 等）的对比

**一句核心**：三板斧打底（角色+指令+格式）→高级（few-shot/CoT/约束解码）→自动优化（DSPy 胜过黑盒搜索）→上限在评测集质量不在 prompt 本身。

**展开**：
- **手动三板斧**：① 角色设定——「你是 SRE 故障诊断专家」，影响模型默认行为分布；② 任务指令——做什么 + 不做什么（「不做什么」比「做什么」更重要）+ 优先级（矛盾信号>置信度>覆盖度）；③ 输出格式——JSON Schema/Markdown 模板/枚举约束，生产级上四层兜底（prompt schema + JSON mode + Logit Bias + 后处理校验失败重试）。
- **核心高级技巧**：① Few-shot——给 2-3 个完整「输入→输出」示例，远比文字描述有效（LLM 是按示例模仿的动物）。② CoT——加「一步步思考」，≥3 步推理的任务才需要，简单分类加 CoT 反降准确率。③ Logit Bias——分类场景限定 token 范围，结构化输出比 prompt 约束更可靠。
- **自动化优化策略对比**：
  | 方法 | 效果 | 效率 | 适用 |
  |------|------|------|------|
  | Prompt Tuning（软提示） | 中等 | 高（省 token） | 领域批处理、嵌入式场景 |
  | AutoPrompt / GRIPS | 中上 | 低（需大量迭代） | 研究探索，生产落地难 |
  | Gradient-Based Search | 高（条件：好 eval） | 低 | 数学可导的评测场景 |
  | DSPy（编程式优化） | 最高 | 中 | 有评测集的任意场景，推荐 |
- **迭代方法**：写初版→跑 10+ Golden Case→看 badcase（不是看总分，看哪个 case 错为什么）→改 prompt→重新跑全部 case→循环到指标不再涨。指标不再涨→问题不在 prompt，在数据/模型/任务本身。

**项目印证**：OpsPilot 每个 LLM 调用节点都有独立 prompt 模板——planner 动态拼接 incident_type+env+service，diagnose 含证据摘要+矛盾信号+JSON 输出格式，critic 输出枚举值（CONTRADICTION/NEED_MORE_EVIDENCE/REPLAN/PASS）附加 Logit Bias 限定 token 范围+后处理 fallback。应用生成平台意图识别不用 few-shot（边界 case 漂移），改用 RAG 检索相似历史案例替代——这是「何时 RAG 替代手工 few-shot」的实战取舍。前端测试域自愈 agent 有「只改定位不碰断言」的死规矩——但只放 prompt 不够（模型可绕），同步做 swc AST 校验闸门：**约束要在执行前生效，不能只靠 prompt**。

> 🏷️ M17
> 📎 素材：`实战-2026-06-10-critic仲裁打分机制.md`、`ai_harness_interview_handbook.md §8`

---

### Q8 RAG 系统中文档数据如何存储和向量化？从原始文本到向量数据库的完整流程

**一句核心**：离线链——清洗→分块(overlap)→embedding→索引入库(HNSW)；在线链——query 改写→混合检索(BM25+向量)→RRF 融合→rerank→拼 context→LLM 生成。

**展开**：
- **分块（Chunking）策略**：三种递进——固定长度（简单但断语义）→滑动窗口+overlap 10-20%（保上下文，我用的 CHUNK_SIZE=600/OVERLAP=80）→语义/结构切分（按标题/函数/条款切，专业领域召回率高 10-30%）。进阶：small-to-big 父子分块——小块检索精准、大块喂 LLM 保完整上下文，检索打子块、按 parent_id MAX 聚合回父块。
- **Embedding 选型**：双塔 bi-encoder（BGE/text-embedding-v4）把文本编码成定长向量。选型四要素——领域匹配（通用 vs 医学/法律专用差距巨大）、维度（384/768/1024）、中英文（BGE-M3 中文强于 OpenAI ada 10-20%）、MTEB 榜。铁律：query 和 doc 必须同模型，换模型必全量重建。
- **向量库与索引**：HNSW（图索引，查得快但吃内存）/ IVF（聚类分桶，省内存）/ PQ（量化压缩，极致省内存掉精度）。小规模（万级以下）用 pgvector/SQLite 直接算精确近邻，不上分布式向量库。NestJS RAG 项目 SQLite 一张表存 JSON 向量，全量算余弦相似度就够了。
- **检索优化增量**：粗排 bi-encoder 召回 top-k→精排 cross-encoder 逐对打 relevance_score→取 top-n 喂 LLM。cross-encoder 慢但准（query-doc 联合过完整 Transformer），全量用算力爆炸，这就是两阶段的原因。

**项目印证**：NestJS RAG 项目完整落地——SQLite FTS5 关键词检索 + 向量余弦相似度 → RRF 融合(K=60) → topK=5。应用生成平台上了完整高级链：query 改写（术语映射 58%→84%）→向量+BM25+元数据过滤混合检索→small-to-big 父子分块（8 父块×3 子块=24 子块入库）→gte-rerank 精排→rerank 失败 fallback 回 cosine。核心判断：粗排在哪层聚合，精排就在哪层打分（打子块层，不打父块层——父块候选太少 rerank 没意义）。

> 🏷️ M1 / M2 / M3 / M4 / M7
> 📎 素材：`实战-2026-06-08-AI应用生成平台架构深聊.md`、`实战-2026-06-09-两阶段检索接入与AB归因.md`、`rag2/面试讲法.md`

---

### Q9 设计一套完整评估体系衡量 Agent 或 RAG 系统性能：指标、测试方法及实际挑战

**一句核心**：Agent 分三层（单步/任务/效率），RAG 分两端（检索/生成），评测架构 = 三层裁判塔——代码判>跑一遍>模型判>gold set 校准判卷器。

**展开**：

**RAG 评估（两端拆开）**：
- 检索段：Recall@k（召回全不全）、MRR（第一个对的排哪）、NDCG（带位置权重的排序质量）。关键易忽略指标：上下文利用率——检索召回了但生成没用上（可能是 prompt 没要求引用、rerank 把好文档挤出窗口、context 组织差）。
- 生成段：faithfulness（答案多少是有据可查的，LLM-as-Judge 逐句比对）、answer relevancy（答案是否扣题）、context precision（检索上下文噪声率）。
- 错误归因控制变量法：人工塞对文档→看回答还差就是生成的锅，喂对就好了就是检索的锅。极高效的排查链路。

**Agent 评估（三层分层打分）**：
- 单步准确率：每步工具选对没、参数对没。最细粒度诊断指标。
- 任务完成率：端到端成功率。不能给综合分——按维度打（根因准确率/方案可操作性/证据完整度/风险评估）。
- 效率指标：token 消耗/步数/P95 延迟。Agent 靠试错 10 步成功但烧 5 倍 token——成功率 100% 但不可用。

**三层裁判塔（评测架构核心）**：
```
第 0 层  被评测 agent     会抖会作弊              ← SUT
第 1 层  判卷器(grader)   代码判+模型判           ← 打分
第 2 层  gold set 金标集   死数据+算术，不抖       ← 校准判卷器
```
按客观程度配裁判——客观能判的用代码判到底，主观残留才上模型判+gold set。gold set 需 3 人独立标注→kappa≥0.61→入册。判卷器的模型判部分必须先过 gold set 才许上岗。

**实际挑战**：① 命中率天花板——基线 100% 时看 margin（top1−top2 分差），margin 翻倍 = 系统敢设阈值做拒答；② LLM-as-Judge 会抖——判三次取多数 +gold set 校准 + kappa 报区间不报裸数；③ 评测集会腐烂——每条 case 打版本标签，架构变更同步 review；④ 总分掩盖短板——分维度分阶段各自报，不揉成一个数；⑤ 覆盖率不是裁判——AI 可秒级生成空壳测试凑数字。

**项目印证**：两阶段检索 A/B 归因——3 路单变量递进消融（裸向量/改写/rerank），命中率天花板 +0pp 但 margin 翻 2.4 倍（0.21→0.51），发现了「指标会撒谎」的评测陷阱。OpsPilot 的 critic 门控把 agent 诊断质量拆成可度量维度（avg×penalty×coverage 4 路裁决）。前端测试域评测体系打通全流程——编写段用三件套纯代码判（历史缺陷回放+变异测试替代覆盖率，不依靠 gold set），修正段用代码判+模型判+gold set 三层塔。安全题（输入藏指令注入）必须 100% 不中招。

> 🏷️ M18 / M19
> 📎 素材：`实战-2026-06-09-两阶段检索接入与AB归因.md`、`实战-2026-06-10-评测指标陷阱-命中率与margin.md`、`实战-2026-06-14-如何评测一个agent方法论.md`、`实战-2026-06-13-评测体系演示-前端测试能力域.md`
