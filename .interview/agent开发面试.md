# Agent 后端开发面试 100 题（问答版）

> 面试风格：一语中的，直击要害。

---

## 一、Agent Runtime 与并发模型

**Q1. Agent 服务为什么用异步框架？**
LLM 调用和工具调用都是 I/O 等待，异步能让单进程复用等待时间；它不能解决 CPU 密集型任务（解析、沙箱执行要扔线程/进程池）。

**Q2. FastAPI async def 底层如何执行？**
Uvicorn 启动一个 Event Loop（asyncio），每个 async def 是 coroutine，遇到 await 时让出 CPU，I/O 完成后由 loop 恢复执行；本质是单线程协作式并发。

**Q3. 异步接口调用同步驱动会发生什么？**
阻塞 Event Loop，所有并发请求都卡住；应用 `loop.run_in_executor` 把同步调用扔进线程池。

**Q4. GIL 对 Agent 服务有什么影响？**
I/O 密集型场景 GIL 基本无影响（等待时自动释放）；CPU 密集型任务（文档解析、代码扫描）需用多进程而非多线程绕过 GIL。

**Q5. LLM 请求是哪种类型？**
I/O 密集型——进程等待网络响应，CPU 空闲，异步框架完全够用。

**Q6. Playwright/文档解析/代码扫描放哪里？**
- Playwright → 独立进程池或独立 Worker 服务（内存隔离）
- 文档解析 → 线程池（I/O + 少量 CPU）
- 代码扫描 → 进程池（CPU 密集）

**Q7. Uvicorn 多 Worker 和单 Worker 异步并发的区别？**
单 Worker = 一个进程，Event Loop 内并发；多 Worker = 多个独立进程，每个有自己的 Loop，进程间不共享内存，由 OS 负载均衡。

**Q8. 多 Worker 模式下为什么不能把 Agent 状态存进程内存？**
不同请求可能落在不同进程，进程重启状态丢失；必须持久化到数据库或 Redis。

**Q9. 单实例能承载多少个模型流式请求？如何估算？**
`最大并发数 ≈ min(网络带宽 / 单流平均带宽, 模型服务限流 / 实例数)`；经验值：单实例并发 20-100，超出需限流（Semaphore）。

**Q10. 如何限制同时运行的 Agent 数量？**
用 `asyncio.Semaphore` 控制并发槽位；超限请求入队列或返回 429，避免模型侧被打爆。

---

## 二、HTTP、SSE 与长连接

**Q11. 长任务为什么不适合普通 HTTP 请求？**
普通 HTTP 请求超时通常 30-60s，Agent 任务分钟级；客户端会超时断连，服务端不知道是否继续。

**Q12. SSE vs WebSocket 如何选？**
Agent 输出是单向流（服务端推，客户端收）→ SSE 够用，更简单；双向实时（用户随时打断/注入）→ WebSocket。

**Q13. SSE 底层协议？浏览器断线如何恢复？**
SSE = 普通 HTTP 长连接，`Content-Type: text/event-stream`；浏览器断线后自动用 `Last-Event-ID` 重连，服务端从该 ID 之后重放未消费事件。

**Q14. Last-Event-ID 有什么用？**
断线重连时告诉服务端"我最后收到了哪条事件"，服务端从该位置续传，避免数据丢失或重复。

**Q15. 前端断开 SSE 后，后端 Agent 该停吗？**
连接生命周期 ≠ 任务生命周期；前端断开只关闭推流，Agent 继续执行；重连后可从 Last-Event-ID 续接。除非前端明确发取消请求，否则不中断。

**Q16. 客户端连接生命周期 vs Agent 任务生命周期？**
连接 = 网络管道（随时断）；任务 = 业务状态（持久化，独立于连接存在）。

**Q17. ALB/Nginx/Ingress 对 SSE 的配置风险？**
Nginx 默认缓冲响应体，SSE 要关缓冲：`proxy_buffering off`；ALB 有空闲超时（默认 60s），要设心跳；Ingress 注解 `nginx.ingress.kubernetes.io/proxy-read-timeout` 要调大。

**Q18. Nginx 代理 SSE 为什么要关响应缓冲？**
Nginx 默认积攒足够数据再转发，SSE 事件会被憋住不发；关掉缓冲才能逐行实时透传。

