# 作战计划 — Agent 开发工程师

> 目标：全栈 Agent 工程师，月 base 30k+，中国大陆大厂/AI独角兽
> 策略：Harness 体系认知作差异化壁垒 + 三项目各打一个深度故事 + 定向补后端高频题
> 时间：零散时间，3.5 周（截止 7月1日）

---

## 一、开场定位（2 分钟）

> 我有 7 年前端研发经验，近一年重点投入 AI Agent 工程化落地。参与了三个方向：企业级研发 Harness（前端自动化测试能力域）、自然语言驱动的应用生成平台（负责意图识别设计），以及 SRE 运维智能体（个人项目，复刻公司 SRE 场景）。
>
> 我的核心判断是：Agent 的可靠性不来自模型，来自 Harness——确定性编排包裹非确定性 Agent，结构化契约替代自然语言交接，证据驱动的质量门禁替代 LLM 的自我报告。这套思路我从产品设计层理解到了代码实现层。

**定位关键词**：AI Harness 工程化 / Agent 编排 / 证据驱动 / 前端 + Agent 全栈

---

## 二、三个项目的深度故事

### 项目 1：开发套件 — 前端自动化测试能力域

**一句话价值**：把前端 Bug 修复从"AI 写完人工验收"变成"Playwright 真实执行 + 截图取证 + 失败归因 + 缺陷流转"的全自动闭环。

**深度故事（5 分钟版）**：

1. **问题**：AI 生成前端代码后，验收靠人肉，不可规模化。10 个团队同时在用 AI 写代码，测试依然是瓶颈。
2. **我设计了什么**：将"前端验证"拆成 8 个原子能力节点——测试范围识别 → 用例生成 → 环境准备 → Playwright 执行 → 证据采集（截图/Console/Network/Trace） → 失败归因（代码/环境/数据/用例/Flaky 五分类） → 缺陷流转 → 修复复测
3. **核心设计决策**：为什么执行结果要落成 evidence pack 而不是 Agent 口头报告？——证据高于断言这条内核。LLM 可以撒谎，浏览器截图不会。
4. **最难的部分**：失败归因的五分类逻辑——同时看 Console、Network、Trace 和重试结果的组合，才能区分代码问题 vs 环境问题 vs Flaky
5. **数据**：典型后台功能研发从 2.2 天缩到 4 小时；试点覆盖 10+ 业务团队

**追问备答**：

| 追问 | 答法 |
|------|------|
| Playwright Worker 和 API 服务怎么隔离？ | 独立 Worker 进程/容器，不混部，浏览器进程内存隔离 |
| 测试数据怎么隔离？ | 每个任务独立测试环境，用例级数据清理，不污染其他任务 |
| Flaky 怎么识别？ | 重试结果不一致 + 失败集中在时序/异步加载，单独标记，不纳入门禁判断 |
| Bad Case 怎么管理？ | 分类（范围遗漏/选择器失效/环境误判/Flaky）→ 聚类排优先级 → 修复 → 回归 |
| Playwright Worker 内存泄漏怎么处理？ | try/finally 保证 context.close() + browser.close()，容器级别有 OOM 自动重启 |

---

### 项目 2：应用生成平台 — 意图识别（Router 层）

**一句话价值**：应用进入修改阶段后，设计了场景化 RAG 意图增强机制，让 Router 能准确识别用户想改什么，派发到正确 Planner。

**深度故事（5 分钟版）**：

1. **问题**：页面生成容易，修改阶段意图识别准确率低。"把按钮改成红色" vs "加一个红色提交按钮"是两种不同操作，朴素 LLM 分类错误率很高。
2. **方案**：Router/Planner 分层 + 场景化 RAG。用历史修改场景、任务类型样例、平台执行规则作为语料，为 Router 提供相似案例参考，提升意图识别稳定性。
3. **核心取舍**：为什么不直接用 LLM few-shot？——不确定性太高，当用户描述不标准时 few-shot 容易漂移；RAG 召回相似案例的方式对边界 case 更稳定。
4. **技术选型**：ts 版 LangGraph 跑在前端静态代码（快速 PoC 验证，避免早期部署复杂度；产品化阶段会拆到服务端）
5. **数据**：10+ 业务团队试点，30+ 应用原型，典型轻应用原型从 1-2 天缩到 30-60 分钟

**追问备答**：

