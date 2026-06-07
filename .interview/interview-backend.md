你说得对。上一版更多是在考：

- 模块是否齐全
- Agent 流程是否合理
- 产品是否可治理

但后端面试官真正想判断的是：

你是否能把一个非确定性的 Agent，做成高并发、可恢复、数据一致、可观测、可扩展的生产系统。

重点应落到：

进程与线程
协程与事件循环
连接池
事务边界
锁与并发控制
幂等与重复执行
消息可靠性
状态持久化
故障恢复
缓存一致性
分布式调度
网络与流式协议
容器隔离
数据库建模
性能和容量

下面重新给一版更偏后端技术深度的 100 题。

⸻

一、Agent Runtime 与并发模型

1. Agent 服务为什么通常使用异步框架？异步能解决什么问题，不能解决什么问题？

答：异步解决的核心问题是 I/O 等待时的 CPU 空转。Agent 服务本质上是 I/O 密集型——网络 I/O（HTTP 调用）、模型调用（LLM API 请求）、工具调用（数据库查询、外部 API）。异步让一个线程在等待 I/O 时去处理其他请求，大幅提升吞吐。异步不能解决 CPU 密集型任务（文档解析、代码扫描、加密计算），在这些场景下异步不会加速执行，反而因事件循环开销变慢。

OpsPilot 做法：FastAPI async def 路由层是异步的，但图中节点的 LLM 调用使用同步 complete_sync()，运行在后台线程的 asyncio.run() 隔离事件循环中，是一个"异步框架包裹同步执行"的混合模型。

2. FastAPI 的 async def 底层是如何执行的？

答：底层链路：Uvicorn（ASGI 服务器）→ ASGI 协议 → Event Loop（asyncio 事件循环）→ Coroutine。Uvicorn 启动一个 asyncio 事件循环监听端口，每个请求进来事件循环调度 async def 路由为协程。当协程执行到 await（如 await some_io()），协程挂起，事件循环处理其他任务。I/O 完成后协程恢复执行。单进程内可并发处理成千上万个连接，不需要多线程。

OpsPilot 做法：app/main.py 使用 FastAPI + uvicorn app.main:app --reload --port 8000。健康检查 /healthz 和 SSE 流端点 stream_events 都是 async def。SSE 端点使用 async for 从 EventBus 的 asyncio.Queue 中消费事件。

3. 在异步接口中调用同步数据库驱动或同步 HTTP SDK 会发生什么？

答：事件循环被阻塞，无法处理其他请求。如果所有请求都走同步调用，相当于退化为单线程串行处理。

OpsPilot 现状：这正是项目的现状。repositories/__init__.py 使用 sqlalchemy.create_engine()（同步引擎），SessionLocal 是同步 session。图中所有节点调用 llm_client.complete_sync()（使用 requests 库）。当图在后台线程中运行时（_run_graph_bg 中的 asyncio.run()），阻塞发生在新创建的隔离事件循环中，不阻塞主 API 线程。但如果 API 路由本身需要同步 DB 操作（如 POST /runs 中创建 run 记录），会短暂阻塞 API 事件循环。

4. Python 的 GIL 对 Agent 服务有什么影响？

答：I/O 密集型操作（网络请求、文件读写）：GIL 在 I/O 等待时释放，影响很小。CPU 密集型操作（JSON 序列化、数据聚合、加密）：GIL 导致无法并行利用多核。混合场景：多线程下 GIL 导致线程间争抢，反而可能比单线程慢。

OpsPilot 关键场景：evidence_fanout_node 使用 asyncio.gather() 并发调用多个工具。如果工具返回大量 JSON（如 query_logs 返回千行日志），Python 解析 JSON 是 CPU 操作，受 GIL 限制——gather 里的任务实际上是串行解析的。绕过方式：对真正的 CPU 密集型任务应放到进程池或独立 Worker 中。

5. LLM 请求属于 CPU 密集型还是 I/O 密集型？

答：毫无疑问是 I/O 密集型。模型推理在远端 GPU 服务器上执行，Agent 服务只需要发送 HTTP 请求（少量字节的 prompt）+ 等待网络返回（耗时占比 >99%）+ 接收流式/完整响应。典型 30 秒超时中的 29.9 秒都在等待网络 I/O。

