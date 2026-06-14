## Agent 评估与监控（121 题）

### Q1 RAG多轮对话中知识遗忘和上下文漂移

**核心**：短期上下文窗口有限→关键信息持久化到外部存储；阶段性总结防早期约束被顶出。

- 结构性摘要存「故障类型+证据指纹+处置结果」而非整段对话，降低存储噪声
- 检索注入：每轮对话前RAG检索历史经验注入当前窗口，保持上下文锚定
- 对话状态追踪：维护显式状态机记录已确认事实、待验证假设、排除的可能

> 🏷️ M9 | 📎 OpsPilot retrieve_memory + Working Memory(state字段)；应用生成平台 RAG检索历史案例

### Q2 高并发Agent系统检索和生成延迟优化

**核心**：架构分层 + 预计算 + 并行化——召回段独立于生成段可横向扩展，embedding 预计算缓存命中。

- 召回段：向量库 ANN 索引（HNSW/IVF）+ 结果缓存（相同query不重复检索）；混合检索两路并行
- 生成段：streaming 生成降低首 token 延迟；context 压缩去噪减少 token 消耗
- 工程：asyncio 并行取证 + 每路独立超时（OpsPilot evidence_fanout 4路并行）；限流+队列削峰

> 🏷️ M19/M21 | 📎 OpsPilot evidence_fanout 并行取证；vector cache

### Q3 多Agent误判引发策略冲突的检测与解决

**核心**：多Agent冲突本质是结论冲突（软冲突），非资源冲突。解法：主从模式+仲裁者裁决，不是 agent 间辩论。

- 检测：跨源矛盾检测（规则表/LLM）→ 发现矛盾信号 → 冲突标记
- 缓解：回退到规划阶段重新分配任务（replan），或降低冲突方置信度
- 容错：主Agent 只读子Agent输出做汇总，子Agent间不互相通信——避免冲突传播
- 关键判断：真正多Agent通信成本平方增长，OpsPilot的13节点是**单Agent内部确定性编排**，非多Agent系统

> 🏷️ M13 | 📎 OpsPilot critic 矛盾检测（12条规则表，非LLM）；fanout并行取证的只读隔离设计

### Q4 分层任务中子任务对最终目标的贡献评估

**核心**：奖励塑形(reward shaping) + 因果推断(state-action归因) + 阶段价值估计。

- 奖励塑形：给中间子任务设定可验证的中间奖励（如证据完整度打分），不等到最终结果才给信号
- 因果推断：控制变量消融——移除该子任务看最终效果是否变差
- 价值估计：用critic评估每个子步骤产出的 quality score 作为该步的价值信号

> 🏷️ M19 | 📎 OpsPilot critic 的 evidence_quality_score（avg × penalty × coverage）即为阶段价值估计

### Q5 智能Agent完整训练链路

**核心**：数据收集→任务建模→策略网络→奖励→训练框架→评估→迭代。SRE Agent 走离线评测迭代而非在线RL。

- 数据：手工工单 + 真实告警日志 → 标准化 intake 输入
- 任务建模：状态空间=IncidentAgentState的47字段；动作空间=工具集（查日志/指标/K8s）
- 训练范式：PPO适合在线环境交互；DPO适合偏好对齐（人工标注A方案优于B方案）
- OpsPilot走「构造题库→跑评测→短板归因→修改prompt/编排→重跑验证」的离线评测迭代，非在线RL训练

> 🏷️ M10/M19 | 📎 OpsPilot 离线评测飞轮

### Q6 基于LLM的Agent训练与迭代流程

**核心**：→ 同 Q5，侧重任务定义(故障诊断)、环境(工具网关)、动作空间(tool registry)、学习策略(模仿→RL)。

- 模仿学习：用人工处置日志做种子数据训练初始行为克隆
- 强化学习：critic 评分作为 reward signal，PPO 优化
- 离线迭代（OpsPilot实际路线）：题库回归→短板飞轮→改prompt/编排>换模型

> 🏷️ M10/M19 | 📎 → Q5

### Q7 Agent系统部署流程

**核心**：模型服务化→工具集成→上下文管理→调度→监控→容错。关键：灰度上线+A/B对照+降级兜底。

- 模型服务：API 网关统一管理模型切换（MiniMax/OpenAI/DeepSeek），配置热切换
- 工具集成：Tool Registry + Gateway（schema校验/重试/审计/脱敏）
- 上下文：LangGraph StateGraph + checkpoint 持久化（自建 Postgres checkpoint，0.0.55无原生interrupt）
- 容错：loop guard（最多2圈）+ 超时兜底 + 工具降级（real→mock fallback）

> 🏷️ M21 | 📎 OpsPilot 部署：FastAPI + LangGraph compile + astream SSE推送

### Q8 RAG技术理解深度

**核心**：离线(清洗→分块→embedding→向量库) + 在线(query改写→混合检索→rerank→拼context→LLM生成+引用)。用检索换记忆。

- 优势：知识可更新不重训、有据可查可溯源、比微调便宜
- 局限：检索到≠回答对（需要分两段评估）；加了RAG仍有幻觉（只治知识缺失型，不治推理型）
- 判断何时用RAG vs 微调：RAG=知识频繁更新需溯源；微调=改变风格/格式对齐；两者互补

> 🏷️ M1 | 📎 应用生成平台完整RAG链路；OpsPilot retrieve_memory

### Q9 多路召回策略的文档质量全面评估

**核心**：定量(Recall@k/MRR/NDCG/margin) + 定性(标注文档相关性分档)。关键是选对指标组合而非只看命中率。

- Recall@k：相关文档在top-k里出现几条→「找全没有」
- MRR：首个正确文档排第几→「第一下就对不对」
- margin(top1−top2)：置信度信噪比→系统「敢不敢下结论」
- 定性：人工标注每路召回的top-n文档相关性(2=高/1=中/0=无)，发现模式(向量漏精确/BM25漏语义)

> 🏷️ M18 | 📎 → Q13

### Q10 搜索排序A/B测试优化特征权重

**核心**：单变量递进消融——每次只改一个变量，控制组vs实验组，看核心指标的统计显著性。

- 实验设计：A(基线) → B(+变量1) → C(+变量2)，归因分解：B−A=变量1贡献pp，C−B=变量2贡献pp
- 指标：命中率 + margin(置信度) + 翻盘/翻车案例明细 + 配对比较（几道由错变对、由对变错）
- 统计：`95%误差半宽≈1.96×√(p(1−p)/n)`，n=1000→±2.5pp；至少覆盖1周周期波动
- 陷阱：命中率天花板后归因+0pp但margin翻2.4倍→不能只看命中率

> 🏷️ M20 | 📎 rag2三路消融：A裸向量/B+query改写/C+rerank

### Q11 多工具均可用时的工具选择机制

**核心**：两阶段——先路由分类(领域Router)再精排选择(评分+成本)。关键：工具描述精确度决定LLM选型质量。

- Router/Classifier 先分到领域（查日志/查指标/查K8s/查部署），再在领域内选具体工具
- 评分维度：功能匹配度(description关键词命中) + 权限(当前env可调) + 成本(token/延迟) + 置信度
- 参数schema要写精确：格式/取值范围/默认值/互斥关系 + 精心写的example比详细constraints文字有效
- 网关兜底：schema校验不通过→结构化错误返回让LLM重填

> 🏷️ M15 | 📎 OpsPilot Tool Gateway 7步链路；function definition 精确度

### Q12 AI Agent安全防护策略（隐私+越权）

**核心**：权限控制(分级授权) + 脱敏过滤(网关层) + 审计日志(全链路) + 高危操作HITL审批。

- 权限分层：只读工具→自动+审计；修改工具→自动+幂等+审计；高风险写→生成方案→卡人工审批→才执行
- 脱敏：Tool Gateway 参数校验时扫敏感字段（手机/密码/密钥），发现即脱敏或拦截
- 审计：每笔工具调用落日志（谁/哪次run/调了什么/入参哈希/结果摘要）
- 防注入：system prompt和user input严格分层；用户输入中的指令性内容用规则/小模型先扫

> 🏷️ M15/M21 | 📎 OpsPilot risk_gate 4路分级 + approval_interrupt + Tool Gateway脱敏审计

### Q13 RAG评估体系最重要的指标

**核心**：检索段 Recall@k/MRR/NDCG/margin；生成段 faithfulness/answer relevancy/context precision。最易忽略：上下文利用率（检索回来了但模型没用上）。

- faithfulness（忠实度）：LLM-as-Judge逐句比对answer和context，生成中有多少能从上下文找到依据
- answer relevancy：LLM根据answer反向生成问题，算与原问题的语义相似度
- context precision：检索回来的context中真正相关的比例
- 上下文利用率：已召回的高相关文档是否在回答中被引用——没引用说明prompt或rerank有问题

> 🏷️ M18 | 📎 rag2 AB归因；RAGAS四维评分的faithfulness/relevancy/precision/recall

### Q14 Agent系统主要优点和挑战

**核心**：优点——能主动使用工具/记忆/反思，从「模型一次回答」变为「多轮闭环」；挑战——可靠性、幻觉、长任务漂移。

- 优点：外部感知(工具调用超越训练数据)、自我纠错(Reflection)、多步推理(规划分解)
- 挑战：单步可靠≠链路可靠(0.9¹³≈0.55)；长任务上下文膨胀偏离约束；工具选择错误；安全(越权/投毒)
- 解法：分解胜于强提示(每步可验证)；闸门分层(HITL+gate)；证据驱动(不下无据结论)

> 🏷️ M10/M19 | 📎 OpsPilot deep agent 四件套(规划/记忆/工具/反思)；0.98¹³≈0.77 信念

### Q15 RAG通过外部知识缓解幻觉

**核心**：把外部可信事实注入LLM上下文窗口，约束生成，用检索换记忆。只治「知识缺失型」幻觉，不治「推理型」幻觉。

- 机制：query→检索→相关文档拼入prompt→LLM基于文档生成+要求引用
- 优势：事实有据可查、知识可更新不重训、溯源可校验
- 边界：RAG不解决推理型幻觉（知道事实但逻辑推错了）→需CoT/RL/校验
- 反幻觉配套：prompt约束「不知道就说不知道」+引用标注+二次LLM校验+低置信标注

> 🏷️ M9 | 📎 应用生成平台5条反幻觉prompt + Planner否决权；OpsPilot confirmed_by_human门控

### Q16 Agent系统稳定性监控体系

**核心**：最容易挂的模块——工具调用(超时/500)、LLM推理(抖动/幻觉)、上下文窗口溢出。分层监控：系统层→应用层→LLM层。

- 系统层：CPU/内存/QPS/延迟 + 各节点wall-clock耗时分位值
- 应用层：节点事件流(NODE_STARTED/NODE_FAILED)、loop_count、critic裁决分布、checkpoint可用性
- LLM层：token消耗、LLM调用成功率、生成内容幻觉率（LLM-as-Judge定期采样）
- 诊断：从run events反向查瓶颈节点 → 查该节点的输入/输出/trace → 归类故障模式