**Q19. 如何做心跳避免连接超时？**
每隔 15-30s 发一条 `: keepalive\n\n` 注释事件，中间网络设备和代理看到数据流动就不会关连接。

**Q20. 如何保证流式事件顺序性和去重？**
每个事件带 `sequence` 单调递增序号 + `event_id`；客户端按 sequence 排序，根据 event_id 幂等去重：

```json
{
  "run_id": "run_001",
  "sequence": 27,
  "event_id": "evt_027",
  "type": "tool.completed",
  "payload": {}
}
```

---

## 三、任务队列与 Worker 调度

**Q21. Agent API 和 Worker 为什么要解耦？**
API 只负责接单并返回 run_id，避免 HTTP 连接超时；Worker 异步拉取执行，各自独立伸缩，不互相阻塞。

**Q22. 不用 MQ 如何用 PostgreSQL 实现任务队列？**
```sql
SELECT * FROM tasks WHERE status = 'PENDING'
ORDER BY priority, created_at
FOR UPDATE SKIP LOCKED LIMIT 1;
```
拿到后更新 `status = 'RUNNING'` + `lease_expires_at`。

**Q23. FOR UPDATE SKIP LOCKED 如何避免多 Worker 抢同一任务？**
SKIP LOCKED = 跳过已被其他事务锁定的行，不同 Worker 并发拿到的是不同行，无冲突。

**Q24. PostgreSQL 任务队列高并发有什么问题？**
频繁轮询 + 热点行更新 → 索引膨胀、VACUUM 压力大、写入吞吐受限；高吞吐场景应迁到专业 MQ。

**Q25. 什么时候从 DB 队列迁到 MQ？**
单机 TPS > 几百、需要跨语言消费、需要 Topic/分区路由、或需 DLQ/重试语义时迁到 RocketMQ/Kafka。

**Q26. Worker 用 Pull 还是 Push？**
Pull（Worker 主动拉取）：更好背压控制，Worker 自己决定消费速率，Agent 场景首选。

**Q27. Worker 执行中崩溃，任务如何被重新领取？**
每个 RUNNING 任务有 `lease_expires_at`；后台 watchdog 定期扫描 `lease_expires_at < now()` 的任务，重置为 PENDING。

**Q28. Task Lease 为什么比单纯 RUNNING 状态可靠？**
RUNNING 状态永远不会自动过期；Lease 有时间戳，Worker 崩溃后超时自动"死亡"，watchdog 可安全重新分配。

**Q29. 如何防止长任务被错误抢占？**
Worker 每隔 N 秒续租（`UPDATE lease_expires_at = now() + interval`）；只要心跳正常，其他 Worker 就不会抢。

**Q30. Worker 优雅退出如何实现？**
捕获 SIGTERM，停止领取新任务，等待当前任务完成（或设最大等待时间），任务完成后正常退出；K8s 配 `terminationGracePeriodSeconds`。

---

## 四、消息可靠性与事件驱动

**Q31. MQ 为什么通常只保证 At-least-once？**
消费者处理完但 ACK 前崩溃，Broker 超时重投；要 Exactly-once 需分布式事务代价极高，大多数 MQ 放弃这一保证。

**Q32. 三种语义是什么？**
- At-most-once：发一次，失败丢弃，可能丢消息
- At-least-once：失败重投，可能重复
- Exactly-once：不丢不重，代价最高（分布式事务或 Kafka 事务 API）

**Q33. Agent 系统真的需要 Exactly-once 吗？**
不需要——MQ At-least-once + 消费端幂等 = 实际效果等同 Exactly-once，代价低得多。

**Q34. 如何设计消息幂等？**
消息携带业务唯一键（`idempotency_key`），消费前查 DB 是否已处理，处理完记录；重复消息直接跳过。

**Q35. 消费成功但 DB 提交失败？**
操作重复执行，需要消费端幂等；或改用 DB 事务 + 消费 offset 在同一事务提交（仅限支持的 MQ）。

**Q36. DB 提交成功但消息发送失败？**
下游收不到事件；用 Transactional Outbox Pattern 解决。