| 追问 | 答法 |
|------|------|
| 为什么 Agent 逻辑放前端？ | PoC 阶段降低部署复杂度，快速验证核心路径；下一步会拆到服务端，前端只保留 UI 层 |
| RAG 语料多少条？怎么评估效果？ | 沉淀历史修改场景 + 人工标注样例；用 Golden Case 集合评估意图识别准确率 |
| Router 分类出错了怎么办？ | Planner 执行前会做结构化输入校验，错误分类会在 Planner 层被发现，回退到 Router 重判 |
| 增量修改怎么识别要改哪些部分？ | 基于新旧页面 Schema diff + 用户指令，识别变更范围，避免全量重构 |

---

### 项目 3：OpsPilot — Harness 整体设计

**一句话价值**：个人项目，复刻公司 SRE 运维诊断场景，用 LangGraph + FastAPI 实现 13 节点 Harness，核心验证了 checkpoint 持久化、Human-in-the-loop、evidence 驱动质量门禁三个生产级特性。

**深度故事（5 分钟版）**：

1. **为什么做这个**：公司 AI 运维智能体我是参与者，想通过个人项目把整个 Harness 从头实现一遍，加深理解。用 Python/LangGraph 是刻意的——补后端技能。
2. **13 个节点的拆分逻辑**：intake → triage → retrieve_memory → planner → evidence_fanout → evidence_aggregate → diagnose → critic → remediation → risk_gate → approval_interrupt → executor → verify → rca。每个节点单一职责，失败可独立重试。
3. **三个最重要的设计决策**：
   - **为什么要 critic 节点**：LLM 有确认偏误，diagnose 给出根因后会找支持证据而不是反例。critic 专门攻击 diagnose 结论，是"证据高于断言 → 反证"的落地。
   - **为什么 evidence 要持久化**：GraphRunner 在每个节点完成后写入 DB，不依赖 LangGraph 内存状态。这是"状态外置"内核。
   - **为什么拆 13 个节点而不是一个大 Agent**：分解胜于强提示——0.9^1 的可靠性远低于 0.98^13 每步可验证的可靠性。
4. **诚实说局限**：Python 是边学边用，对部分实现不如前端熟悉；没有真实生产流量，是个人 PoC 级别。

**追问备答（高危区）**：

| 追问 | 答法 |
|------|------|
| LangGraph checkpoint 机制怎么工作的？ | thread_id 是主键，CheckpointTuple 存 channel_values（全量状态快照）、channel_versions、pending_writes；实现上用 InMemorySaver，生产换 RedisSaver |
| Human-in-the-loop 怎么实现？interrupt 后怎么恢复？ | interrupt() 依赖 checkpointer，暂停后把 payload 通过 stream API 暴露；恢复用 Command(resume=<人工输入>)，从 checkpoint 继续 |
| evidence_fanout 并发怎么实现的？ | asyncio.gather() 并发调用多个工具适配器，每个适配器有独立超时，单个失败不阻塞整体 |
| Pydantic 对象从 checkpoint 反序列化后变成 dict，怎么处理？ | `ticket.service if hasattr(ticket, 'service') else ticket.get('service', 'unknown')`，兼容两种形式 |
| risk_gate 的判断逻辑？ | 基于 remediation 输出的风险等级和影响范围，规则硬编码：写操作/生产环境/数据删除必须走 approval |
| 这个项目 AI 写了多少？ | 大部分实现由 coding agent 完成，我主导了系统设计、节点划分、关键设计决策。Python 代码我能读懂和调试，但从零写需要时间。 |

---

## 三、面试官问题穷举

> 🔴 = 高危，必须答两层  🟢 = 优势，主动引导

### A. 开场确认

1. 你之前是前端，为什么转 Agent 开发？
2. 这三个项目你分别是什么角色？主导了什么？
3. 华为 OD 是什么性质？你做的工作是团队项目还是你个人主导？
4. 你的代码贡献量大概是什么水平？

### B. 开发套件深挖

5. 🟢 前端自动化测试能力域，你从哪些维度设计的？
6. 🟢 2.2 天缩到 4 小时，具体哪个环节省了时间？
7. 测试用例是 AI 生成还是手写的？生成质量怎么保证？
8. 🔴 Playwright Worker 和 API 服务怎么隔离？资源怎么限制？
9. 截图和 Console 日志存在哪里？S3 还是 DB？
10. 🔴 Flaky 测试识别机制怎么设计的？
11. 失败归因五分类的判断逻辑是什么？优先级怎么排？
12. Bad Case 管理的闭环是什么？从发现到回归多长时间？
13. 这套能力在几个团队试点了？推广遇到过什么阻力？

### C. 应用生成平台深挖