> 🏷️ M19/M21 | 📎 OpsPilot _wrap_with_events 节点事件落DB + SSE实时推 + critic loop guard

### Q17 为何RAG不能直接用向量相似度生成回答

**核心**：向量相似度=粗略语义对齐，不能替代LLM的语境理解+信息整合+逻辑推理。直接回答会丢失上下文、产生幻觉。

- 准确性：向量检索是「整块文档和query的粗略语义距离」，不是「文档中哪句话回答了问题」
- 上下文完整性：生成的回答需要多文档多片段交叉整合验证，单条检索无法覆盖
- 幻觉控制：LLM基于多条context交叉验证生成，降低单一不可靠来源被采信的概率；可加引用溯源

> 🏷️ M1 | 📎 RAG本质：检索提供候选事实原料 → LLM做信息合成+推理+格式输出

### Q18 完整RAG评估体系+迭代优化手段

**核心**：检索段指标(Recall/MRR/NDCG) + 生成段指标(faithfulness/relevancy/context precision) + 上下文利用率。迭代分三端优化。

- 检索端优化：query改写→混合检索→rerank→元数据过滤；调整chunk策略
- 生成端优化：反幻觉prompt约束、引用溯源、context去噪重排、small-to-big分块
- 协同优化：控制变量归因——人工塞对文档给生成器，好了=检索的锅，还差=生成的锅
- 最易忽略：margin(置信度)→裸向量0.21没法设gate，rerank后0.51才能做拒答/转人工

> 🏷️ M18 | 📎 rag2 AB归因 + 指标陷阱(命中率天花板但margin翻倍)

### Q19 RAG性能系统评估与迭代优化

**核心**：→ 同 Q18，侧重「如何系统性评估」：自动评估(RAGAS/Trulens)+人工复盘badcase+A/B对照。

- 自动评估：RAGAS提供faithfulness/answer relevancy/context precision/context recall四维自动量化
- 人工评估：定期拿badcase做人工标注，查LLM-as-Judge判卷器是否漂移（kappa校准）
- 评测集维护：每道case打版本标签，架构变更时同步review受影响的case

> 🏷️ M18 | 📎 → Q18

### Q20 RAG缓解幻觉的技术机制和有效性边界

**核心**：→ 同 Q15，侧重「有效性边界」——仅治知识缺失型幻觉，前提是知识库正确且检索精准。

- 有效性边界：①知识库必须有正确答案（检索不到就无效）；②检索必须精准（错误文档反而加重幻觉）
- 不生效场景：模型需要多步推理的问题（事实全在context里但逻辑链太长）、知识库覆盖不到的领域
- 反效果：检索到错误文档→LLM被误导，幻觉率可能比没检索更高

> 🏷️ M9 | 📎 → Q15

### Q21 RAG提升LLM生成质量的作用机制

**核心**：→ 同 Q15/Q20，侧重「如何提升生成质量」：减少因知识缺失导致的编造、提高事实准确性、增强上下文相关性。

- 事实准确性：外部权威文档替换LLM不确定的内部记忆，从「大概对」到「可溯源」
- 上下文相关性：检索的文档为当前query量身定制，避免模型泛泛而谈
- 量化：术语映射58%→84%的召回改善直接转化为回答质量提升

> 🏷️ M9 | 📎 → Q15

### Q22 RAG输出错误时判断检索or生成问题

**核心**：控制变量法——人工塞正确答案文档给生成器。好了=检索的锅；还差=生成的锅。

- 步骤1：对同一个query，手工构造包含标准答案的context喂给LLM（不走检索）
- 步骤2：对比两种回答质量。人工塞对后变好→调检索(chunk/embedding/rerank)；没变好→调生成(prompt/context组织/模型)
- 步骤3：检索准确但生成差→针对性调优：prompt强调引用、context重排、降低温度参数
- 常见模式：检索准确率90%+但生成质量差→检查「上下文利用率」——prompt是否要求引用

> 🏷️ M18 | 📎 控制变量归因法（母题骨架M19）；上下文利用率指标

### Q23 RAG错误根源的实验设计判断

**核心**：→ 同 Q22，侧重实验设计：双盲对照 + 分模块指标观察。

- 观察检索端指标(Recall@k/MRR)是否正常→若检索指标正常则问题必在生成
- 对照实验：A组=当前系统 B组=用标准答案替换检索结果的对照 C组=用检索结果+不同prompt
- 逐一消融定位：换分块→重跑→改embedding→重跑→改prompt→重跑

> 🏷️ M18 | 📎 → Q22

### Q24 什么是RAG，解决LLM哪些局限

**核心**：Retrieval-Augmented Generation，检索增强生成。检索外部知识源→注入LLM上下文→输出有据可查的答案。

- 解决三大局限：①知识截止日期（训练数据有终点）→RAG实时检索最新文档；②幻觉（编造事实）→有据可查；③领域知识不足（通用模型不懂专业术语）→注入领域文档
- 知识密集型任务必用RAG：答案不在模型参数里在外部分档中，需要溯源+更新+校验

> 🏷️ M1 | 📎 应用生成平台 RAG检索scene→plan范式；OpsPilot retrieve_memory 检索历史RCA

### Q25 医疗/法律等专业领域RAG技术链路

**核心**：专业文档按结构切分(病历SOAP/合同条款)→领域embedding+元数据→精确检索+引用溯源→人工审核环节。

- 数据处理：按领域结构切(法律按条款、医疗按SOAP)，保留章节路径元数据
- 检索策略：领域术语映射改写query + BM25精确匹配(法规编号/药品名) + 向量语义检索双路
- 生成优化：引用标注法规号/文献出处；置信度低标注+转人工；高危回答加HITL审核
- 评估：领域专家标注QA对，重点考事实准确性(不能有半句错)和遗漏(是否回答完整)

> 🏷️ M1/M18 | 📎 专业领域=语义/结构切块 + 元数据过滤 + 引用溯源

### Q26 RAG召回策略评估的主要指标

**核心**：Recall@k(召回率→全不全)、MRR(平均倒数排名→第一下准不准)、NDCG(归一化折损累计增益→排得对不对)。

- Recall@k：标准答案文档在top-k中出现比例，k取1/3/5/10。答「找回来了没有」
- MRR：`Σ(1/第一个正确答案的排名)/N`，看首次命中位置。值域(0,1]，越接近1越好
- NDCG：带位置权重的排序质量=DCG/IDCG，相关文档排越靠前NDCG越高
- 选用原则：关注排序质量→NDCG；关注最终结果完整性→Recall@k；关注首个结果准确度→MRR

> 🏷️ M18 | 📎 rag2评测：三指标并用 + margin补充

### Q27 RAG检索评估的关键指标和系统影响

**核心**：→ 同 Q26，侧重「指标如何影响系统」：Recall@k决定信息完备性、MRR影响用户感知的即时质量、NDCG影响多文档综合推理质量。

- Recall太低→LLM拿不到完整信息，必编造；Recall高但NDCG低→首屏全是噪声，真正有用的在末尾被注意力稀释
- 生产权衡：高Recall+弱Rerank=k大可保信息不丢但生成质量低；低Recall+强Rerank=k小但精准

> 🏷️ M18 | 📎 → Q26

### Q28 RAG整体流程+编码模型(DPR/Contriever)+检索能力评估

**核心**：整体流程→M1(Q8)。编码模型：bi-encoder双塔架构，DPR用两个独立编码器(Query/Passage)，Contriever用对比学习无监督预训练。

- DPR：Query Encoder + Passage Encoder分离，需领域微调（用BM25挖hard negative）；优势精确，劣势需标注数据
- Contriever：无监督对比学习，不依赖标注query-doc对；优势零样本通用，劣势领域精度不如DPR微调
- 评估编码模型：MTEB排行榜(分类/聚类/对检索/重排等8类任务) + 领域内Recall@k实测

> 🏷️ M1/M3/M18 | 📎 应用生成平台text-embedding-v4 1024维；BGE-M3评测

### Q29 RAG系统常见性能瓶颈及迭代优化

**核心**：瓶颈=检索精度(chunk/embedding)、检索延迟(索引/缓存)、生成质量(prompt/context利用)。优化=三端迭代。

- 检索精度瓶颈：chunk粒度不匹配→small-to-big策略；vocabulary gap→query改写(ROI最高)
- 检索延迟瓶颈：全量精确检索慢→ANN索引+两阶段（粗排召回+精排rerank）+结果缓存
- 生成质量瓶颈：context噪声多→去重+压缩+重排；生成幻觉→引用溯源+反幻觉prompt
- 协同瓶颈：retrieval得分再高，prompt不要求引用=白费→查上下文利用率

> 🏷️ M8 | 📎 应用生成平台三端优化(query改写/混合检索+rerank/context去噪)

### Q30 缓解LLM幻觉的主要方法比较

**核心**：四类：RAG(注入外部事实)→治知识缺失型；RLHF(对齐人类偏好)→治推理/行为偏差；解码策略(temperature/top-p)→减少随机性；后处理校验→兜底拦截。

- RAG：最直接有效(知识缺失)，前提知识库正确+检索精准
- RLHF/DPO：改变模型行为分布(少编造/承认不知道)，代价高频成本高
- 解码策略：降低temperature减少随机生成，但也会降低创造力；不适合需要多样性的场景
- 后处理：LLM二次校验回答+事实核查规则，兜底但增加延迟和成本

> 🏷️ M9 | 📎 应用生成平台5条反幻觉prompt + LLM-runner评审兜底

### Q31 RAG vs 强化学习(RLHF)缓解幻觉的对比

**核心**：RAG治「不知道」（知识缺失→补知识）；RLHF治「知道了但表达错/逻辑错」（行为偏好→对齐价值观）。

- RAG路径：给LLM装个搜索引擎→不知道就去查→有据可查。不改变模型本身，只在推理时注入事实
- RLHF路径：让LLM学会「不确定时承认不知道」「不自相矛盾」→改变模型内在偏好。训练成本高
- 本质区别：RAG是外部知识的「补丁」，RLHF是内部行为的「校准」。两者互补——RAG确保有材料，RLHF确保不乱用材料
- 选型：知识频繁更新→RAG优先；回答风格/安全性→RLHF/DPO优先

> 🏷️ M9 | 📎 OpsPilot 用RAG补历史经验 + prompt约束替代RLHF

### Q32 医疗/法律RAG智能助手整体技术链路

**核心**：→ 同 Q25，专业文档处理+精确检索+引用溯源+人工审核。

> 🏷️ M1/M18 | 📎 → Q25

### Q33 单Agent vs 多Agent架构设计模式

**核心**：单Agent=一个LLM包揽全部，上下文不割裂但长任务会漂移。多Agent=拆角色协作，各司其职但通信成本平方增长。