**Q37. Transactional Outbox Pattern 是什么？**
业务数据变更和 outbox 事件在同一 DB 事务写入；独立 Publisher 轮询 outbox 表发送 MQ 并标记 sent；保证"写 DB 必发消息"：

```
业务事务
├── 更新 agent_run
└── 写入 outbox_event

后台 Publisher
→ 读取 outbox_event
→ 发送 MQ
→ 标记已发送
```

**Q38. Outbox 如何避免重复发送？**
Publisher 用幂等键（`outbox_id`）发送，MQ 消费端幂等处理；或 Publisher 原子性地 SELECT-UPDATE-SEND，`sent = true` 后不再处理。

**Q39. Inbox Pattern 解决什么？**
防止消费端重复处理：消费消息时先把 `message_id` 写 inbox 表（唯一约束），写成功才执行业务逻辑；重复消息在 inbox 插入时唯一约束冲突，直接跳过。

**Q40. 死信队列/重试队列/人工补偿怎么设计？**
重试 N 次失败 → 进 DLQ → 人工或自动化补偿脚本处理 → 标记 compensated 或 abandoned；关键是有审计轨迹。

---

## 五、状态机与持久化

**Q41. Agent State 和业务数据有什么区别？**
Agent State = 工作流执行的中间过程（当前节点、context、临时产物）；业务数据 = 最终结果（诊断结论、修复方案）；前者可重建，后者需永久存储。

**Q42. 保存完整对象还是事件/增量？**
关键节点保存完整快照（易恢复）+ append 事件日志（易追溯）；纯事件溯源重建成本高，纯快照无变更历史。

**Q43. JSONB 保存工作流状态的优缺点？**
优：灵活，schema 随时改，嵌套结构方便；缺：无法对 JSON 内字段建高效索引，大对象读写慢，难做字段级迁移。

**Q44. 状态拆列存储 vs 整块 JSON 如何选？**
频繁查询/过滤的字段拆列（如 `status`、`priority`）；大型动态结构存 JSONB；关键查询字段绝不放 JSON 里。

**Q45. 如何避免 Lost Update？**
乐观锁（version 字段）或悲观锁（SELECT FOR UPDATE）；两个节点并发更新时只有一个能成功提交。

**Q46. 乐观锁怎么用？**
```sql
UPDATE agent_runs
SET state = :new_state, version = version + 1
WHERE id = :id AND version = :old_version;
```
影响行数为 0 → 冲突，重试或报错。

**Q47. 悲观锁适合什么场景？**
并发冲突概率高、冲突代价大（如审批决策、状态关键转换），宁可等锁不愿重试。

**Q48. 如何阻止非法状态转换？**
在代码层定义合法转换表：`ALLOWED_TRANSITIONS = {RUNNING: {SUCCEEDED, FAILED, WAITING}}`；转换前校验，不在表内直接抛异常：

```
PENDING → RUNNING
RUNNING → SUCCEEDED / FAILED / WAITING
SUCCEEDED 不能重新回到 RUNNING
```

**Q49. 如何保证节点输出落库与状态转换原子性？**
在同一数据库事务中写入节点产物和更新 `agent_run` 状态；两者要么都成功要么都回滚。

**Q50. 工作流定义升级后旧任务 Schema 如何兼容？**
版本化 `workflow_definition`（加 version 字段），旧任务绑定旧版本 schema；新字段加默认值，删字段用 Optional；用迁移脚本而非强制切换。

---

## 六、事务、一致性与补偿

**Q51. 调用外部工具为什么不能用本地 DB 事务保证一致性？**
本地事务只管 DB，外部 API 调用不在事务范围内；DB 回滚不会撤销已发出的 HTTP 请求。

**Q52. 为什么不建议 Agent 工具链用强分布式事务？**
2PC/XA 需要所有参与方支持且性能差；外部第三方 API 根本不支持；实际上用 Saga + 补偿即可。

**Q53. Saga 模式如何用于 Agent？**
每步操作定义正向动作和补偿动作；任何步骤失败时按反向顺序执行补偿；最终达到"全成功或全撤销"的业务一致性：

```
创建分支 → 修改代码 → 创建 MR → 触发部署

失败时：
关闭 MR → 删除分支 → 回滚部署
```