14. 🟢 Router 和 Planner 怎么分层的？各自负责什么？
15. 🟢 场景化 RAG 的语料怎么积累？效果怎么评估？
16. 🔴 为什么把 Agent 逻辑写在前端静态代码里？这有什么隐患？
17. LangGraph ts 版本和 Python 版本有什么坑？
18. 增量修改怎么识别变更范围？
19. 生成的代码质量怎么保证？有没有代码规范检查？
20. Sandpack 在线预览有没有遇到性能问题？
21. 多租户隔离怎么做的？

### D. OpsPilot 深挖

22. 🟢 为什么是 13 个节点？拆分依据是什么？
23. 🟢 critic 节点和 diagnose 怎么交互？它怎么"攻击"诊断结论？
24. 🔴 LangGraph checkpoint 机制是怎么工作的？channel_values 是什么？
25. 🔴 Human-in-the-loop 代码层面怎么实现？interrupt 后怎么恢复？
26. 🔴 evidence_fanout 并发机制是什么？单个工具超时怎么处理？
27. 🔴 Pydantic 从 checkpoint 反序列化变成 dict 的问题你怎么处理的？
28. risk_gate 的规则是什么？能不能绕过？
29. RCA 结果写回知识库有没有防污染机制？
30. 🔴 这个项目哪些代码是你自己写的？executor.py 里的幂等怎么实现的？
31. 如果上生产，你觉得最需要补的是什么？

### E. 后端工程基础（高危区）

32. 🔴 FastAPI async def 底层是怎么工作的？Event Loop 是什么？
33. 🔴 Agent 任务在后台运行，SSE 断了任务会停吗？为什么？
34. 🔴 Worker 崩溃了任务怎么恢复？Task Lease 是什么？
35. 🔴 两个节点并发更新同一份 State 会发生什么？乐观锁怎么做？
36. 🔴 工具调用失败了，什么情况下可以重试，什么情况下不能？
37. LangGraph 状态怎么持久化的？你用的什么 checkpointer？
38. SSE 的 Last-Event-ID 是什么？你实现了断线续传吗？
39. Tool Gateway 怎么保证幂等？幂等键怎么设计？
40. DB 提交成功但工具执行失败，怎么保证一致性？
41. 🔴 K8s Pod 重启后 Agent 状态怎么恢复？

### F. LangGraph 框架（中危区）

42. 🟢 LangGraph 和 LangChain 的区别是什么？
43. 🟢 add_conditional_edges 怎么用？path 函数返回什么？
44. Send 实现 Map-Reduce 并发是什么意思？你用过吗？
45. 🔴 checkpoint 的 thread_id、channel_values、versions_seen 各是什么？
46. 图执行到一半要等人工审批，代码层面怎么实现？
47. 流式输出 token-level 和 node-level 有什么区别？
48. 子 Agent 作为 tool 和作为子图有什么区别？
49. 你用的是哪个版本的 LangGraph？有没有遇到版本升级的 breaking change？

### G. LLM / RAG 基础

50. 意图识别为什么不用 Fine-tune 用 RAG？
51. 混合检索（BM25 + 向量）的 RRF 融合怎么工作？
52. Chunking 策略用的什么？overlap 怎么设置？
53. Embedding 模型选的什么？为什么？
54. Rerank 用了吗？cross-encoder 和 bi-encoder 的区别？
55. Langfuse / LangSmith 能追踪到什么粒度？
56. 模型幻觉缓解手段有哪些？你具体用了哪些？

### H. 系统设计题

57. 🟢 设计一个生产级 SRE 故障诊断 Agent，画整体架构（就是 OpsPilot）
58. 设计一个企业级 AI Coding 助手，如何保证生成代码的质量？
59. evidence_fanout 要并发查 10 个工具，怎么控制超时和失败降级？
60. 🔴 如果要支持 1000 个并发 Agent 任务，架构怎么改？
61. 如何设计 Agent 的离线评测体系？数据集怎么构建？
62. 🟢 如何防止 Agent 调用危险工具？你的 Tool Gateway 是怎么设计的？

### I. Harness 体系认知（你的差异化）

63. 🟢 Harness Engineering 的核心是什么？用一句话说
64. 🟢 Context / Capability / Constraint 三层为什么要分离？
65. 🟢 "可靠性来自结构不来自 prompt"，你能解释一下吗？
66. 🟢 证据高于断言，在你项目里怎么体现的？
67. 🟢 critic 节点为什么值得单独存在？
68. 🟢 企业大规模推广 Agent，最大的挑战是什么？你怎么看？

### J. 行为面试

69. 你为什么从前端转 Agent 开发？不担心竞争力吗？
70. Python 是边学边用，你遇到的最大挑战是什么？
71. 如果给你一个纯后端 Agent 服务需求，你会怎么开始？
72. 和后端工程师合作时，最大的摩擦点是什么？
73. 5 年后你希望自己是什么角色？