- 单Agent模式：所有逻辑在一个上下文窗口里，优势=决策链路可追溯/无通信损耗/简单可控
- 多Agent三种协作：主从(主拆活+汇总)/对等协作(轮流发言易跑偏)/辩论投票(多个方案仲裁)
- 判据：任务能自然切成2+独立子任务且子任务间不互相商量吗？能→多Agent；不能→单Agent
- 关键澄清：OpsPilot的13节点是**单Agent内部编排**（共享state/规则路由/无agent间自然语言通信），不是Multi-Agent

> 🏷️ M13 | 📎 OpsPilot 13节点=Deep Agent非Multi-Agent；evidence_fanout并行取证=最安全主从子模式

### Q34 RAG中评估选择BGE-M3向量 vs BM25关键词检索

**核心**：关键指标=Recall@k + MRR + 响应延迟。向量管语义(BGE-M3)、BM25管精确(术语/ID)，互补不互斥。

- Recall@k：两路各自的召回率，向量在语义改述场景吊打BM25，BM25在精确匹配场景反超
- MRR：看首条命中质量，混合检索融合后MRR应有提升
- 响应延迟：BM25<10ms，向量检索取决于向量库规模50-200ms，混合检索需考虑两路并行开销
- 权重：通用场景各0.5；专业术语密集→BM25权重↑；长文本改述→向量权重↑

> 🏷️ M5/M18 | 📎 混合检索(向量+BM25)+RRF融合免调权重

### Q35 大模型对检索结果二次生成如何减少幻觉

**核心**：LLM对检索context做信息交叉验证→发现矛盾时可质疑；通过引用溯源约束输出→不编造。

- 提示工程：要求「仅基于提供的文档回答」「逐条标注引用来源」「文档信息不足则说不知道」
- 约束生成：logit bias限定输出格式（JSON/引用标注），减少自由发挥空间
- 多文档交叉验证：多条context互相冲突→提示LLM指出矛盾并标注置信度降低
- 低分检索结果不注入context（Planner有权否决）→防止错误文档带偏生成

> 🏷️ M7/M9 | 📎 应用生成平台Planner否决权+5条prompt约束

### Q36 多工具均可用时的工具调度与决策流程

**核心**：→ 同 Q11，侧重决策流程：意图解析→候选工具筛选→评分排序→参数填充→网关校验→执行。

- 流程：用户指令→意图解析→领域Router分类→候选工具集(领域内匹配)→评分(功能+权限+成本+置信)→选top1→参数提取→网关校验→执行
- 评分机制：硬过滤(权限/可调用性) + 软排序(匹配度/置信度/成本)
- 失败处理：执行失败→结构化错误返回→LLM根据error_code决定重试/换工具/放弃

> 🏷️ M15 | 📎 → Q11

### Q37 召回阶段(retrieval)质量的成熟评价体系

**核心**：离线指标=Recall@k/MRR/NDCG/Precision@k；在线指标=用户点击率/满意度/NPS。

- 离线优势：可复现/可消融/可定量，缺点是封闭测试集不能反映真实分布
- 在线优势：反映真实用户行为，缺点是噪声大/周期长/多个因素混杂无法归因
- MRR的局限：只关心首个正确答案，忽略其他相关信息→多相关文档场景用NDCG更好
- NDCG适用于排序质量敏感场景(搜索结果页)，Recall适用于保证信息完备场景(RAG context输入)

> 🏷️ M18 | 📎 rag2 离线三路消融 + 配对比较翻盘/翻车案例

### Q38 粗排模型性能评估的关键指标和方法

**核心**：→ 同 Q37，侧重粗排：Recall@k(保证精排有料) + 延迟(百ms级) + 内存占用。

- 关键：粗排的目标不是高精度而是高召回——宁可多召回一些噪声，也不能漏掉正确答案
- 离线：Recall@k（如k=200时目标文档是否在候选集）、粗排top-k通过率（被精排选中的比例）
- 在线：精排后最终结果质量（间接反映粗排质量传递）、首屏点击率、端到端延迟
- 冷启动见→ Q49

> 🏷️ M18/M20 | 📎 两阶段检索：粗排bi-encoder召回→精排cross-encoder打分

### Q39 推荐系统粗排模型评估+冷启动策略

**核心**：→ 同 Q38，侧重冷启动：规则兜底(热门/随机)+内容特征(元数据)+ 在线探索(汤普森采样)。

- 离线指标(同Q38) + 在线指标：CTR、转化率、用户停留时长
- 冷启动：新用户→热门推荐+探索臂(随机推少量新item收集信号)；新物品→用元数据(content-based)先匹配已知相似物品的用户行为
- 技术路径：双塔模型(用户塔用基础属性拟合，物品塔用元数据编码)→协同过滤(相似用户行为推测)

> 🏷️ M18/M19 | 📎 → Q38

### Q40 LangChain框架核心设计原理

**核心**：用模块化抽象(Prompt Template→Chain→Agent→Tool→Memory)把LLM应用开发标准化。LCEL(LangChain Expression Language)是其底层编排引擎。

- Chain：把多个步骤串成流水线(如"查知识库→拼prompt→调LLM→解析输出")，支持顺序/分支链
- Agent：ReAct循环的标准化实现——接受工具集+用户输入→选工具+填参→执行→观察→下一步
- Tool：function calling的封装，定义tool name/description/parameters schema供LLM选型
- 关键局限：DAG编排不支持环（无法从步骤5退回步骤2）→复杂Agent需LangGraph

> 🏷️ M16 | 📎 LangChain DAG编排 vs LangGraph环形图；OpsPilot选LangGraph因需要回边

### Q41 Agent开发框架(LangChain/LlamaIndex)对比

**核心**：LangChain=通用LLM编排框架(Chain/Agent/Tool抽象)。LlamaIndex=专注数据索引与检索(连接器+索引+查询引擎)。LangGraph=有状态图编排(环形/条件/并行)。

- LangChain：快速起步、生态丰富(DAG链/Agent/Memory)，但抽象层厚调试难、不支持环
- LlamaIndex：RAG开箱即用(分块策略/索引类型/检索模式)，但不是通用Agent框架
- LangGraph：底层StateGraph，支持环/条件分支/并行扇出，适合复杂Agent但上手门槛高
- 选型口诀：快速起步→LangChain；底层可控→LangGraph；开箱RAG→LlamaIndex；三者不互斥常组合

> 🏷️ M16 | 📎 OpsPilot 选 LangGraph 因需要 critic 回边 + 条件路由 + HITL 中断

### Q42 智能体多工具选择决策机制

**核心**：→ 同 Q11/Q36，侧重实现细节：工具定义→注册→LLM选型→网关校验→执行→结果回灌。

- 评分模块：text embedding算query和tool description的语义相似度 + 规则匹配(关键词命中)
- 置信度评估：工具返回成功后对比预期(observation符合thought假设)→更新置信度
- 成本排序：优先只读/低成本工具，写操作需额外确认
- 优化：领域Router先分类缩工具范围，避免50个工具全给LLM选错

> 🏷️ M15 | 📎 → Q11

### Q43 LangChain框架核心设计原理与链式调用

**核心**：→ 同 Q40，侧重「链式调用」：`prompt | llm | output_parser` 管道式组合。

- LCEL管道：`|` 操作符连接runnable，自动处理输入输出衔接、并行、流式、回退
- key组件：PromptTemplate(模板化)→LLM/ChatModel(模型调用)→OutputParser(解析)→Chain(串多个Runnable)
- Chain类型：SequentialChain(顺序)、RouterChain(条件分发)、MapReduceChain(并行)

> 🏷️ M16 | 📎 → Q40

### Q44 LangChain框架核心设计原理及关键组件

**核心**：→ 同 Q40，侧重工作流：定义chain→配置memory和tools→执行invoke/stream→回调监控。

- 工作流：Prompt→LLM→Parser→(optionally)Tool call→Observation→Prompt→… 的ReAct循环
- Memory组件：ConversationBufferMemory(全量保存)、SummaryMemory(压缩摘要)、VectorStoreMemory(RAG)
- Callbacks：on_llm_start/on_tool_start/on_chain_end，用于日志/监控/审计

> 🏷️ M16 | 📎 → Q40

### Q45 RAG适用于缓解哪类幻觉？有效性前提？

**核心**：RAG只治「知识缺失型」幻觉——模型不知道某个事实所以编。前提：知识库有正确答案+检索精准。

- 不适用：推理型幻觉(知道事实但逻辑链错误)、价值观型幻觉(偏见/有害内容)
- 前提1：知识库有相关文档且内容正确→无文档或错文档反而更糟
- 前提2：检索能精准命中正确答案→召回miss则RAG失效
- 前提3：LLM能正确解读和使用context→需要反幻觉prompt配合

> 🏷️ M9 | 📎 知识缺失→RAG补；推理错误→CoT/校验；价值观→RLHF/安全filter

### Q46 RAG常用评估指标——自动vs人工

**核心**：自动指标(RAGAS faithfulness/relevancy/precision/recall)+人工指标(事实准确率/回答完整性/引用正确率)。

- 自动评估：快速/低成本/可规模化，但LLM-as-Judge会抖会错→需gold set校准
- RAGAS四维：faithfulness(忠实度)、answer relevancy(答案相关性)、context precision(上下文精度)、context recall(上下文召回)
- 人工评估：事实准确率→答案中每句事实是否与源文档一致；回答完整性→是否覆盖所有关键点；引用正确率→标注的引用是否真能找到对应原文
- 适用：自动=日常回归/批量评测；人工=badcase复盘/gold set标注/判卷器校准

> 🏷️ M18 | 📎 RAGAS与Trulens对比；LLM-as-Judge需定期kappa校准

### Q47 A/B测试评估并优化搜索排序权重

**核心**：→ 同 Q10，侧重动态优化：在线分桶→指标监控→归因分析→权重调整→迭代。

- 实验设计：正交分桶保证流量不重叠，样本量n=total/2(两组均分)，至少1周覆盖周期波动
- 指标监控：核心指标(CTR/转化率/符合率)+护栏指标(延迟/报错率，不能恶化)
- 权重调整：A/B结果确认有效后→灰度扩量→全量→持续监控防衰减
- 陷阱：只监测正向指标不看护栏→优化了CTR但延迟翻倍不可接受

> 🏷️ M20 | 📎 → Q10

### Q48 Agent系统主要优缺点及未来发展

**核心**：→ 同 Q14，侧重技术趋势：从Shallow Agent(仅工具) → Deep Agent(规划/记忆/反思) → 多模态Agent→具身智能。

- 当前优势：特定垂直领域(代码/SRE/客服)单Agent已可用，任务可分解可验证
- 当前瓶颈：通用自主性不足、长任务可靠性低、多Agent通信成本高
- 趋势：HITL会逐步收敛(低级放行/高级审批)→评测体系标准化→从「写prompt」到「搭评测」范式迁移

> 🏷️ M10/M19 | 📎 → Q14

### Q49 粗排模型冷启动：新用户/新物品无行为数据