OpsPilot 证实：llm_client.py 中 complete_sync() 使用 requests.post(url, ..., timeout=30)。SSE 流式场景下每个 Token 到达时需要 CPU 处理（JSON 解析、事件分发），但相比网络延迟可以忽略。

6. Playwright、文档解析和代码扫描应该放在线程池、进程池还是独立 Worker？

答：Playwright 浏览器操作 → 独立 Worker（K8s Job）。浏览器进程不隔离会泄漏内存；Playwright 启动 chromium 子进程，与 API 服务混部会导致资源竞争。文档解析（PDF/Word）→ 进程池。CPU 密集型，需要利用多核。代码扫描 → 进程池。CPU 密集型，可能有安全风险（扫描不可信代码），需沙箱隔离。

OpsPilot 现状：暂无 Playwright 集成；文档解析和代码扫描还未实现。工具适配器（tools/adapters/__init__.py）预留了 Playwright 相关工具的 mock 定义。

7. Uvicorn 多 Worker 和单 Worker 异步并发有什么区别？

答：单 Worker：一个进程一个事件循环，所有连接在一个事件循环中并发处理。优点是无共享数据无需进程间竞争，内存状态直接可用；缺点是只能用一个 CPU 核，一个请求阻塞整个进程。多 Worker（uvicorn --workers 4）：多个进程各自独立事件循环，操作系统负责负载均衡。优点是利用多核 CPU，一个 Worker 崩溃不影响其他；缺点是进程间不共享内存，Agent 状态不能只存本地内存。

OpsPilot 现状：启动命令 uvicorn app.main:app --reload --port 8000 没有 --workers 参数，默认单 Worker 单进程。--reload 通常用于开发环境。

8. 多 Worker 模式下，为什么不能把 Agent 状态只保存在进程内存中？

答：三个原因。请求可能打到不同 Worker：用户发起 Agent 任务后，后续查询状态/获取 SSE 流的请求可能被负载均衡到另一个 Worker。进程隔离：每个 Worker 是独立进程，内存不共享。Worker 重启：部署更新或 Worker 崩溃重启后，内存状态全部丢失。

OpsPilot 实践：所有状态持久化到数据库——图状态 → incident_checkpoints 表（state_json JSON 列），事件 → incident_run_events 表，证据 → incident_evidence 表。SSE 流用 EventBus（基于 DB 事件 + asyncio.Queue），但 EventBus 自身是内存的，当前单 Worker 没问题。如果未来切多 Worker，EventBus 需要换成 Redis Pub/Sub。

9. 一个 Agent API 实例最多能同时承载多少个模型流式请求？如何估算？

答：估算公式：最大并发数 ≈ (总可用 RAM - 系统预留) / (单请求峰值内存)，但实际瓶颈是操作系统文件描述符限制和网络连接池大小。

OpsPilot 估算：llm_client.complete_sync() 使用 requests 库，默认 urllib3 连接池最大 10 个连接（每个 host）。同步调用意味着调用线程被阻塞，BackgroundTasks 使用线程池（FastAPI 默认 ThreadPoolExecutor，max_workers ≈ CPU 核数 × 5）。如果 CPU=4，max_workers≈20，最多同时处理 20 个模型的同步请求。每个请求 30 秒超时，则 20 × (30/平均响应时间) 的吞吐。改善建议：改为 complete_async()（已存在，使用 aiohttp）后理论上可同时处理数百个流式请求。

10. 如何限制单实例同时运行的 Agent 数量，避免模型请求拖垮服务？

答：可讨论四种方案。Semaphore（信号量）：asyncio.Semaphore(N) 限制并发协程数，超出时排队等待。Worker Pool（固定线程池大小）：ThreadPoolExecutor(max_workers=N) 限制后台线程数。Admission Control（准入控制）：在 API 入口检查当前运行数，超过阈值返回 429 Too Many Requests。Queue（队列）：使用消息队列（RabbitMQ/Redis）做缓冲，Worker 以固定速率消费。

OpsPilot 现状：项目没有任何限流/准入控制。POST /runs 直接 background_tasks.add_task(_run_graph_bg)，同时提交 100 个工单会启动 100 个后台线程，全部尝试调用 LLM，导致连接池耗尽、LLM API 被限流、内存飙升。建议在 RuntimeService.start_run() 中增加 asyncio.Semaphore 或使用 Settings.max_concurrent_runs 配置项控制。