**Q54. 补偿一定能完全回滚吗？**
不一定——"发送邮件"无法真正撤回，只能发"取消通知"；补偿是业务级尽力而为，不是技术级精确回滚。

**Q55. 外部 API 超时后不确定是否执行，如何处理？**
用幂等键重试：若操作已执行则服务端返回已有结果；若未执行则正常执行；关键是接口必须支持幂等键。

**Q56. 如何为外部工具设计幂等键？**
`idempotency_key = sha256(run_id + tool_name + input_hash)`；同参数重试命中同一键，服务端返回缓存结果。

**Q57. 创建工单/发邮件/执行部署，幂等策略差异？**
- 创建工单：数据库唯一约束，重复请求返回已有工单
- 发邮件：记录 `sent_at`，同 key 只发一次
- 执行部署：查询当前状态，若目标版本已部署则跳过

**Q58. 如何处理"部分成功"的 Agent 任务？**
记录每步成功/失败状态，支持从失败点重试（幂等跳过已成功步骤）；向用户暴露部分结果，人工决定是否继续。

**Q59. 最终一致性在 Agent 系统哪些地方体现？**
Outbox 异步发送、工具调用结果异步写回、evidence 收集后异步聚合、状态同步到外部系统——这些都是最终一致性。

**Q60. 如何设计对账任务？**
定时任务扫描 RUNNING 状态超时的任务，与外部系统查询实际状态对比；差异项进入人工队列或自动修复。

---

## 七、数据库设计与性能

**Q61. Agent 系统最核心的表有哪些？**
```
agent_runs          工作流执行主记录
agent_node_runs     节点执行详情
tool_calls          工具调用记录
messages            消息历史
artifacts           产物元数据
evidence            证据条目
workflow_definitions 工作流定义
workflow_versions   版本快照
outbox_events       事务性发件箱
human_tasks         人工审批任务
```

**Q62. agent_runs 和 agent_node_runs 为什么拆表？**
一个 run 有几十个 node_run，混在一张表行数爆炸；分表后可独立分区、独立归档、按 run_id 聚合查询高效。

**Q63. 工具参数和返回结果全存 DB 吗？**
参数存（审计需要）；返回结果看大小——小的存，大的（几十 KB+）存 OSS，DB 只存元数据（URI、hash、size）。

**Q64. 大型工具响应如何存储？**
DB 存元数据（`s3_uri, content_hash, size_bytes, content_type`），原始内容存 OSS/S3；查询走 DB，内容按需从 OSS 拉取。

**Q65. 消息表快速增长如何处理？**
按时间分区（PostgreSQL range partition by `created_at`），老分区 detach 后归档到冷存储或直接 DROP。

**Q66. PostgreSQL 按时间分区适合哪些表？**
`messages, events, tool_calls, artifacts`——写多读少、按时间查询、需要定期清理的高频流水表。

**Q67. 任务查询如何设计索引？**
```sql
-- Worker 抢任务
CREATE INDEX ON tasks(status, priority, created_at) WHERE status = 'PENDING';
-- 租户查询
CREATE INDEX ON tasks(tenant_id, status, created_at);
-- 事件回放
CREATE INDEX ON events(run_id, sequence);
```

**Q68. 为什么索引太多降低写入性能？**
每次 INSERT/UPDATE 都要同步更新所有索引的 B-Tree；写入频繁的 Agent 事件表索引要精简。

**Q69. 消息和 Trace 应该用同一个 DB 吗？**
不建议——Trace/可观测性数据写入量巨大，用专用存储（ClickHouse/Jaeger）；业务 DB 只存业务状态，避免互相拖垮。

**Q70. 如何估算数据库容量？**
```
日任务数 × 节点数 × 工具调用数 × 单条大小(KB) × 保存天数 × 膨胀系数(1.3)
= 所需存储；加上 WAL、索引约 2-3x
```

---

## 八、Redis、缓存与分布式锁

**Q71. Redis 适合存什么，不适合存什么？**
适合：限流计数、短期缓存、心跳、分布式锁、临时状态；
不适合：唯一业务状态（重启丢失）、长期审计数据。

**Q72. 如何缓存模型响应？哪些不该缓存？**
对完全相同的 prompt + 参数缓存（semantic cache 用 embedding 相似度匹配）；带时间戳、随机 seed、用户个性化的请求不缓存。