**核心**：内容特征(content-based)+人口统计(demographic)+在线探索(bandit/随机)+相似用户/物品传递。

- 新用户：用注册信息(年龄/地区/设备)找相似老用户的行为推测→热门推荐兜底→探索臂快速收集信号
- 新物品：用元数据(类别/标签/文本描述)embedding→与已知物品embedding算相似→用相似物品的受众人群做初步推荐
- 技术路径：双塔模型(用户塔基础属性+物品塔元数据)→协同过滤(相似用户行为)→Thompson Sampling在线学习
- 评估：新用户/物品的CTR/转化率初始低，需设定合理的冷启动窗口期指标预期

> 🏷️ M18/M19 | 📎 content-based + 探索-利用(exploration-exploitation)

### Q50 构建RAG系统时如何评估和选择向量数据库

**核心**：性能(QPS/查询延迟)+可扩展性(数据量增长后性能衰减)+索引类型(HNSW/IVF)+与现有技术栈集成成本。

- 性能：小规模(<10万)用pgvector/SQLite够用；中规模用Milvus；超大规模用Pinecone/Zilliz Cloud托管
- 索引类型：需要高精度低延迟→HNSW(吃内存)；内存有限→IVF+PQ(省内存掉精度)
- 延迟：HNSW <5ms(内存内)；Milvus 10-50ms(网络+序列化)；SQLite 1-5ms(进程内)
- 集成成本：已有PostgreSQL→pgvector最轻；已有K8s→Milvus Operator；零运维→托管服务

> 🏷️ M4 | 📎 NestJS RAG项目SQLite存JSON向量(数据小)；OpsPilot可考虑pgvector

### Q51 RAG vs RL缓解幻觉的适用场景

**核心**：RAG治「知识缺失」导致的幻觉（模型不知道X→检索X→有据可查）；RL治「行为/推理模式」导致的幻觉（模型知道但乱说、不自知、偏见）。

- RAG适用：实时信息、长尾知识、专业领域（医疗/法律）→外部文档补知识
- RL适用：减少编造行为本身（DPO训练"不确定就说不知道"）、减少有害/偏见输出、自我一致性
- 本质：RAG是外部注入事实（补信息缺口），RL是内部改变行为偏好（补判断缺口）
- 误区：RAG救不了推理型幻觉——查到了事实但逻辑推错了，RAG无能为力

> 🏷️ M9 | 📎 OpsPilot用RAG补历史经验(只读)；反幻觉prompt替代RLHF行为约束

### Q52 现代RAG系统vs传统先检索后生成流水线

**核心**：现代RAG不是简单拼接，而是深度协同——迭代检索(agentic RAG)、自我校正、检索-生成联合优化。

- 传统：query→检索→拼接context→LLM生成，单次、线性、无反馈
- 现代改进：①agentic RAG：LLM主动判断检索充足性→不够就改query重新检索（迭代）；②self-RAG：LLM在生成时自我评估是否需要对每句加检索校验；③查询分解+子查询检索合并
- 融合机制：rerank精排->生成->引用校验->不合格回退重新检索→形成闭环(类似OpsPilot critic回边)
- 代表：LangGraph搭建的RAG agent=有状态多轮检索+生成，非一次性流水线

> 🏷️ M1 | 📎 agentic RAG = ReAct in RAG context

### Q53 用户兴趣话题偏好建模系统

**核心**：数据收集(行为日志+交互历史)→特征工程(短期兴趣+长期偏好+社交关系)→模型(双塔/Transformer)→增量更新。

- 数据处理：点击/收藏/停留时长→正样本；曝光未点击→负样本；按时间衰减加权
- 特征工程：短期=最近N次行为的平均embedding；长期=全量行为的聚类topic分布
- 模型选型：双塔(用户塔+物品塔，高效检索)→Transformer序列模型(捕捉行为序列)→多任务学习(同时预测点击/时长)
- 更新策略：在线增量更新(新行为实时更新用户embedding) + 离线全量重训(每周/每天)

> 🏷️ ML 系统设计 | 📎 用户画像 = 短期兴趣+长期偏好+实时行为融合

### Q54 Transformer Agent多轮对话中标准Attention的局限性

**核心**：长期依赖衰减(注意力分散)、上下文长度限制(平方复杂度)、推理效率(每轮重新计算KV缓存)、信息遗忘。

- 长期依赖：随着对话增长，早期指令被后续token稀释(prompt中间部分容易被忽略→Lost in Middle)
- 上下文长度：O(n²)复杂度限制实际可用长度，超长对话推理成本爆炸
- KV缓存：多轮对话需保留历史KV cache或重新计算，内存和算力压力大
- 解法：阶段性总结压缩、关键信息外部持久化、滑动窗口attention + 检索增强(取出再喂)

> 🏷️ ML / M10 | 📎 OpsPilot的阶段性总结 + 外部checkpoint持久化关键状态

### Q55 偏好感知对话系统训练设计

**核心**：构建偏好标注数据（A方案优于B方案）→DPO/RLHF训练→自动化+人工评估。

- 数据构建：同一query生成多个回答→人工标注偏好排序（喜好程度/有用程度/语气合适度）
- 模型架构：Base LLM + 偏好头(或直接DPO微调不给头) + LoRA低秩适配降低训练成本
- 评估：自动指标(G-Eval/奖励模型打分)+人工评估(AB盲评偏好符合率)
- 核心难点：偏好是主观多维的（准确/简洁/友好），需要多维度分打分而非一个笼统分

> 🏷️ ML/M19 | 📎 DPO vs RLHF；分维度打分不小总分

### Q56 LangChain框架集成LLM+工具+数据源+记忆

**核心**：→ 同 Q40，侧重集成机制：Tools=function calling封装；Data=Document Loaders+VectorStores；Memory=历史对话管理。

- Tools：@tool装饰器定义tool→ToolRegistry注册→Agent通过function calling选type+填参→执行→结果回灌
- Data源：DocumentLoader(20+格式)→TextSplitter(分块)→Embeddings(向量化)→VectorStore(索引)
- Memory：ConversationBufferMemory(存历史)→ConversationSummaryBufferMemory(压缩版)→与RAG长期记忆互补

> 🏷️ M16 | 📎 → Q40

### Q57 Agent工具调用是否采用Workflow形式

**核心**：确定性高、步骤固定→Workflow(省token/可靠/可审计)；不确定性高、需边走边看→ReAct(灵活/纠错)。

- Workflow优点：步骤显式可审计、每步可独立测试、不会跑偏、token效率高（不需要Thought溢写）
- Workflow缺点：缺少灵活性、未预见的工具选择/异常分支无法覆盖
- ReAct优点：灵活、可纠错、处理意外情况
- 结论：生产Agent用Workflow做主干（OpsPilot 13节点），内部不确定环节用ReAct（fanout内部专科agent）。两者不互斥

> 🏷️ M15 | 📎 OpsPilot：图级固定编排(Workflow)+节点内部ReAct循环

### Q58 对AI Agent的理解及未来发展看法

**核心**：Agent=LLM + 规划 + 记忆 + 工具调用 + 反思，从「一问一答」到「多轮闭环自主决策」。未来=从写prompt到搭评测的范式迁移。

- 三层演进：Chatbot（纯对话）→ Shallow Agent（工具调用）→ Deep Agent（四件套+文件系统+HITL）
- 核心突破：反思（Reflection）让Agent从「能做事」到「能把事做对」
- 未来方向：评测体系标准化是瓶颈（非模型能力）；HITL会逐步收敛；多Agent协作还在早期

> 🏷️ M10 | 📎 OpsPilot=手搓deep agent；四件套=规划/记忆/工具/反思

### Q59 RAG检索语义相似但实际不相关的分析和解决

**核心**：语义相似≠回答相关——向量检索召回「同一主题但不含答案」的文档。靠rerank精排+元数据过滤+LLM否决。

- 根因：embedding模型只捕捉主题相关性，不判断「是否包含该问题的答案」。问「怎么修」、文档是「怎么用」→高相似低相关
- 诊断：人工review召回的top-k，看「相关但无用」的比例，确认是embedding粒度问题
- 解法1：cross-encoder rerank重新打分（query+doc联合编码），能捕获细粒度的问答匹配
- 解法2：元数据过滤（文档类型/章节），检索前限制文档类型必须为「故障处置」而非「配置说明」
- 解法3：Planner/LLM有权否决低质量context不注入prompt

> 🏷️ M8/M18 | 📎 应用生成平台Planner否决权 + cross-encoder rerank

### Q60 多智能体系统中Reflection和Memory的技术实现

**核心**：Reflection=执行完回头看「我对吗」→外部信号校准(非纯自省)。Memory=短期上下文+长期向量库。两者协同：Reflection结论写入Memory→下次同类任务直接避免重错。

- Reflection实现：①内省式(LLM自评，轻量但不总有效)；②外部信号式(Critic读矛盾信号+质量分→裁决)，OpsPilot用后者
- Memory分层：短期(对话窗口)→工作(当前任务state)→长期(向量库/RAG检索历史经验)→情节(完整事件序列含走过的弯路)
- 协同：Reflection产出「这个故障的证据矛盾、置信度过低」→写入Memory→下次同类故障直接跳过已被证伪的假设
- 坑：LLM自我合理化→Reflection必须有外部锚点(工具真实返回/跨源矛盾)，不是纯自省

> 🏷️ M14 | 📎 OpsPilot critic=Reflection工程落地(读矛盾信号非自评)；retrieve_memory=长期Memory

### Q61 RAG文档检索方法选择及优化措施

**核心**：向量检索(语义相似)+BM25关键词(精确匹配)→混合检索+RRF融合→rerank精排。优化=query改写+分块策略+元数据过滤。

- 向量检索：选BGE-M3/text-embedding-v4，管语义相似和同义改写
- BM25：Elasticsearch/SQLite FTS5，管精确命中和罕见表征
- 优化：query改写(术语映射ROI最高)→chunk粒度调整(语义切优于固定长度)→元数据硬过滤→cross-encoder精排
- 父子分块(small-to-big)：小块检索(精准)→聚合回取大块(完整上下文)→双赢

> 🏷️ M5/M8 | 📎 应用生成平台query改写58→84% + 混合检索 + small-to-big父块聚合

### Q62 MRR含义、计算及与NDCG/Precision的对比

**核心**：MRR=`Σ(1/首个正确答案的排名)/N`，衡量「第一个正确答案排多前」。NDCG带位置权重衡量整体排序质量，Precision衡量检索结果中正确比例。

- MRR：只看首个正确答案的排名位置，对「有且只有一个正确答案」的任务最合适（如FAQ问答）
- NDCG：考虑位置权重+相关性分级，适合排序质量敏感场景（搜索页/推荐列表），多级相关(0-3)比二元更合理
- Precision@k：top-k中正确比例，不考虑排序，适合只需保证「前端结果相关」的场景
- 选型：问「第一个答案对不对」→MRR；问「所有相关文档排得合不合理」→NDCG；问「召回结果是否干净」→Precision