⸻

二、HTTP、SSE 与长连接

11. 为什么长时间 Agent 任务不适合一直占用普通 HTTP 请求？

答：普通 HTTP 请求的生命周期 = 客户端连接的生命周期。Agent 任务执行 5 分钟，HTTP 连接也要保持 5 分钟，带来四个问题。连接资源浪费：Web 服务器（如 Nginx/ALB）有 proxy_read_timeout（通常 60 秒），超过会断开。无恢复能力：浏览器刷新、网络闪断后整个请求丢失。客户端阻塞：用户无法关闭页面，否则任务中断。Worker 爆炸：每个请求占用一个线程/协程 5 分钟，吞吐急剧下降。

OpsPilot 做法：POST /runs 立即返回 { "run_id": "run_xxx", "status": "PENDING" }，后台执行，前端通过 GET /runs/{run_id}/stream（SSE）获取事件流。

12. SSE 和 WebSocket 在 Agent 流式输出中如何选择？

答：SSE 基于 HTTP 长连接，服务器→客户端单向，浏览器原生 EventSource API 支持自动重连（Last-Event-ID），对代理更友好。WebSocket 是独立 TCP 连接（ws://），全双工，适合实时对话和双向通信，但需要自行实现重连逻辑。Agent 流式输出是"服务器主动推送事件"模式，客户端不需要发送数据（除了初始请求），SSE 更合适。

OpsPilot 选择：SSE。使用 sse_starlette.EventSourceResponse 实现 GET /runs/{run_id}/stream。

13. SSE 的底层协议是什么？浏览器断线后如何恢复？

答：底层就是 HTTP。服务器回复 Content-Type: text/event-stream，然后逐步发送格式化的文本行：每个事件由 data: 行和可选的 id: / event: 行组成，空行分隔。断线恢复：浏览器 EventSource 在断开后自动重连，重连时发送 Last-Event-ID 头，值为最后收到的 event_id，服务器据此决定从哪开始重发。

OpsPilot 实现：incidents.py:stream_events 使用 EventSourceResponse。EventBus 的 async for 消费 asyncio.Queue。如果客户端断线后重连会新建 Subscriber，从当前最新事件开始，不会回溯历史。历史事件通过 GET /runs/{run_id}/events?last_event_id=... 单独提供。

14. SSE 的 Last-Event-ID 有什么作用？

答：断线重连时告诉服务器"我最后收到的消息是 ID=X，请从 X+1 开始发"。这是 SSE 协议内置的可靠性机制，不需要额外编码。

Agent 场景的重要性：Agent 执行中的每个节点完成、工具调用结果都是关键事件。如果前端在 diagnose 节点完成后断线，重连后应该从 remediation 开始显示。OpsPilot 局限：EventBus 当前使用 asyncio.Queue，重连后丢失历史。要实现 Last-Event-ID 恢复需要在 incident_run_events 表存 sequence 序号，SSE 端点接收 Last-Event-ID 从数据库拉取后续事件。

15. 前端断开 SSE 后，后端 Agent 是否应该停止执行？

答：不停止。Agent 任务生命周期和客户端连接生命周期应该解耦。客户端连接可能因网络闪断、浏览器刷新、用户关闭窗口而断开。Agent 任务应该继续执行到完成，状态持久化到数据库。用户重新打开页面时应该能看到当前进度。

OpsPilot 做法：图中的执行在 _run_graph_bg 的后台线程中，完全不依赖 SSE 连接。即使所有 SSE 客户端断开，graph.astream() 继续执行，检查点、事件和证据照常持久化。

16. 如何区分"客户端连接生命周期"和"Agent 任务生命周期"？

答：解耦设计：任务生命周期（PENDING → RUNNING → SUCCEEDED/FAILED）由 POST /runs 启动，返回 run_id，不依赖长连接。连接生命周期（连接 → 接收事件 → 断开）仅用于实时推送。任务层完全在后台执行，使用持久化存储（检查点、事件表）。展示层提供 GET /runs/{run_id} 查看最新状态，不依赖实时流。

OpsPilot 完全遵循：POST /runs → 立即返回 run_id → BackgroundTasks 执行 → 状态写入 DB → SSE 或 GET /events 查看进度。

17. ALB、Nginx、Ingress 对 SSE 有哪些超时和缓冲配置风险？