**Q73. 工具查询缓存 TTL 怎么定？**
根据数据变更频率：指标数据 30-60s，配置数据 5-10min，静态元数据 1h+；写操作结果不缓存。

**Q74. 缓存穿透/击穿/雪崩如何避免？**
- 穿透：查不到的 key 缓存空值（short TTL）
- 击穿：热点 key 失效时用互斥锁重建缓存
- 雪崩：TTL 加随机抖动，避免同时失效

**Q75. Agent 上下文缓存如何处理知识版本变化？**
缓存 key 带上知识库版本号；版本升级时旧 key 自然失效或主动 invalidate。

**Q76. Redis 分布式锁常见错误？**
SETNX 和 EXPIRE 分两步执行（中间崩溃永久死锁）；用非拥有者释放锁；锁过期但业务未完成导致并发。

**Q77. 为什么 SETNX + EXPIRE 分开不安全？**
SETNX 成功但 EXPIRE 执行前进程崩溃，锁永远不释放；应用 `SET key value NX PX ttl` 原子命令。

**Q78. 如何安全释放分布式锁？**
用 Lua 脚本原子性校验 + 删除，只有锁持有者（value 匹配）才能删除：
```lua
if redis.call('get', key) == value then
    return redis.call('del', key)
end
```

**Q79. Redlock 适合高风险 Agent 操作吗？**
Redlock 存在争议（时钟漂移问题），高风险操作（扣款、部署）建议用 DB 唯一约束 + 乐观锁，比 Redlock 更可靠。

**Q80. 分布式锁 vs 数据库唯一约束如何选？**
能用 DB 唯一约束解决的优先用 DB（强一致、持久、事务支持）；跨服务协调、非 DB 资源或需要 TTL 自动释放时用分布式锁。

---

## 九、模型网关与 LLM 调用工程

**Q81. 为什么业务代码不能直接调各模型 SDK？**
各厂商 SDK 接口不同，切换成本高；超时/重试/限流/成本统计分散在各处；Model Gateway 统一管理，业务代码无感换模型。

**Q82. Model Gateway 应该承担哪些职责？**
协议统一、模型路由、连接超时/首 Token 超时/流式空闲超时、指数退避重试、限流熔断、Token 计量、成本控制、降级策略。

**Q83. 模型超时如何设置？**
四层分开设：
- 连接超时：5s
- 首 Token 超时：30s
- 总请求超时：5min
- 流式空闲超时：30s（防止模型"卡住不输出"）

**Q84. 模型失败可以无脑重试吗？**
不行——429 限流可重试（退避），500 可重试，400 参数错误不重试，已返回部分流式 Token 不重试（幂等性破坏）。

**Q85. 流式输出部分返回后连接中断如何处理？**
已有 Token 保存到 buffer；根据业务决策：若内容完整可用则保留，否则从 buffer 末尾续传（需模型支持 suffix 续写）或丢弃重来。

**Q86. 模型降级策略怎么设计？**
```
主模型超时
→ 同级备用模型
→ 小模型降级（降精度）
→ 返回部分结果 + 人工标记
→ 人工接管
```
每级降级都记录 metrics。

**Q87. 如何避免模型重试导致工具重复执行？**
模型层重试只重发 LLM 请求，不重发已执行的工具调用；工具调用结果缓存在 run state，重试时从缓存恢复而非重新执行。

**Q88. Prompt/模型/温度/工具定义如何版本化？**
每次运行记录完整配置快照（prompt 版本 hash、model id、temperature、tool schema hash），与 run_id 绑定；保证复现性。

**Q89. 如何统计单次 Agent 任务的完整模型成本？**
每次 LLM 调用记录 `(model, input_tokens, output_tokens, cache_hit)`；run 结束后 SUM 所有调用，按模型单价计算总费用。

**Q90. 如何限制 Agent Loop 次数和 Token 消耗？**
全局计数器：`max_iterations = 50, max_tokens = 100k`；每轮检查，超限时强制终止并返回 `status = LIMIT_EXCEEDED`。

---

## 十、工具沙箱与执行安全