> 🏷️ M18 | 📎 rag2评测三指标并用；MRR适合单一正确答案场景

### Q63 RAG评估指标从检索和生成两维度说明

**核心**：→ 同 Q18/Q46，两维分解：检索看是否找对文档(Recall/MRR/NDCG)；生成看是否用好文档(faithfulness/relevancy/context precision)。

> 🏷️ M18 | 📎 → Q18

### Q64 RAG技术的主要缺陷和局限性

**核心**：①检索到≠回答对(两段误差叠加) ②幻觉治不彻底(推理型幻觉) ③知识库质量直接决定上限 ④延迟增加。

- 缺陷1：embedding语义匹配粗粒度→召回想关但不含答案的文档（→ Q59）
- 缺陷2：多跳推理困难→需要多文档串联推理时RAG一次检索不够
- 缺陷3：知识库维护成本→过期/错误信息危害比没知识库更大(+门控写回防污染)
- 缺陷4：增量更新换embedding模型→必须全量重建旧向量

> 🏷️ M1/M9 | 📎 门控写回(confirmed_by_human)防知识库污染；换模型必全量重建

### Q65 RAG上下文信息不准确的诊断和解决

**核心**：→ 同 Q22，侧重数据质量：检查检索召回+context内容完整性+标注数据质量→修复源头。

- 诊断：人工review检索结果→检索结果本身就错→查知识库内容质量(过期/错误)
- 检索结果对但context拼接乱了→检查分块和context组装逻辑(去重/排序/截断)
- 数据质量控制：标注review+版本标签(知识库每条chunk标注来源+更新时间)，错误内容及时下线

> 🏷️ M18 | 📎 → Q22

### Q66 Multi-Agent中Reflection和Memory的作用

**核心**：→ 同 Q60，侧重多Agent协作：Reflection让每个agent校准自己的判断→Memory让agent间通过共享记忆间接协同。

- Reflection在多Agent：各agent独立反思自己的输出→仲裁者(主Agent)汇总各反思结论→识别矛盾
- Memory在多Agent：共享长期记忆(向量库)让agent之间交换经验而不需要直接通信→降低通信成本
- 协同效果：各Agent各自反思+共享记忆→减少重复犯错+缩短诊断路径
- 注意：直接agent间通信(辩论)成本高且不收敛→优选主从模式(只读+仲裁)

> 🏷️ M14 | 📎 → Q60

### Q67 LLM在搜索检索场景的应用

**核心**：传统倒排索引+语义检索(embedding)融合，LLM做query理解(改写/意图识别)+rerank精排+答案生成。

- 技术方案：query→LLM改写(术语映射/消歧)→混合检索→LLM rerank(精排打分)→LLM生成摘要/答案
- 优势：语义理解能力远超传统NLP(意图识别/同义改写/多语言)，零样本能力
- 挑战：延迟高(LLM rerank比cross-encoder慢)、成本(token消耗)、幻觉风险
- 最佳实践：LLM在关键节点(改写/精排/生成)点状介入，不替代整条链路

> 🏷️ M1/M18 | 📎 query改写用LLM + rerank用cross-encoder(比LLM快且便宜)+最终生成用LLM

### Q68 RAG系统效果评估方法和指标

**核心**：→ 同 Q18/Q46，概述：自动(RAGAS四维)+人工(事实准确率)+A/B在线

> 🏷️ M18 | 📎 → Q18

### Q69 根据任务复杂度决定单Agent还是多Agent

**核心**：→ 同 Q33，侧重判据：任务能自然切成2+独立子任务且互不商量吗？能=多Agent，否=单Agent。

- 简单任务(查天气/写邮件)→Shallow Agent(工具调用即可)
- 中等复杂度(SRE诊断/代码生成)→Deep单Agent(规划+记忆+工具+反思，13节点编排)
- 高复杂度(多专业协同/并行独立取证)→多Agent主从模式(主拆活+子Agent执行+汇总)
- 灵魂拷问：切开后几份活需要互相商量吗？需要=没切开=回去用单Agent

> 🏷️ M13 | 📎 → Q33

### Q70 RAG评估的完整方法和指标体系

**核心**：→ 同 Q18/Q46，完整概述检索+生成两维+自动+人工+在线

> 🏷️ M18 | 📎 → Q18

### Q71 Agent/大模型项目经验

**核心**：三步应答——项目背景(SRE故障诊断/OpsPilot)→技术方案(13节点LangGraph编排+critic仲裁)→个人职责(架构设计+关键取舍)。

- 背景：SRE故障处置需要可控/可解释/可中断，纯ReAct浅Agent不行
- 方案：LangGraph搭建Deep Agent，13节点5段路由，每节点职责单一可独立验证
- 个人工作：架构设计→critic门控(评分决策解耦+矛盾检测选规则表不选LLM)→HITL自建审批(绕过0.0.55无原生interrupt)→端到端可观测(事件+SSE)
- 关键取舍：矛盾检测数据说话(LLM判不一致率39%→选规则表)；13节点不嫌多→每步可验证

> 🏷️ M19/M21 | 📎 OpsPilot全链路；诚实边界：NL抽取/矛盾仲裁/方案择优三缺口

### Q72 LLM客服质量评估系统设计(伪代码)

**核心**：多维度评估(准确性/礼貌性/解决率/效率)→LLM-as-Judge分维度打分→人工抽样校准。

```python
def evaluate_ticket(conversation, resolution):
    # 1. 维度拆分
    dims = {
        "accuracy": check_factual_accuracy(conversation, resolution),
        "empathy": check_tone_politeness(conversation),
        "completeness": check_all_questions_answered(conversation, resolution),
        "efficiency": count_turns(conversation)
    }
    # 2. LLM-as-Judge 分维度打分(1-5)
    scores = {}
    for dim, context in dims.items():
        prompt = build_rubric_prompt(dim, context)
        scores[dim] = llm_judge(prompt)  # 返回 1-5 分
    # 3. 加权汇总 + 弱项归因
    total = weighted_sum(scores, weights=[0.4,0.2,0.3,0.1])
    weak_dims = [d for d,s in scores.items() if s < 3]
    return {"total": total, "dims": scores, "improve": weak_dims}
```

> 🏷️ M19 | 📎 分维度打分不揉总分；LLM-as-Judge + 人工kappa校准

### Q73 多Agent系统各组件的优化策略

**核心**：→ 同 Q33，通信效率(减少自然语言转述/共享结构化state)+决策协调(主从模式+仲裁)+资源分配(并行独立子任务)。

- 通信效率：Agent之间传递结构化数据(JSON/state)而非自然语言，避免信息在转述中丢失
- 决策协调：主Agent统一拆任务+汇总，避免多Agent投票辩论（成本高不收敛）
- 资源分配：不共享排他资源→可并行；共享→串行加锁
- 容错：子Agent失败不影响其他（隔离上下文），主Agent负责汇总+降级处理

> 🏷️ M13 | 📎 OpsPilot evidence_fanout并行取证：只读/互不依赖/不通信/独立超时

### Q74 RAG技术理解及解决的具体问题

**核心**：→ 同 Q24/Q8，侧重项目效果：应用生成平台RAG检索scene→plan范式（不用few-shot，防边界漂移）。

- 解决的问题：用户自然语言模糊指令和系统结构化修改的语义鸿沟
- 效果提升：query改写58%→84%召回率；RAG召回6000+chunk中历史验证范式，比few-shot固定示例更稳

> 🏷️ M1 | 📎 → Q24

### Q75 Agent/大模型项目经验分享

**核心**：→ 同 Q71，三步：背景-方案-个人职责+挑战-解决

> 🏷️ M19/M21 | 📎 → Q71

### Q76 当前大模型Agent有效性及与主流框架对比

**核心**：Agent在垂直领域(代码/SRE/客服)已可用，通用自主性仍不足。LangChain快速起步但闭环难；LangGraph底层可控支持复杂编排；AutoGPT自主性高但可靠性低。

- 有效性：拆成可独立验证步骤→每步0.98→13步0.77，可用。一步到位裸调LLM→不可靠
- LangChain：生态丰富/快速开发，但DAG无环限制长期任务
- AutoGPT/BabyAGI：ReAct循环自驱，自主性强但死循环风险高、token消耗大
- MetaGPT：Role-based多Agent协作，角色扮演好但通信成本高→适合探索性场景，生产不稳

> 🏷️ M16/M19 | 📎 OpsPilot用LangGraph(可控)>LangChain(简单DAG)>AutoGPT(不可控)

### Q77 RAG系统中意图识别模块的关键作用

**核心**：意图识别=输入信号的第一道过滤器——决定后续检索用什么策略、怎么改写query、需要什么类型的文档。

- 作用1：分类意图类型(事实查询/故障诊断/操作指南)→路由到不同检索策略和prompt模板
- 作用2：提取关键实体(service/env/time_range)→作元数据过滤条件→缩小检索范围提高精度
- 作用3：判断复杂度→简单问答直接走快车道（跳过Planner），复杂任务进入深层编排
- 重要性：意图识别错误→整个RAG链路从第一环就错→后面全是白费

> 🏷️ M8 | 📎 应用生成平台Router先分类(改样式/改逻辑/改数据)→决定走快慢车道

### Q78 RAG评估体系中最关键的指标

**核心**：→ 同 Q13，侧重「最关键」：faithfulness(忠实度)是底线——如果生成内容和检索文档不一致，整个RAG就失败了。

- faithfulness > answer relevancy > context precision：不忠实=系统不可信，这是RAG存在的意义
- 上下文利用率=最易被忽略的关键指标：检索回来了但没用上→优化空间被埋没

> 🏷️ M18 | 📎 → Q13

### Q79 多Agent系统优化方向

**核心**：→ 同 Q73，三方向：通信效率(结构化/共享state)→决策协调(主从+仲裁)→资源分配(并行化+隔离)。

> 🏷️ M13 | 📎 → Q73

### Q80 Agent/大模型项目实践经验

**核心**：→ 同 Q71，三步：背景-方案-挑战-个人贡献

> 🏷️ M19/M21 | 📎 → Q71

### Q81 LangGraph框架的适用场景

**核心**：需要环形图(回边/重试)+条件路由(多路分支)+HITL中断续跑的复杂有状态Agent。

- 适用场景：①故障诊断Agent(OpsPilot，critic退回重查)→需要回边；②审批工单Agent（中断→人审批→续跑）；③并行取证+聚合评分的多步推理
- 优势：StateGraph有向图支持环/条件分支/并行扇出——LangChain DAG做不到的三样
- 底层：Pregel/BSP引擎，channel更新在super-step间原子apply，并行节点读同一冻结快照无并发写冲突
- 不适用：简单线性任务(LangChain更快)；纯RAG系统(LlamaIndex更高效)

> 🏷️ M16 | 📎 OpsPilot选LangGraph三大理由：环形图(critic回边)+条件路由(risk_gate 4路)+HITL