答：三大风险。Nginx 缓冲整个响应后才发给客户端（proxy_buffering off; 必须关闭）、空闲连接超时断开（proxy_read_timeout 建议 600s+）。AWS ALB 空闲超时默认 60s（建议 600s），且 ALB 不支持关闭缓冲，不是最佳选择。K8s Ingress-Nginx 需通过 Annotation 配置 nginx.ingress.kubernetes.io/proxy-buffering: "off"。核心原则：任何中间代理都不能缓冲 SSE 响应，所有代理的超时时间必须大于 Agent 最大执行时间。

18. 为什么 Nginx 代理 SSE 时通常需要关闭响应缓冲？

答：Nginx 默认 proxy_buffering on，它会将后端响应收完整后再一次性发给客户端。SSE 的每个事件通常很小（几百字节），如果 LLM 响应慢，第一个 Token 可能几十秒后才到。Nginx 在收到完整 buffer 前不会推送，前端看到的是长时间无响应然后一次性收到所有事件，失去了流式的意义。proxy_buffering off 让 Nginx 收到数据立即转发。

OpsPilot 注意：uvicorn --reload 开发模式没有 Nginx，上生产时必须在 Nginx location 块中显式关闭缓冲。

19. Agent 流式输出如何做心跳，避免中间网络设备关闭连接？

答：定期发送特殊事件（如 type: "heartbeat"）让中间网络设备知道连接还活着。Nginx proxy_read_timeout 默认 60 秒，AWS ALB idle_timeout 默认 60 秒，60 秒内无数据传输连接会被关闭。最佳实践：服务端每 15-30 秒发送一次心跳事件；使用 SSE 的 :comment 行（冒号开头的注释行）作为轻量级心跳，浏览器自动忽略；心跳不增加事件序列号，不干扰业务逻辑。

OpsPilot 现状：EventBus 和 SSE 端点没有实现心跳。如果节点执行时间超过 60 秒（如 evidence_fanout 同时查询多个慢工具），SSE 连接可能被中间代理断开。

20. 如何实现流式事件的顺序性和去重？

答：事件结构包含递增 sequence 序号（如 run_id + sequence + event_id）。顺序性：生产端由事件持久化层（数据库自增 ID 或序列）保证严格递增，消费者按 sequence 排序渲染，即使收到乱序也先缓存后排好。去重：消费者维护 last_sequence，忽略 sequence ≤ last_sequence 的事件；重连时传 last_sequence 给服务器，服务端只推送 sequence > last_sequence 的事件。

推荐事件结构：
```json
{
  "run_id": "run_001",
  "sequence": 27,
  "event_id": "evt_027",
  "type": "tool.completed",
  "payload": {}
}
```

OpsPilot 实现：incident_run_events 表有自增主键 id 和 sequence 列，EventBus 发布时分配 sequence。增量查询 list_incremental() 使用 id > last_event_id 过滤。

⸻

三、任务队列与 Worker 调度

21. 为什么 Agent API 和 Agent Worker 应该解耦？

22. 不使用消息队列时，如何用 PostgreSQL 实现任务队列？

23. FOR UPDATE SKIP LOCKED 是如何避免多个 Worker 领取同一个任务的？

24. PostgreSQL 任务队列在高并发下有什么问题？

重点：

- 频繁轮询
- 索引膨胀
- 热点更新
- VACUUM 压力
- 吞吐受数据库限制

25. 什么时候应该从数据库任务队列迁移到 RocketMQ、Kafka 或 RabbitMQ？

26. Agent Worker 应该采用 Pull 模型还是 Push 模型？

27. Worker 执行任务期间崩溃，任务如何重新被领取？

可设计：

RUNNING

- lease_expires_at
- heartbeat_at

28. 什么是任务租约 Lease？为什么比简单的 RUNNING 状态可靠？

29. 如何防止执行时间较长的任务被其他 Worker 错误抢占？

30. 如何实现 Worker 优雅退出，避免部署时中断正在执行的 Agent？

⸻

四、消息可靠性与事件驱动

31. 消息队列为什么通常只能保证 At-least-once？

32. At-most-once、At-least-once、Exactly-once 分别是什么意思？

33. Agent 系统真的需要 Exactly-once 吗？

正确思路通常是：

MQ 至少一次投递 + 消费端幂等。

34. 如何设计消息幂等？