**Q91. 代码执行 Worker 为什么不能与 Agent API 混部？**
不可信代码可以逃逸容器、耗尽资源、访问敏感环境变量；API 服务和沙箱 Worker 必须强隔离，不共享进程和文件系统。

**Q92. 如何隔离不可信代码执行？**
生产方案：Kubernetes Job + gVisor（syscall 拦截）+ read-only FS + seccomp profile + resource limits；高安全要求用 Firecracker microVM。

**Q93. 如何降低容器逃逸风险？**
不以 root 运行（UID 非 0），禁用特权模式，挂载 seccomp/AppArmor profile，只暴露必要 capability，网络策略限制出口。

**Q94. 如何限制执行容器的资源？**
K8s `resources.limits`：`cpu: 1, memory: 512Mi`；`pids_limit` 限制进程数；临时存储 `ephemeral-storage: 1Gi`；超限 OOM Kill 或 CPU 节流。

**Q95. Playwright Worker 为什么容易内存泄漏？**
每个 Page/Context 都持有大量 DOM、JS Heap、网络连接；未正确 close 时 Browser 进程持续累积，最终 OOM。

**Q96. 浏览器任务完成后如何确保资源释放？**
```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    try:
        context = await browser.new_context()
        page = await context.new_page()
        # ... do work ...
    finally:
        await context.close()
        await browser.close()
```
用 try/finally 或 context manager，确保异常时也关闭。

**Q97. 如何避免 Agent 读取宿主机敏感文件？**
挂载 read-only FS，不挂载宿主机目录；使用 user namespace（UID 映射），容器内 root = 宿主机普通用户；seccomp 禁止敏感 syscall。

**Q98. 工具执行产生的临时文件如何清理？**
任务完成或失败时删除 `/tmp/{run_id}/` 目录；容器 Job 模式下容器退出后卷自动销毁；设置 `emptyDir` 而非持久卷。

**Q99. 如何限制工具只能访问指定域名/API？**
K8s NetworkPolicy 限制 egress，只允许白名单 CIDR/域名；或在 Worker 设置 HTTP_PROXY 代理，代理层做域名白名单过滤。

**Q100. 高风险操作如何实现 Dry-run、审批和审计？**
- Dry-run：`execute(dry_run=True)` 返回"将要做什么"而不实际执行
- 审批：插入 `human_tasks` 表，触发审批中断（LangGraph interrupt），等待人工决策
- 审计：每次执行记录 `who, what, when, result`，不可删除，写入 append-only 审计表

---

## 面试高频追问链（速记）

| 追问链 | 一句话核心 |
|--------|-----------|
| 为什么异步 → Worker 挂了怎么办 | **Lease 超时 + watchdog 重分配** |
| 消息重复 → 幂等怎么做 | **业务唯一键 + 去重表** |
| 状态并发 → Lost Update | **乐观锁 version 字段** |
| 外部 API 超时 → 不知道有没有执行 | **幂等键重试，服务端返回缓存结果** |
| 模型流式中断 → 工具重复执行 | **工具结果缓存在 state，重试不重跑工具** |
| 分布式锁 → Redlock 可靠吗 | **高风险操作优先 DB 唯一约束** |

## 建议重点掌握的 25 题

| # | 题目 |
|---|------|
| 2 | FastAPI 异步执行模型 |
| 7 | Uvicorn 多 Worker |
| 9 | 长连接容量估算 |
| 13 | SSE 与断线恢复 |
| 17 | Nginx/ALB 流式配置 |
| 23 | SKIP LOCKED |
| 27 | Worker 崩溃恢复 |
| 28 | Task Lease |
| 31 | 消息至少一次 |
| 34 | 消费幂等 |
| 37 | Transactional Outbox |
| 43 | JSONB 状态设计 |
| 46 | 乐观锁 |
| 49 | 状态与产物原子提交 |
| 53 | Saga 补偿 |
| 55 | 外部 API 超时后的不确定状态 |
| 64 | 大型产物存储 |
| 67 | 任务表索引 |
| 76 | 分布式锁 |
| 83 | 模型超时 |
| 85 | 流式中断 |
| 87 | 模型重试与工具重复执行 |
| 92 | 工具沙箱 |
| 95 | Playwright 内存管理 |
| 100 | Dry-run 和审批 |