### Q82 ReAct vs Planning(Plan-Execute)框架对比

**核心**：ReAct=边想边做(Thought→Action→Observation循环)，纠错快但token消耗大。Plan-Execute=先出完整计划再批量执行，省token但一旦偏差无法纠正。

- ReAct设计理念：每步推理依赖上步真实观察，灵活应对意外，适合环境交互型任务
- Plan-Execute设计：全局视角先规划完整依赖图→并行执行，适合确定性高、依赖图已知的任务
- ReAct优点：纠错能力强/可解释(每步有trace)；缺点：token消耗大/上下文膨胀快/可能死循环
- Plan-Execute优点：Token效率高/可并行；缺点：初始计划错=全程错，无法中途修正
- OpsPilot混合：图级用Plan-Execute(planner出计划→fanout并行执行)，节点内部用ReAct，critic回边提供图级纠错

> 🏷️ M11 | 📎 OpsPilot planner(Plan-Execute)+fanout(内部ReAct)+critic回边(图级纠错)

### Q83 RAG效果不佳如何系统性定位问题模块

**核心**：→ 同 Q22，系统性排查：检索指标→生成指标→协同环节，控制变量逐段排除。

- 排查顺序：①查检索段(Recall@k/MRR是否正常)→②查生成段(人工塞对文档后是否变好)→③查协同(上下文利用率/引用率)
- 诊断信号：检索Recall低→调chunk/embedding/query改写；检索好生成差→调prompt/context组织/温度
- 协同问题：检索对、prompt对、但context组装乱(去重误删关键块/排序倒置)→debug context拼接逻辑

> 🏷️ M18 | 📎 → Q22

### Q84 LLM幻觉缓解的多层面分析

**核心**：训练数据(去噪/去重)→模型架构(约束解码/不确定性估计)→知识增强(RAG)→推理控制(temperature)→后处理(校验)。

- 训练层：高质量数据去伪、RLHF/DPO校准"不知道就说不知道"的行为
- 架构层：约束解码限定输出空间(分类/JSON场景)；输出不确定性量化(低置信不输出)
- RAG层：注入外部事实约束生成 + 引用溯源 + prompt约束
- 后处理：LLM二次校验一致性、事实核查规则、人工review高风险输出
- 局限性：没有银弹——RAG治知识缺失但不治推理型；RLHF成本高且无法完全消除

> 🏷️ M9 | 📎 多层防御：RAG(知识) + prompt约束(行为) + 引用校验(兜底)

### Q85 Agent中规划与执行的理解

**核心**：规划=把模糊目标拆成可执行子任务序列(DAG)。执行=按规划调用工具完成各子任务，处理异常。两者协同=规划出蓝图→执行反馈偏差→replan。

- 规划能力：目标分解、依赖关系推理、优先级排序、不确定性感知(识别需要留replanning回路)
- 执行能力：工具调用(选tool+填参数)、异常处理(超时/500/权限)、结果验证、反馈回路
- 协同方式：Plan-Execute先全出计划再执行(确定性)；ReAct每步规划后再执行(灵活性)
- OpsPilot协同：planner出计划→evidence_fanout执行→critic裁决偏差→回退到planner重新规划

> 🏷️ M10 | 📎 OpsPilot planner→fanout→critic→replan 的规划-执行-反馈闭环

### Q86 RAG整体生成效果不佳的系统性定位

**核心**：→ 同 Q22/Q83，侧重诊断步骤：①查检索→②查生成→③查协同。

> 🏷️ M18 | 📎 → Q22

### Q87 RAG效果不佳的三模块系统性排查

**核心**：→ 同 Q22/Q83，强调检索/生成/协同三模块各自诊断方法。

- 检索诊断：Recall@k是否低于阈值？→调chunk粒度/embedding模型/query改写/混合检索
- 生成诊断：人工塞正确答案后LLM能否生成高质量回答？→调prompt/温度/context组织
- 协同诊断：检索回来的文档在回答里被引用了吗？（上下文利用率）→调prompt强制引用/context排序

> 🏷️ M18 | 📎 → Q22

### Q88 RAG效果不佳定位+检索准确但生成差的调优

**核心**：检索端→Q22控制变量法定位；生成端调优=反幻觉prompt约束+引用要求+context重排+降低温度+LIMIT回答长度。

- Prompt优化：强制「逐条引用来源」「不知道就说不知道」「不要推断context没写的内容」
- Context优化：去重→按相关性排序（最重要的放开头）→压缩长文档去掉无关段落
- 生成参数：temperature 0.1-0.3(减少随机性)、限制max_tokens(防止跑题)、logit bias防偏离格式
- 进阶：用另一个LLM做post-hoc事实核查，不通过的标记置信度低

> 🏷️ M18 | 📎 反幻觉prompt + context重排 + 引用溯源

### Q89 主流AI Agent框架对比(LangChain/AutoGPT/MetaGPT)

**核心**：LangChain=通用编排(快速)、LangGraph=底层状态机(可控)、AutoGPT=自主ReAct(灵活但不可靠)、MetaGPT=角色协作(探索强)。

- LangChain：DAG编排，生态丰富，适合快速开发。缺陷：不支持环形图，长任务失控
- AutoGPT/BabyAGI：自驱ReAct循环，高度自主。缺陷：死循环风险、token浪费、不可预测
- MetaGPT：SOP驱动的多Agent角色扮演(产品经理/架构师/工程师)。缺陷：通信成本高、SOP僵化难适配
- LangGraph：StateGraph + Pregel引擎，支持环/条件/并行。缺陷：上手门槛高，需要手搓编排
- 选用：快速原型→LangChain；生产级复杂Agent→LangGraph；探索性任务→AutoGPT

> 🏷️ M16 | 📎 OpsPilot=LangGraph(生产级)；应用生成平台=自研Router→RAG→Planner(拆解LangChain概念)

### Q90 人机协同中人工干预与自动处理的切换机制

**核心**：置信度阈值分级 → 风险等级评估 → 动态调度。低置信/高风险→卡人工审批；高置信/低风险→自动放行。

- 三级切换：自动放行(只读+低风险)→半自动(自动执行+审计，事后抽查)→人工审批(高危写操作+置信度低)
- 置信度阈值：critic评分 > 0.7 + risk=LOW → 自动；< 0.5 + risk=HIGH → HITL审批
- 动态调度：环境(prod>staging)、severity(P1>P3)、loop_count(>2圈强制人工)升高→自动提升审批等级
- 核心指标：人工介入率(太高→太保守)、自动化错误率(太高→太激进)，两者平衡

> 🏷️ M10/M21 | 📎 OpsPilot risk_gate(LOW_ONLY/NEEDS_APPROVAL/BLOCKED/NEEDS_HUMAN)+ loop guard

### Q91 RAG基本架构和工作流程

**核心**：→ 同 Q24，离线建库+在线检索生成+引用校验。知识密集型任务优势=可溯源的动态知识；局限=检索质量瓶颈+推理型幻觉不治。

> 🏷️ M1 | 📎 → Q24

### Q92 Agent建模的常见方法

**核心**：基于规划(Plan-first→O分解执行)、基于记忆(RAG历史→决策)、基于工具调用(Tool-only→ReAct)、反应式(直接映射→无规划)。

- 规划型：Planner拆任务→Executor执行→critic反馈。适合复杂多步任务。OpsPilot主干
- 记忆型：RAG检索历史经验→直接匹配方案。适合高频重复任务(客服常见问题)
- 工具型：LLM直接选tool+填参→执行。适合确定性高、单步任务
- 反应式：state→action的直接映射(规则/小模型)，延迟最低但灵活性差。适合简单路由
- 混合型（生产主流）：规则+小模型兜底确定性场景+LLM处理复杂推理。Orchestrator统一调度

> 🏷️ M10 | 📎 OpsPilot混合：triage规则兜底+planner LLM规划+fanout工具执行+critic规则裁决

### Q93 大模型Agent优缺点及未来方向

**核心**：→ 同 Q14/Q48，侧重当前局限+未来突破方向。

> 🏷️ M10/M19 | 📎 → Q14

### Q94 多Agent系统中实现协同工作的常见机制

**核心**：通信协议(结构化消息)+共享记忆(向量知识库)+角色分工(主从/专职)+仲裁裁决(不是投票辩论)。

- 通信：Agent间传递结构化JSON(state/action)而非自然语言→信息不丢失。主Agent派活→子Agent返回result
- 共享记忆：共享向量库存储历史经验→所有Agent检索同一个记忆池→间接协同
- 角色分工：主Agent(拆任务+汇总)、子Agent(专职执行，如查日志Agent/查K8s Agent)、仲裁Agent(裁决冲突)
- 最佳实践：主从模式(最安全可控)+只读执行(不共享排他资源)→避免多Agent通信的brooks定律困境

> 🏷️ M13 | 📎 OpsPilot evidence_fanout=主从模式(主fanout拆任务→4路子Agent并行取证→只读/不通信)

### Q95 ReAct vs Plan-Execute处理长上下文任务的对比

**核心**：ReAct每轮Observation全量保留→上下文膨胀快；Plan-Execute先计划再执行→中间步骤不需要Thought浪费token→更省上下文。

- 上下文管理：ReAct膨胀（每步Thought+Action+Observation全写进历史）；Plan-Execute紧凑（执行阶段无冗长Thought）
- 推理效率：ReAct每步推理都是连续的→长链推理容易Lost in Middle；Plan-Execute全局规划一次完成→推理集中高效
- 错误恢复：ReAct每步能纠错（观察-反思-修正）；Plan-Execute计划偏差→全盘错误→需replan
- 适用：长上下文+依赖图清晰→Plan-Execute；长上下文+不确定性高需边走边看→ReAct

> 🏷️ M11/M12 | 📎 OpsPilot图级Plan-Execute(planner→fanout) + 节点内ReAct + critic回边纠错

### Q96 Agent研究方向中最可能3-5年规模化落地的方向

**核心**：编程助手（coding agent）最成熟→已有GitHub Copilot/Cursor验证；其次领域客服Agent；再SRE Agent。

- Coding：技术成熟度最高(有编译器/测试做客观裁判)、需求最刚性(开发者付费意愿强)、成本效益(单次生成成本低)
- 电商/领域客服：市场需求大(降人力成本)、但情绪感知和安全合规是门槛
- SRE诊断：单Agent可用(信噪比高任务可分解)，但全自主仍需HITL准入
- 判据：有便宜可靠的客观裁判（编译器/测试/API校验）→Agent就能闭环迭代；纯主观任务（创作/咨询）→仍需人校验

> 🏷️ M19 | 📎 coding agent=有客观裁判能闭环→最早落地

### Q97 Agent基础能力的定义

**核心**：四件套——感知(输入解析)→规划(任务分解)→工具调用(外部操作)→反思(自我纠错)。加上记忆(短期+长期)贯穿四者。