35. 消息消费成功，但数据库提交失败，会出现什么问题？

36. 数据库提交成功，但消息发送失败，如何处理？

37. 什么是 Transactional Outbox Pattern？

典型链路：

业务事务
├── 更新 agent_run
└── 写入 outbox_event
后台 Publisher
→ 读取 outbox_event
→ 发送 MQ
→ 标记已发送

38. Outbox 表如何避免重复发送消息？

39. 什么是 Inbox Pattern？它解决什么问题？

40. 如何设计死信队列、重试队列和人工补偿流程？

⸻

五、状态机与持久化

41. Agent State 和数据库业务数据有什么区别？

42. Agent 状态应该保存完整对象，还是保存事件和增量？

43. JSONB 保存工作流状态有什么优缺点？

44. 状态拆列存储和整块 JSON 存储如何选择？

45. 如何避免两个节点同时更新同一份 Agent State 发生 Lost Update？

46. 乐观锁如何用于 Agent 状态更新？

例如：

UPDATE agent_runs
SET state = :new_state,
version = version + 1
WHERE id = :id
AND version = :old_version;

47. 悲观锁适合什么 Agent 场景？

48. 什么是状态机的非法状态转换？如何在代码层阻止？

例如：

PENDING → RUNNING
RUNNING → SUCCEEDED / FAILED / WAITING
SUCCEEDED 不能重新回到 RUNNING

49. 如何保证节点输出落库与工作流状态转换是原子的？

50. 工作流定义升级后，旧任务的状态 Schema 如何兼容？

⸻

六、事务、一致性与补偿

51. Agent 调用外部工具时，为什么无法依靠本地数据库事务保证一致性？

52. 什么是分布式事务？为什么一般不建议 Agent 工具链使用强分布式事务？

53. Saga 模式如何用于 Agent 工具执行？

例如：

创建分支
→ 修改代码
→ 创建 MR
→ 触发部署

失败时：

关闭 MR
→ 删除分支
→ 回滚部署

54. 什么是补偿操作？补偿一定能完全回滚吗？

55. 外部 API 已执行成功，但客户端超时，如何判断是否需要重试？

56. 如何为外部工具设计业务幂等键？

57. 创建工单、发送邮件、执行部署这三种操作，幂等策略有什么差异？

58. 如何处理"部分成功"的 Agent 任务？

59. 最终一致性在 Agent 系统中通常表现在哪些地方？

60. 如何设计后台对账任务，发现状态与外部系统不一致？

⸻

七、数据库设计与性能

61. 一个 Agent 系统最核心的数据库表有哪些？

建议：

agent_runs
agent_node_runs
tool_calls
messages
artifacts
evidence
workflow_definitions
workflow_versions
outbox_events
human_tasks

62. agent_runs 和 agent_node_runs 为什么应该拆表？

63. 工具调用参数和返回结果应该全部存数据库吗？

64. 大型工具响应应该如何存储？

正确方向：

数据库存元数据
OSS 存原始结果
数据库保存 URI、Hash、大小、类型

65. 消息表会快速增长，如何做归档和分区？

66. PostgreSQL 按时间分区适合哪些 Agent 表？

67. 如何为任务查询设计索引？

例如：

(status, priority, created_at)
(tenant_id, status, created_at)
(run_id, sequence)

68. 为什么索引太多会降低 Agent 事件写入性能？

69. Agent 消息和 Trace 是否应该使用同一个数据库？

70. 如何估算数据库容量？

需要考虑：

日任务数
× 每任务节点数
× 每节点工具调用数
× 单条日志大小
× 保存天数

⸻

八、Redis、缓存与分布式锁

71. Agent 系统中 Redis 适合存什么，不适合存什么？

适合：

- 限流
- 短期缓存
- 心跳
- 临时状态
- 分布式锁

不适合：

- 唯一事实状态
- 长期审计记录

72. 如何缓存模型响应？哪些请求不应该缓存？

73. 工具查询结果缓存如何确定 TTL？

74. 如何避免缓存穿透、缓存击穿和缓存雪崩？

75. Agent 上下文缓存如何处理知识版本变化？

76. Redis 分布式锁有什么常见错误？

77. 为什么 SETNX + EXPIRE 分开执行不安全？

78. 如何安全释放分布式锁？

重点：只能由锁持有者删除。