---

## 四、高频追问链标准答案（必背）

### 链路一：FastAPI 异步模型
> Uvicorn 启动一个 asyncio Event Loop，每个 async def 是协程，遇到 await 让出 CPU，I/O 完成后恢复。单进程内并发处理成千上万请求，不需要多线程。LLM 调用是 I/O 密集型，异步完全够用；CPU 密集型（文档解析/代码扫描）要放进程池。

### 链路二：SSE 断线后 Agent 要不要停
> 不停。连接生命周期 ≠ 任务生命周期。Agent 在后台线程执行，状态持久化到 DB，和 SSE 连接完全解耦。前端断开只关闭推流通道，Agent 继续跑，重连后从 DB 拉历史事件。

### 链路三：Worker 崩溃恢复（Task Lease）
> 每个 RUNNING 任务有 lease_expires_at，Worker 每隔 N 秒续租。Worker 崩溃后不续租，watchdog 定时扫描 lease_expires_at < now() 的任务，重置为 PENDING，其他 Worker 重新领取。

### 链路四：乐观锁防 Lost Update
> `UPDATE agent_runs SET state=:new_state, version=version+1 WHERE id=:id AND version=:old_version`，影响行数为 0 说明并发冲突，重试或报错。

### 链路五：工具调用幂等
> 幂等键 = sha256(run_id + tool_name + input_hash)。重试时相同参数命中相同键，服务端返回缓存结果而不是重新执行。已经返回部分流式 Token 的 LLM 请求不重试（幂等性破坏）。

### 链路六：LangGraph checkpoint
> thread_id 是主键，CheckpointTuple 核心字段：channel_values（全量状态快照）、channel_versions（各 channel 版本向量）、versions_seen（节点已见版本）、pending_writes（未提交写操作）。生产用 RedisSaver 替代 InMemorySaver。

### 链路七：1000 并发 Agent 架构
> API 和 Worker 解耦：POST /runs 写 tasks 表（PENDING）立即返回 run_id；Worker 池用 FOR UPDATE SKIP LOCKED 抢任务；每个 Worker 用 asyncio.Semaphore(20) 限制并发 LLM 数量；checkpointer 换 RedisSaver 支持多实例共享；SSE 推送换 Redis Pub/Sub 跨实例。

### 链路八：Saga 补偿
> 每步定义正向操作和补偿操作，任意步骤失败时按反向顺序执行补偿（关闭 MR → 删除分支 → 回滚部署）。补偿是业务级尽力而为，不是技术级精确回滚；补偿操作本身也要幂等。

---

## 五、诚实但不失分的话术

**Q: 这个项目你写了多少代码，你真的懂 executor.py 吗？**
> "OpsPilot 的实现大部分由 coding agent 完成，我主导了系统设计、节点划分和关键设计决策。Python 代码我能读懂和调试，executor.py 里的幂等逻辑是基于 call_id 唯一约束 + 状态机，我可以解释设计意图，但如果你要问具体某行代码的细节，我可能需要确认一下。我不想给你一个错误的答案。"

**Q: 你没有后端生产经验，怎么保证能做 Agent 后端开发？**
> "你说得对，这是我的短板。我的判断是 Agent 后端的核心复杂度不在 CRUD，在状态管理、LLM 编排和工具调用的可靠性设计。这些我通过 OpsPilot 有了第一手实践。后端基础知识——FastAPI 异步、checkpoint、幂等——我在持续补。如果团队有经验的后端愿意 review 我的代码，我相信学习曲线是可以跨过去的。"

**Q: 你说 Harness 体系，但这不就是工作流编排吗？有什么新东西？**
> "区别在于 Harness 有七个不变内核，每个都来自 LLM 的固有属性。比如'控制权归确定性系统'是因为 LLM 无界，'证据高于断言'是因为 LLM 会幻觉。这不是对工作流的重新命名，是从建材属性推导出来的对策体系。"

---

## 六、执行计划（3.5 周）

| 时间 | 任务 |
|------|------|
| 第 1 周 6/7-6/14 | 三个项目深度故事各练 3 遍（口述不看稿）；读 graph_runner.py + executor.py 搞清楚实现 |
| 第 2 周 6/15-6/21 | 刷 agent开发面试.md 的 25 道重点题，每天 3-4 题；重点：FastAPI异步/SSE/checkpoint/乐观锁/幂等/Saga |
| 第 3 周 6/22-6/28 | 用本文件问题清单自问自答，高危题反复练到不卡顿 |
| 最后 3 天 6/29-7/1 | 停止刷题，收口整理；准备 2-3 个问面试官的问题 |