- 感知：将自然语言/结构化数据转成Agent可理解的内部表示(intent+entities+context)
- 规划：把复杂目标拆成可执行的子任务序列+依赖图+优先级
- 工具调用：选择合适工具+填充正确参数+解释返回结果→决定下一步
- 反思：执行后评估输出质量+检测矛盾+决定是否重来
- 记忆：短期state(当前任务状态)+长期知识库(历史经验检索)
- 依赖：感知→规划→工具调用→反思，记忆贯穿全程。四者缺一即Shallow Agent

> 🏷️ M10 | 📎 OpsPilot 13节点=四件套的工程分解：intake(感知)→planner(规划)→fanout(工具)→critic(反思)

### Q98 Agent/RAG构建中的评估指标和方法

**核心**：→ 同 Q18(Q13)+Q19(M19)，三维度：相关性(检索召回/precision)、准确性(生成faithfulness/事实正确率)、效率(延迟/token/步数)。

- Agent评估三层：单步准确率(工具选对没)→任务完成率(端到端)→效率(token/步数/耗时)
- RAG评估两维：检索段(Recall/MRR/NDCG)→生成段(faithfulness/relevancy)
- 两者融合评估：上下文利用率(检索→生成的传递效率)
- 挑战：Agent动作序列无唯一正确路径→需要gold set标注+判卷器校准

> 🏷️ M18/M19 | 📎 Agent三层指标(M19) + RAG两维评估(M18)

### Q99 LLM Agent的外部工具定义、封装和集成

**核心**：→ Q11/Q15扩展——工具定义(JSON Schema)→注册(Registry)→LLM选型(function calling)→网关校验→执行→结果回灌。

- 定义：name(工具名)+description(何时用/何时不用/输入输出)+parameters(JSON Schema含type/enum/required/default/example)
- 封装：函数实现+超时+错误处理→包装成标准接口(success/data/error_code/elapsed_ms)
- 集成关键因素：①参数解析(LLM填的JSON可能不合法→schema校验兜底) ②错误处理(结构化错误返回让LLM知道重试还是换工具) ③可扩展性(动态注册新工具+按context裁剪工具列表)
- 安全：权限分级(只读/修改/高危)+审计日志+幂等防护

> 🏷️ M15 | 📎 OpsPilot Tool Gateway 7步链路(定义→注册→选择→校验→幂等→执行→回灌)

### Q100 Coding/GUI/Search三种Agent核心能力

**核心**：Coding=理解需求→生成代码(确定性判定，客观裁判最充分)。GUI=视觉感知→操作元素(不确定性最高)。Search=查询理解→检索知识(成熟度最高)。

- Coding：接收自然语言需求/错误日志→生成/修改代码→通过编译/测试/变异测试验证。代表：GitHub Copilot/Cursor/Devin
- GUI：接收截图/自然语言指令→识别UI元素+理解交互流程→模拟点击/输入/滚动→在真实界面上完成操作。代表：Claude Computer Use/UFO
- Search：接收查询→多源检索(向量/关键词/结构化)→整合答案+引用溯源。代表：Perplexity/RAG各种应用
- 技术成熟度：Search > Coding > GUI（GUI最不成熟因为无标准API+视觉识别不可靠+操作反馈长）

> 🏷️ M19 | 📎 Search(成熟度高)→Coding(有编译/测试裁判)→GUI(最不成熟)

### Q101 多Agent系统中Query改写的实现与训练评估

**核心**：Query改写=将用户原始query转换成更精准的检索query。训练=从真实日志采样+构造改写对+DPO/监督微调。

- 实现方式：规则(TERM_MAP术语映射/停用词去除)+LLM改写(去口语+补上下文+消歧)，线上线下双通道
- 数据采样策略：①取真实query+对应的点击/满意文档作为正样本改写对；②取检索效果差的query（低Recall/低MRR）重点采样（ROI高）；③负样本=改写后检索效果下降的query
- 训练：监督微调（query→理想改写query的序列对）+ DPO（好改写>A，坏改写>B）
- 评估：离线→改写前后Recall@k/MRR对比 + 改写保留语义率（是否改偏）；在线→核心业务指标（满意度/解决率）A/B测试

> 🏷️ M13/M8 | 📎 应用生成平台TERM_MAP+STOPWORDS；采样重点取效果差的query

### Q102 构建RAG系统评估数据集的方法

**核心**：问题来源(真实日志+专家造题)→答案标注(双人标注+仲裁)→负样本(难负例)→多样性保障(分层采样)。

- 问题来源：①真实用户query/工单（代表性高）②领域专家造题（覆盖边界case/对抗性）③线上badcase回流
- 标注流程：双人独立标注→算kappa→不一致题仲裁会→全员一致入gold set→打版本标签
- 负样本构造：easy negative(随机) + hard negative(BM25/向量检索得分高但不相关) → 防止模型偷懒
- 多样性：按业务域/难度/意图类型分层采样，保证每个格子有足够样本
- 关键：评测集需要版本标签+定期review，架构变更同步更新受影响的case（防腐烂）

> 🏷️ M18 | 📎 gold set构建三步骤(双标→kappa→对齐)；hard negative防作弊

### Q103 Agent/RAG系统完整评估体系设计

**核心**：→ 同 Q98，补：三层裁判塔架构 + 8步方法论 + 北极星向量。

- 三层裁判塔：被评测Agent(SUT)→判卷器(代码判+模型判)→gold set金标集(死数据校准判卷器)
- 北极星向量：P(准确率) + R(召回/覆盖) + 效率 + 成本 → 分维度报永不揉成一个总分
- 8步方法论(→见M19)：确认可验证→拆段→定义"对"→配裁判→建题库→建gold set→冻结世界→北极星

> 🏷️ M18/M19 | 📎 M19 完整8步评测方法论 + 三层塔

### Q104 如何构建高质量Agent/RAG评估数据集

**核心**：→ 同 Q102，侧重Agent：任务设计(action sequence标注)→标注策略(gold set+双标)→多样性→偏差控制。

- Agent特有：①状态快照(冻结环境/数据)→保证可复现；②动作序列标注(多路径可能都正确→标注"可接受路径集合")
- 数据采集：真实工单(正)+专家造题(边+对抗)+线上badcase→三层数据源
- 标注：多个正确答案路径均接受(不唯一)→需要判卷器判断"是否在可接受集合内"而非精确匹配
- 偏差控制：分布对齐(测试集query分布和线上真实分布一致)→避免只在简单/常见场景下评测

> 🏷️ M18/M19 | 📎 → Q102；Agent特有：动作序列多路径标注 + 环境冻结

### Q105 Coding/GUI/Search能力比较与短期落地判断

**核心**：→ 同 Q100，侧重落地判断：Search已落地(Perplexity/RAG)，Coding正在大规模落地(Cursor/Copilot)，GUI尚在早期。

- 落地难度：Search < Coding < GUI。根因=客观裁判的可获得性：Search(点击/满意度)→Coding(编译/测试)→GUI(无标准裁判)
- Search：技术最成熟、成本最低、ROI最清晰，已经是标配
- Coding：有编译器/测试做免费裁判，能闭环迭代，商业化已验证
- GUI：无API→视觉识别不可靠；无标准裁判→每次操作结果难验证；环境差异大→难迁移

> 🏷️ M19 | 📎 → Q100

### Q106 Coding/GUI/Search模块在Agent中的职责

**核心**：→ 同 Q100，侧重架构定位：Coding=执行层(文本→可运行代码)；GUI=感知-操作层(视觉→交互)；Search=知识获取层(查询→信息)。

- Coding：输入=需求/错误日志→处理=理解意图+代码生成/修改→输出=可运行代码+测试结果。定位：Agent的「动手」能力
- GUI：输入=截图/自然语言任务→处理=视觉感知+元素定位+操作序列规划→输出=界面操作结果。定位：Agent的「眼睛+鼠标」
- Search：输入=自然语言查询→处理=query改写+多路检索+信息整合→输出=带引用的结构化答案。定位：Agent的「外部记忆+知识获取」
- 三者关系：Search(获取信息)→Coding(生成方案)→GUI(部署/验证)

> 🏷️ M19 | 📎 → Q100

### Q107 构建高质量可复现的Agent/RAG评估数据集

**核心**：→ 同 Q102/Q104，侧重可复现：任务设计(覆盖度+难度分层)→标注策略(多人+kappa)→多样性→偏差控制+环境冻结。

- 可复现性保障：①环境冻结(Docker/snapshot)→每次跑相同；②模型版本钉死→不用最新版；③每次全量重跑不挑选
- 任务设计：简单/中等/困难3:4:3分布→防题型一面倒
- 标注：3人独立标→kappa(≥0.61)→对齐→全员一致的入gold set
- 注：gold set需要50-100条才稳（几十条置信区间太宽）

> 🏷️ M18/M19 | 📎 → Q102

### Q108 知识库更新策略及实时性/一致性/准确性保障

**核心**：增量追加(新文档独立embedding写入)+门控写回(只有人工确认的才入库)+版本标签管理(到期/变更自动下线)。

- 更新策略：①实时增量(少量新文档即时写入→HNSW天然支持增量)；②批量增量(大量新文档定时重建索引)；③门控写回(确认→写入，未经确认不入向量库)
- 实时性：新文档→清洗→分块→embedding→追加写入→异步更新索引(秒-分钟级)
- 一致性：chunk_id管理→同一文档更新→用chunk_id删除旧向量+插入新向量
- 准确性：门控写回(confirmed_by_human)防错误信息污染 + 版本标签定期review + LLM-as-Judge定期扫知识库质量
- 核心原则：写入收窄(只有确认的才入库)，读取放开。知识库污染比没知识库危害更大

> 🏷️ M9 | 📎 OpsPilot confirmed_by_human门控写回；增量追加embedding

### Q109 AI Agent的主要瓶颈及技术改进方向

**核心**：可靠性(分解+可验证+闸门)→可解释性(引用溯源+推理链)→长期记忆(RAG+门控写回)→多步推理(Plan+ReAct混合+回边纠错)。

- 可靠性瓶颈：长链路可靠性=0.9ⁿ急剧下降→解法：分解胜于强提示(每步0.98)、闸门分层(每步可验证不闯祸)
- 可解释性瓶颈：黑盒端到端→解法：分解+中间产物可视化(planner设计+critic评分+引用溯源)
- 长期记忆瓶颈：存什么/怎么检索/记多久→解法：结构化摘要+向量检索+门控写回+过期淘汰
- 多步推理瓶颈：长链推理漂移→解法：Plan+ReAct混合(图级计划+步骤级React+critic回边)+阶段性总结

> 🏷️ M10/M19 | 📎 OpsPilot四件套 + 分解+闸门+回边 就是对四瓶颈的工程解法

### Q110 理想AI Agent的核心能力

**核心**：→ 同 Q97(四件套)，加：文件系统(上下文卸载)+子Agent(上下文隔离)+HITL(人机协同)。现有技术：垂直领域Deep Agent已可用，通用自主性仍不足。