79. Redlock 是否适合高风险 Agent 操作？

80. 分布式锁和数据库唯一约束如何选择？

通常：

能用数据库唯一约束解决的，不优先使用分布式锁。

⸻

九、模型网关与 LLM 调用工程

81. 为什么生产 Agent 不应该在业务代码中直接调用各模型 SDK？

82. Model Gateway 应该承担哪些职责？

- 协议统一
- 模型路由
- 超时
- 重试
- 限流
- 熔断
- Token 统计
- 成本控制
- 降级

83. 模型调用超时应该如何设置？

需要区分：

- 连接超时
- 首 Token 超时
- 总请求超时
- 流式空闲超时

84. 模型请求失败可以无脑重试吗？

85. 流式输出已经返回部分 Token 后，模型连接中断，如何处理？

86. 如何设计模型降级策略？

例如：

主模型超时
→ 同级备用模型
→ 小模型降级
→ 返回部分结果
→ 人工接管

87. 如何避免模型重试导致同一个工具被执行两次？

88. Prompt、模型、温度、工具定义应该如何版本化？

89. 如何统计单次 Agent 任务的完整模型成本？

90. 如何限制 Agent Loop 次数和 Token 消耗？

⸻

十、工具沙箱与执行安全

91. 为什么执行代码、Shell 和 Playwright 的 Worker 不应与 Agent API 混部？

92. 如何隔离不可信代码执行？

可讨论：

- Docker
- Kubernetes Job
- gVisor
- Firecracker
- 用户命名空间
- Seccomp
- Read-only FS

93. 容器逃逸风险如何降低？

94. 如何限制 Agent 执行容器的 CPU、内存、PID 和磁盘？

95. Playwright Worker 为什么容易出现内存泄漏？

96. 浏览器任务完成后，如何保证 Context、Page、Browser 进程都被释放？

97. 如何避免 Agent 读取宿主机敏感文件？

98. 工具执行产生的临时文件如何清理？

99. 如何限制工具只能访问指定内网域名和 API？

100.  Agent 执行高风险操作时，技术上如何实现 Dry-run、审批和审计？

⸻

后端面试官真正会连续追问的技术链

链路一：长任务与可靠执行

为什么异步
→ 为什么需要 Worker
→ Worker 挂了怎么办
→ 如何判断任务是否死亡
→ 如何重新领取
→ 重复执行怎么办
→ 如何幂等
→ 外部操作不能幂等怎么办
→ 如何补偿

链路二：工作流状态

状态存哪里
→ 为什么不存内存
→ 多 Worker 如何并发更新
→ 如何防止 Lost Update
→ 乐观锁怎么做
→ 更新冲突怎么办
→ 状态与事件如何保持一致
→ 是否使用 Outbox

链路三：模型调用

模型为什么要网关
→ 超时怎么设置
→ 能不能重试
→ 流式中断怎么办
→ 模型重试后工具会不会重复执行
→ 工具如何幂等
→ Token 如何控制
→ 如何降级

链路四：Playwright 自动化测试

测试任务在哪里运行
→ 为什么不能跑在 API 容器
→ 如何并发
→ 浏览器资源如何释放
→ 测试数据如何隔离
→ 截图 Trace 存哪里
→ Worker 崩溃如何恢复
→ 同一用例是否允许重试
→ Flaky 如何识别

你需要重点掌握的技术核心

对于你的背景，建议重点准备这 25 个：

2 FastAPI 异步执行模型
7 Uvicorn 多 Worker
9 长连接容量估算
13 SSE 与断线恢复
17 Nginx/ALB 流式配置
23 SKIP LOCKED
27 Worker 崩溃恢复
28 Task Lease
31 消息至少一次
34 消费幂等
37 Transactional Outbox
43 JSONB 状态设计
46 乐观锁
49 状态与产物原子提交
53 Saga 补偿
55 外部 API 超时后的不确定状态
64 大型产物存储
67 任务表索引
76 分布式锁
83 模型超时
85 流式中断
87 模型重试与工具重复执行
92 工具沙箱
95 Playwright 内存管理
100 Dry-run 和审批

这一版考察的就不是"你知道 Agent 有哪些模块"，而是：

你能不能真正实现一个不会重复执行、不会丢状态、服务崩溃后能恢复、并发下数据不乱、外部工具可控、上线后能稳定运行的 Agent 后端。