- 理想状态：自主规划+工具调用+记忆+反思+安全决策+跨领域迁移
- 现有技术：Deep Agent(OpsPilot)在下限定领域(SRE诊断)已可工作(0.98¹³≈0.77)，但通用自主(从零学新领域、跨模态、长周期任务)远未达到
- 差距：①通用规划(无领域知识从零推理)②可靠性上限(0.98¹³是顶)③自我进化(不靠人类修改prompt)
- 理由：当前最缺的不是模型能力，而是**便宜可靠的客观裁判**——有裁判才能闭环，闭环才能进化

> 🏷️ M10 | 📎 OpsPilot=手搓deep agent的四件套+HITL+文件系统+子Agent(扇出)

### Q111 多Agent训练流程的关键阶段

**核心**：环境建模→通信机制设计→协同目标设定→联合训练(集中训练分布式执行CTDE/对抗训练)→评估。

- 环境建模：定义状态空间(共享/私有)、动作空间(每个Agent的可用动作)、奖励函数(个体+团队奖励)
- 通信：显式(消息传递协议/共享记忆)vs隐式(通过环境间接协调)；离散vs 连续通信
- 训练范式：CTDE(训练时访问全局信息，执行时只用局部观察)→MADDPG/QMIX；对抗训练(GAN)→生成-判别
- 联合训练：各Agent独立策略网络→团队奖励 → 各自优化→ 周期性同步
- 评估：个体贡献评估(奖励塑形分配)；团队协作效率(通信开销/步数)；对抗鲁棒性

> 🏷️ M13/M19 | 📎 CTDE 集中训练分布式执行；多Agent RL vs 多Agent LLM编排

### Q112 MRR在RAG系统中的定义及特殊意义

**核心**：MRR的RAG意义——衡量「检索系统能否第一时间给对答案」→对于单正确答案场景(FAQ/事实问答)最关键。

- 特殊意义：RAG的「首条准确性」直接影响用户体验和生成质量——首条对→token省(不用翻很多文档)、幻觉少(正确context)
- MRR高=检索精准定位能力强；MRR低但Recall高=检索能召回但对的内容埋在后面→需要rerank精排
- 和NDCG互补：MRR衡量「第一下准不准」(适合单标准答案)，NDCG衡量「整体排得对不对」(适合多相关文档)

> 🏷️ M18 | 📎 rag2评测MRR用于衡量检索精准度；MRR vs NDCG互补

### Q113 NDCG计算公式及在IR/推荐中的应用

**核心**：`NDCG@k = DCG@k / IDCG@k`。DCG=`Σᵏ rel_i / log₂(i+1)`带位置折损的相关性加权和；IDCG=理想排序的DCG(rel降序)。

- DCG：位置i+1的折损因子log₂(i+1)→排在前面的高相关文档贡献更大
- IDCG：按真实相关性relevance降序排列计算的DCG→完美排序的理论上限
- NDCG值域[0,1]，1=完美排序
- 计算步骤：①定义相关性分级(0=无关/1=部分相关/2=高度相关)→②计算DCG→③计算IDCG(rel降序)→④NDCG=DCG/IDCG
- 应用：搜索结果排序(相关文档越靠前NDCG越高)、推荐系统(用户兴趣高的item排前面)

> 🏷️ M18 | 📎 DCG(位置+相关) / IDCG(理想上限) / NDCG(归一化)

### Q114 提升LLM输出准确性的多角度技术路径

**核心**：数据(高质量/去噪/配平)→训练(SFT+RLHF/DPO对齐)→推理(CoT/约束解码/low temperature)→外部增强(RAG/工具调用/校验)。

- 数据：数据质量 > 数据数量。去重/去伪/去偏见→SFT微调基础能力
- 训练：SFT(学格式/学能力)→RLHF/DPO(学偏好/学"不知道就说不知道")→Iterative refinement
- 推理：CoT(拆步推理)、Self-Consistency(多跑几次取多数)、约束解码(限定合法token空间)、temperature≈0
- 外部增强：RAG(注入事实)+工具调用(查真数据)+后处理校验(LLM二次审核)
- 可行性排序：RAG(最低成本/最快见效)>CoT(免费)>约束解码(分类场景)>DPO(有标注)>RLHF(成本最高)

> 🏷️ M9/M19 | 📎 多层防御：RAG(知识)→CoT(推理)→DPO(行为)→约束解码(格式)

### Q115 使用过的评测数据集及选择原因

**核心**：项目中使用自建评测集(非开源benchmark)——因为通用benchmark和SRE诊断/前端测试域差距太大。

- 自建RAG评测集：10条Golden case(真实query+标注相关文档)→用于Query改写+Rerank两阶段检索的AB归因
- 自建agent评测集：28组mock工单→用于critic仲裁测试(规则表 vs LLM裁判对比：LLM不一致率39%→选规则表)
- 选自建原因：领域专用任务(故障诊断/前端自愈)无开源benchmark覆盖；需测试的边界case(跨层矛盾/假红vs真红)自己造
- 对模型性能的反映：小样本评测(<50道)统计置信区间宽→结论需标注误差范围(如"79%±5.5")，不能裸报数字

> 🏷️ M18/M19 | 📎 OpsPilot自建28组mock工单 + rag2 10条Golden case；通用benchmark不覆盖领域需求

### Q116 保障LLM输入输出准确性的技术手段

**核心**：输入校验(规则+LLM扫异常)→推理过程可观测(CoT+中间输出)→输出校验(语法/格式/事实核查)→反馈闭环(用户纠错回流)。

- 输入保障：结构化表单(防NL歧义) + 意图识别(Router分类) + 中间插入校验节点（事前检测异常）
- 生成保障：CoT推理链可追溯 + 格式校验(JSON schema/prompt指定) + 事实核查(引用比对/RAG溯源)
- 反馈闭环：badcase回流→评测题库新增→回归测试防退化→如果发现退步→挡住上线
- 测试框架：CI评测门禁——改prompt/配置→跑题库回归→北极星掉出误差范围→禁止合入

> 🏷️ M9/M19 | 📎 CI评测门禁(守agent)+gold set(守判卷器)→双门禁防输入输出漂移

### Q117 LLM自动评价和人工评价指标对比

**核心**：自动指标(BLEU/ROUGE/精确匹配→速度快但无语义理解)→模型评判(G-Eval/GPTScore→有语义但抖)→人工(事实准确性/流畅度/有用性→最准但贵)。

- 自动指标：BLEU/ROUGE基于n-gram重叠→速度快/成本低，但不理解语义同义改写(«改得好»和«优化了»得0分)
- 模型评判(LLM-as-Judge)：G-Eval用LLM打分、GPTScore用概率评估→有语义理解，但会抖(今天判对明天判错)、偏好长答案
- 人工评估：事实准确率、回答完整性、流畅度、有用性→标准最真实但昂贵/慢/不可规模化
- 最佳组合：日常回归→自动+LLM-as-Judge快速；关键版本→人工gold set校准判卷器(kappa≥0.61)；上线→A/B真实用户满意度

> 🏷️ M18/M19 | 📎 三层组合：自动(量) + LLM-Judge(速) + 人工(质) + gold set(校准)

### Q118 缓解LLM幻觉和安全风险的多层面方法

**核心**：训练数据(去毒/去偏见)→模型架构(safety RLHF/约束解码)→推理控制(RAG+CoT)→后处理(安全过滤器)→评估(红队测试)。

- 训练数据：去毒(过滤有害内容)、去偏见、去PII(个人隐私)→SFT
- 模型对齐：RLHF/DPO训练模型拒绝有害请求、知道什么不该说
- 推理层：RAG(注入可信事实→治知识缺失)、CoT(公开推理链→可审查)、constraint decoding(限定输出空间)
- 后处理：安全检测API(OpenAI Moderation)、敏感词过滤、输出二次审核
- 评估：红队测试(对抗攻击)、安全benchmark(TruthfulQA/RealToxicityPrompts)

> 🏷️ M9 | 📎 多层纵深防御：数据(源头)→训练(对齐)→推理(RAG+CoT)→后处理(安全filter)

### Q119 判别式转化为生成式任务的性能比较

**核心**：不同转化方法无「统一最优」——取决于任务性质、数据量和基模型能力。分类/情感分析→简单prompt即可；多标签/复杂关系→结构化输出+few-shot。

- 方法1：直接生成标签（"正面/负面"）→简单，但对异常输出无保护
- 方法2：生成+约束解码（限定合法token集合）→分类场景精准度高、不受prompt漂移影响
- 方法3：生成+后校验（正则/规则提取标签）→兼容性好但可能丢失信息
- 影响性能因素：①基模型大小（大模型zero-shot好，小模型需few-shot）②任务标签数（多标签=生成式比分类头更灵活）③label语义性（标签有语义→生成式优势大）
- 结论：分类头仍是数字精度最高的（有概率输出+可校准），但生成式在灵活性和零样本能力上有优势

> 🏷️ ML general | 📎 约束解码(分类场景最优) > 后校验 > 裸生成

### Q120 为何验证集和测试集要分开

**核心**：验证集用于模型选择+超参调优→会overfit到验证集分布。测试集用于最终泛化能力评估→必须「从未被用于任何决策」才能诚实反映泛化性能。

- 分开原因：如果合并→你会用测试集做模型选择（选在合并集上表现最好的模型）→测试集信息泄露→评估乐观偏差
- 导致问题：①模型选择偏差(选了过度适配test集噪声的模型)②泛化能力高估(报告90%实际上线70%)
- 正确做法：训练集调参→验证集选择最佳模型/epoch→测试集仅运行一次报告结果→不动任何超参
- 特殊情况：小数据集(不足)用交叉验证替代，但每个fold的test严格不能参与该fold的模型选择

> 🏷️ ML fundamental | 📎 train/val/test三者不可交叉；test严格只用一次

### Q121 近期重要学术论文及技术启发

**核心**：面试中的论文讨论应选2-3篇有深度理解且能关联项目经验的论文，而非堆砌数量。

- 推荐框架：选「你真正读透+能讲清楚贡献+能关联项目」的论文
- 经典推荐方向：①RAG系(ReAct/self-RAG/GraphRAG)—聊RAG从线性到迭代的演进→关联OpsPilot critic回边；②Agent系(Reflexion/Toolformer/Devin)—聊Agent从工具调用到反思的跃迁；③评测系(G-Eval/RAGAS)—聊LLM-as-Judge的挑战和校准→关联gold set
- 关键话术：不只说"这篇论文做了什么"，要说"它改变了我对X的设计判断——比如读完Reflexion后，我把OpsPilot的critic设计从纯自评改为外部信号驱动"
- 启发：最有价值的论文不一定是SOTA刷榜，而是那些改变了你**设计直觉**的——比如ReAct教会我「不要一口气猜到底」、RAGAS教会我「分维度打分不揉总分」

> 🏷️ 论文讨论 | 📎 选2-3篇真读透+能关联项目；讲"它改变了我的什么判断"而非"它做了什么"
