# Round 1 · A 组母题标准答案

> 每题结构：**Kernel → Layer 1/2/3 展开 → 项目印证 → 素材**
> 目标每题 90 秒，能接追问。

---

## A1：FastAPI async 底层

**Kernel**：asyncio Event Loop 调度协程，遇 await 让出 CPU，I/O 完恢复 → 单线程并发上万。

**展开**：

### Layer 1 — 为什么 / 背景

Python 传统同步框架（Flask/Django）每请求独占一线程，1000 并发 = 1000 线程 → 内存爆、上下文切换开销大。FastAPI 基于 ASGI + asyncio，用一个 Event Loop 单线程调度成千上万协程，每个协程在 I/O 等待时主动让出控制权，不阻塞其他请求。适合 I/O 密集型场景——绝大多数 Web/API 调用都是等网络、等 DB、等 LLM，不是烧 CPU。

### Layer 2 — 怎么做 / 机制

Uvicorn 启动时创建 asyncio Event Loop → 监听端口，每个 HTTP 请求被包装为 `asyncio.Task` → 路由到对应的 `async def` 协程 → 协程执行到 `await`（如 `await llm.acomplete()`）时挂起，Event Loop 去调度其他 Task → I/O 完成后 OS 通知 Event Loop，恢复协程继续执行。关键约束：**单线程**——所有协程跑在同一条 OS 线程里，靠「主动让出 + 回调恢复」而非抢占式调度实现并发。

### Layer 3 — 坑 / 边界 / 追问预判

- **同步 DB 驱动会阻塞整个 Loop**：`psycopg2`/`pymysql` 是同步的，执行 `cursor.execute()` 会卡住整个线程，所有协程停滞。解法：`loop.run_in_executor(None, sync_func)` 把同步调用扔进线程池（ThreadPoolExecutor），不阻塞主 Loop。
- **async 不是并发银弹**：CPU 密集型任务（如图像处理、大 JSON 解析）会占着 CPU 不让出，此时应该用 `ProcessPoolExecutor`。
- **混合模式**：OpsPilot 用了 `asyncio.run()` 在后台线程里跑独立的 Event Loop 包裹同步的 `complete_sync()`——这是「异步框架包裹同步执行」的工程折中，不是最佳实践但兼容已有代码。
- **Nginx 反向代理 SSE 需关缓冲**：`proxy_buffering off`，否则流式响应被 Nginx 攒着延迟推送，SSE 实时性丢失。

**项目印证**：
- OpsPilot：FastAPI async def 做路由入口，LLM 调用走 `complete_sync()` 跑在后台线程独立 Event Loop 里（`asyncio.run()` 隔离），是异步框架包裹同步执行的混合模式。`backend/app/main.py` FastAPI 实例通过 Uvicorn 启动。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A1

---

## A2：SSE 断了任务停吗

**Kernel**：不停。连接生命周期 ≠ 任务生命周期，断开只关推流通道，重连靠 Last-Event-ID 补发。

**展开**：

### Layer 1 — 为什么 / 背景

SSE（Server-Sent Events）是单向推送协议：服务端推、浏览器收。如果 SSE 连接断开 = Agent 任务停了，那用户关浏览器就会毁掉正在执行的故障修复——这在生产运维里是不可接受的。所以任务执行必须与连接存活解耦：Agent 在后台线程/进程执行，状态落入 DB，SSE 只是「观察窗口」而非「控制链路」。

### Layer 2 — 怎么做 / 机制

1. Agent 任务放到 `BackgroundTasks`（FastAPI）或独立 Worker 进程执行，与 SSE 连接的 HTTP 请求生命周期完全独立。
2. 每个节点执行后，状态落入 `incident_checkpoints` 表（`state_json` 全量 + `sequence` 序号），事件落入 `incident_run_events` 表。
3. 前端 `EventSource` 断开时，浏览器**原生**记录最后收到的 `id:` 值（即 event sequence），重连时自动在请求头带上 `Last-Event-ID: N`。
4. 服务端读请求头 `Last-Event-ID`，查 DB `SELECT * FROM events WHERE run_id = ? AND sequence > ?`，补发断线期间遗漏的事件，然后继续推新鲜事件。
5. Nginx 反向代理需 `proxy_buffering off` + `proxy_read_timeout 600`。

### Layer 3 — 坑 / 边界 / 追问预判

- **asyncio.Queue 做 EventBus 不行**：Queue 是纯内存，事件推完即消失，无历史可查。重连时服务端不知道你上次到哪，也无法补发。生产必须事件落 DB + Redis Pub/Sub 跨实例推送。
- **Last-Event-ID 是浏览器原生行为**：`EventSource` 自动处理，前端一行代码不用写。但前提是服务端推事件时**必须带 `id:` 字段**，否则浏览器无 id 可记。
- **OpsPilot 现状**：当前 EventBus 用 asyncio.Queue，重连会丢历史。断线续传方案已验证但未落地——是已知的待补项。

**项目印证**：
- OpsPilot：`graph_runner.py` 的事件循环用 asyncio.Queue 推 SSE，`backend/app/api/incidents.py` 的 SSE 路由负责推送。事件通过 `builder.py:25` 的 `_wrap_with_events` 在每节点前后发 `NODE_STARTED`/`NODE_FAILED` 事件。已知待补：DB sequence + Redis Pub/Sub 断线续传。

> 📎 素材：`battle-plan/实战-2026-06-10-SSE断线续传机制.md`，`battle-plan/题库/高危题标准答案.md` — A2

---

## A3：Worker 崩溃恢复

**Kernel**：Task Lease。RUNNING 任务有 `lease_expires_at`，Worker 每 10s 续租；崩溃不续租 → watchdog 扫过期 Lease 重置 PENDING。

**展开**：

### Layer 1 — 为什么 / 背景

在分布式任务调度里，Worker 执行中可能因 OOM、Pod 驱逐、机器宕机而意外终止。如果任务永远卡在 RUNNING 状态，就成了僵尸任务——没人执行、也没人敢接手。单纯的 RUNNING/PENDING 状态字段不够：RUNNING 状态永远不会自动过期，无法判断 Worker 是还在跑还是已经死了。

### Layer 2 — 怎么做 / 机制

引入「租约（Lease）」概念，给 RUNNING 加时间戳维度的生命信号：

```
任务表关键字段：
  status: PENDING | RUNNING | COMPLETED | FAILED
  lease_expires_at: TIMESTAMP   -- RUNNING 时 = now() + 30s
  heartbeat_at: TIMESTAMP       -- 最后一次心跳时间
  worker_id: TEXT               -- 谁在跑

Worker 正常执行时每 10s 续租：
  UPDATE tasks SET lease_expires_at = now() + 30s, heartbeat_at = now()
  WHERE id = :id AND worker_id = :worker

独立 watchdog 定时任务（每 5s）：
  SELECT * FROM tasks
  WHERE status = 'RUNNING' AND lease_expires_at < now()
  → UPDATE tasks SET status = 'PENDING', worker_id = NULL
  → 其他空闲 Worker 领走
```

### Layer 3 — 坑 / 边界 / 追问预判

- **重复执行问题**：新 Worker 领到 PENDING 任务后，要从 checkpoint 恢复而**不是从头重跑**。LangGraph 的 `graph.invoke(None, thread_id)` 会从最新 checkpoint 续跑，跳过已完成节点。
- **工具调用幂等兜底**：即使从 checkpoint 续跑，最后一步工具调用可能已发出但结果未落盘。所以工具调用必须带幂等键——重复提交同一动作，已完成的直接返回缓存结果。
- **Lease 时间的平衡**：太短 → 正常 Worker 网络抖动被误判死亡；太长 → 真崩溃后恢复太慢。30s 是常见平衡点。
- **OpsPilot 现状**：当前用 `BackgroundTasks` 直跑，没有 Lease。生产化必须引入任务队列 + Lease + 持久化 checkpointer。

**项目印证**：
- OpsPilot：当前 `backend/app/services/graph_runner.py` 用 `BackgroundTasks` 直接同步跑图，没有任务队列、没有 Lease。生产化路线：`FOR UPDATE SKIP LOCKED` 抢任务 + `lease_expires_at` 续租 + watchdog 恢复 + 自建 `IncidentCheckpoint` 续跑。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A3

---

## A4：并发改 State / Lost Update

**Kernel**：乐观锁——`UPDATE SET version=version+1 WHERE id=:id AND version=:old`，影响行数 0 即冲突 → 退避重试。

**展开**：

### Layer 1 — 为什么 / 背景

两个 Worker 同时读 `run.state` → 各自修改 → 各自写回。后写的覆盖先写的，先写的修改丢失——这就是 Lost Update。在 Agent 场景：两路证据并行采集后先后写回 State，后写者可能覆盖先写者的证据列表。传统方案要么串行化（损失并行性），要么加锁（损失吞吐）。

### Layer 2 — 怎么做 / 机制

**乐观锁（optimistic locking）**——假设冲突概率低，不加锁，更新时检查版本是否被改过：

```sql
-- 读取时带 version
SELECT state, version FROM agent_runs WHERE id = :id   -- version = 5

-- 更新时 version 作为条件（CAS 语义）
UPDATE agent_runs
SET state = :new_state, version = version + 1
WHERE id = :id AND version = 5;

-- 影响行数 = 0 → 被其他进程抢先更新了，冲突
-- 影响行数 = 1 → 更新成功
```

冲突后策略：指数退避重试（等 50ms → 100ms → 200ms）或直接报错让上游决定。

### Layer 3 — 坑 / 边界 / 追问预判

- **框架层的 BSP 屏障**：LangGraph 底层是 Pregel/BSP 模型。同一 super-step 内并行的节点读的是**冻结的同一份快照**，各自的写暂存为 `pending_writes`，step 末尾统一 `_apply_writes`。如果两个节点在同一 step 写同一个 LastValue channel，框架直接抛 `InvalidUpdateError`——你根本不会遇到「后写着覆盖先写着」的框架层 bug。
- **OpsPilot 的实际情况**：拓扑基本是线性的——每个 super-step 只有一个活跃节点，不存在两个 Pregel 节点同时写同一 channel。真正并行（`evidence_fanout` 里的 `asyncio.gather`）发生在**单个节点内部**，对 Pregel 不可见，也不会触发 channel 写冲突。
- **跨进程才需要乐观锁**：只有多 Worker 共享同一份持久化 state（如 RedisSaver / PostgresSaver）时，才需要在 DB 层加乐观锁。
- **高冲突场景用悲观锁**：冲突概率高、冲突代价大时（如审批决策、关键状态转换），用 `SELECT FOR UPDATE` 直接锁行，宁等锁不重试。

**项目印证**：
- OpsPilot：`IncidentAgentState` 47 个字段全是 LastValue（无 reducer），但拓扑为线性编排，不存在跨节点并发写冲突。自建 checkpoint 表 `incident_checkpoints` 中 state 按 `run_id + node_name` 定位，每个节点写自己的快照——天然隔离。

> 📎 素材：`battle-plan/langgraph底层-三层映射与Pregel.md` §4，`battle-plan/题库/高危题标准答案.md` — A4

---

## A5：工具调用何时能重试

**Kernel**：幂等才能重试。`idem_key=sha256(run_id+tool+input)`，重试命中同键返缓存。超时/429/500 可重试；400、已吐流式 token、不可逆操作必须带幂等键。

**展开**：

### Layer 1 — 为什么 / 背景

Agent 调用外部工具时，网络超时、限流、服务端 500 都可能导致调用失败。但「重试」不是无脑再来一遍——如果第一次调用实际上已经执行了（只是响应丢了），重试会**重复执行**，可能造成：同一个部署被执行两次、同一封告警邮件发出两次、同一个 K8s scale 操作叠加两次。所以「能不能重试」的核心标准是：**该操作是否幂等**——相同参数重复执行，结果一致且无额外副作用。

### Layer 2 — 怎么做 / 机制

**幂等键设计**：

```python
import hashlib, json

def make_idempotency_key(run_id: str, tool_name: str, input_params: dict) -> str:
    raw = f"{run_id}|{tool_name}|{json.dumps(input_params, sort_keys=True)}"
    return hashlib.sha256(raw.encode()).hexdigest()
```

服务端收到调用时：
1. 检查 `idempotency_key` 是否已存在 → 若存在且状态为 `COMPLETED`/`EXECUTING`，**直接返回已有结果**，不重复执行
2. 若不存在 → 执行，完毕后将 `(key, status, result)` 写入缓存/DB
3. 设置 TTL（如 24h），过期后自动清理

**可重试**：网络超时（不确定是否执行）、429 限流（指数退避）、500 服务端错误

**不可重试**：400 参数错误（重试没意义）、已返回部分流式 Token 的 LLM 请求（幂等性已破坏，token 已部分流出）

### Layer 3 — 坑 / 边界 / 追问预判

- **幂等键 ≠ 去重**：幂等键保证「同参数同结果」，但不保证「不同参数不同结果」。如果 input 包含时间戳等非确定性字段，两个「逻辑相同」的调用会生成不同幂等键 → 去重失效。所以 input 要**规范化：排序 key、去除时间戳等噪音字段**。
- **非幂等 API 的兜底**：如果外部 API 本身不支持幂等键语义（大多数 SaaS API 不支持），Server 端最多做到「查重跳过」。真正的原子性要靠业务层补偿（见 A10 Saga）。
- **OpsPilot 的 ControlledExecutor**：用 `call_id` 做幂等键，同一 call_id 的重复调用直接 skip + 返回缓存结果。`backend/app/services/executor.py:64-85`。

**项目印证**：
- OpsPilot：`ControlledExecutor`（`executor.py:62`）用 `call_id` 做幂等键查重——同一 `call_id` 只执行一次，重复调用返回 `action_cached`。前置条件校验（`_check_preconditions`）在执行前检查 `service_exists`/`deployment_healthy`，不满足直接拒绝。审计日志（`executor.py:120`）记录每次调用及其幂等命中情况。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A5，`battle-plan/实战-2026-06-15-Harness控制面vs写路径治理.md` §写路径治理

---

## A6：LangGraph checkpoint

**Kernel**：分两层答！通用：`thread_id` 主键，`CheckpointTuple={channel_values/channel_versions/versions_seen/pending_writes}`。⚠️ 但 OpsPilot 用 0.0.55 是自建，`checkpointer=None`，逐节点落 `IncidentCheckpoint` 表。

**展开**：

### Layer 1 — 通用机制（教科书答案）

LangGraph 原生 checkpoint 以 `thread_id` 为主键，每完成一个 super-step 自动保存一份 `CheckpointTuple`：

| 字段 | 含义 |
|------|------|
| `channel_values` | 全量 State 快照——每个 channel（对应 State 的一个字段）的当前值 |
| `channel_versions` | 各 channel 的版本号向量——用于判断哪些 channel 有更新、哪些节点该被唤醒 |
| `versions_seen` | 每个节点已消费到的 channel 版本——防重复执行（一个版本不会触发同一节点两次） |
| `pending_writes` | 当前 step 累积的、尚未 apply 的写入（step 间屏障统一 apply） |

底层是 Pregel/BSP 模型（`langgraph/pregel/__init__.py:1117-1121` 有注释原话）：step N 的 channel 更新只有 step N+1 可见；step 期间 channel 不可变；更新只在 step 过渡时统一写入——checkpoint 就是每个 step 结束时的 channel 快照。

原生 saver：`InMemorySaver`（开发）、`SqliteSaver`/`PostgresSaver`（生产）、`RedisSaver`（多 Worker 共享）。

现代 HITL 用 `interrupt()` 暂停 + `Command(resume=...)` 恢复——LangGraph 自动从最新 checkpoint 续跑。

### Layer 2 — ⚠️ OpsPilot 的真实实现（致命陷阱，必须说！）

**OpsPilot 用的是 LangGraph 0.0.55，版本太早，所有现代 API 都不存在**：

| 能力 | 0.0.55 | 现代版 |
|------|:---:|:---:|
| `checkpointer=...` → 自动 checkpoint | ❌ 只有 MemorySaver/SQLite | ✅ PostgresSaver/RedisSaver |
| `interrupt()`/`Command(resume=…)` | ❌ import 报错 | ✅ |
| `Send()` API 扇出 | ❌ | ✅ |

所以 OpsPilot**三套都自建了**：

1. **Checkpoint 持久化**：`builder.py` 编译时 `checkpointer=None`（`graph_runner.py:211`），`GraphRunner` 在 `astream` 循环里每节点完后手动 `_save_checkpoint(run_id, node_name, state)` 落到自建 `IncidentCheckpoint` 表（`run_id + node_name + state_json`）。
2. **HITL 中断续跑**：`approval_interrupt` 节点 → END（图执行结束），人工审批后 `approval_runtime` 从自建 checkpoint 读回 state、设 `_resume_from_node`，重新 `astream` → `node_dispatcher`（入口透传节点 + 条件边）按白名单路由到续跑入口。
3. **并行扇出**：节点内 `asyncio.gather`（非 `Send` API）。

### Layer 3 — 为什么自建，不是重复造轮子

那版压根没有对应的轮子。而且自建带来了原生框架给不了的好处：
- 可跟 `runs`/`events`/`evidence` 等业务表 join
- 前端运行详情页直接查 checkpoint 历史（框架内部格式对业务不可见）
- 支持**可控的多入口续跑**（批准→executor、改方案→risk_gate、补证据→evidence_fanout），原生 `interrupt_before` 给不了这种显式多入口路由

**诚实边界**：自建代价 = 重复了框架后来提供的能力、自己管序列化/反序列化、没有原生 time-travel/分支调试。

**项目印证**：
- OpsPilot：`backend/app/graph/builder.py:177-218` 定义 `node_dispatcher` + `_route_dispatcher` + 白名单；`graph_runner.py:252-262` 逐节点手动落 checkpoint；`approval_runtime.py:78-166` resume 状态准备 + 入口映射。自建 checkpoint 表在 `db_models.py:59`。

> 📎 素材：`battle-plan/dispatcher-resume机制.md`（全篇），`battle-plan/langgraph底层-三层映射与Pregel.md` §2-3，`battle-plan/题库/高危题标准答案.md` — A6

---

## A7：Pydantic 反序列化变 dict

**Kernel**：checkpoint 存 JSON，回来 Pydantic 变 dict → `x.f if hasattr(x,'f') else x.get('f','default')`；遍历 list 先防 None。

**展开**：

### Layer 1 — 为什么 / 背景

LangGraph 的 checkpoint 机制（无论原生还是自建）存储的都是 JSON——Pydantic 对象序列化成 dict 存入，反序列化后就是 dict，**不会再变回 Pydantic 对象**。如果代码里用 `.attribute` 访问，dict 没有这个属性 → `AttributeError`。

这在 LangGraph 里是特别容易踩的坑：图正常执行时 state 里是 Pydantic 对象（`.service` 工作），checkpoint 恢复后变成 dict（`.service` 报错），同一份代码对「首跑」和「续跑」行为不一致。

### Layer 2 — 怎么做 / 机制

**防御式属性访问**：

```python
# 错误写法
service = ticket.service  # ticket 是 dict 时抛 AttributeError

# 正确写法
if hasattr(ticket, 'service'):
    service = ticket.service
else:
    service = ticket.get('service', 'unknown')

# 简写一行的变体
service = ticket.service if hasattr(ticket, 'service') else ticket.get('service', 'unknown')
```

**遍历 list 必须先防 None**：

```python
for action in actions:
    if action is None:
        continue
    if isinstance(action, dict):
        action_type = action.get("action_type")
        risk_level = action.get("risk_level", "UNKNOWN")
    else:
        action_type = action.action_type
        risk_level = action.risk_level
```

### Layer 3 — 坑 / 边界 / 追问预判

- **`isinstance` 检查不是银弹**：Pydantic v2 的 model 也是 dict 的 subclass（在 behavior 上），直接 `isinstance(obj, dict)` 在 v1 能区分、v2 会混淆。更稳健的做法是检查 `__class__.__name__` 或 `hasattr` 方法。
- **OpsPilot 的解决方案**：在 `AGENTS.md` 标注为「已知陷阱 #1」，所有节点代码（`nodes/__init__.py`）里访问 `ticket`/`actions` 时都用兼容写法。
- **如果有条件引入 Pydantic v2 的 `model_validate`**：可以从 dict 显式重建 model 对象再访问——`Ticket(**ticket)` 或 `Ticket.model_validate(ticket)`——但要注意如果 dict 缺少必填字段会直接崩，不如防御式兼容写法安全。

**项目印证**：
- OpsPilot：`AGENTS.md` 明确标注「已知陷阱 #1：Pydantic 对象 vs dict 二义性」并给出正确写法模板。`nodes/__init__.py` 中所有节点访问 state 字段时都遵循 `hasattr + .get` 兼容范式。自建 checkpoint（存 `state_json` 到 `IncidentCheckpoint` 表）同样走 JSON 序列化路径，反序列化后全是 dict。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A7，AGENTS.md §已知陷阱#1

---

## A8：K8s Pod 重启状态恢复

**Kernel**：状态外置到 DB。内存态全丢 → 生产换 RedisSaver + Redis Pub/Sub；Worker 启动扫过期 Lease 重领，`graph.invoke(None, thread_id)` 从 checkpoint 续跑。

**展开**：

### Layer 1 — 为什么 / 背景

K8s Pod 随时可能因 OOM、节点故障、滚动更新被杀死重启。Pod 内的所有内存状态——包括 `InMemorySaver` 的 checkpoint、`asyncio.Queue` 的事件队列、正在运行的协程——**全部丢失**。Agent 任务不能因此就没了——一个正在执行故障修复的 Agent，Pod 重启后必须能从断点继续，而不是从头再来。

### Layer 2 — 怎么做 / 机制

**状态外置三件套**：

1. **Checkpointer 换持久化存储**：
   - 开发/单机：`InMemorySaver`（快但重启丢）
   - 生产多 Worker：`RedisSaver`（`langgraph-checkpoint-redis`）+ Redis 做主存储
   - 替代方案：`PostgresSaver`（与业务 DB 同库，但 checkpoint 读写量大，别互相拖慢）

2. **EventBus 换 Pub/Sub**：
   - `asyncio.Queue` 纯内存 → 重启丢、多实例不共享
   - 生产：事件写 DB（持久化）+ Redis Pub/Sub（跨实例实时推送）

3. **Watchdog 自动恢复**：
   - Worker 启动时扫描 DB：`SELECT * FROM runs WHERE status='RUNNING' AND lease_expires_at < now()`
   - 重置为 PENDING → 领走恢复执行
   - 恢复方式：`graph.invoke(None, config={"configurable": {"thread_id": run_id}})` → LangGraph 从最新持久化 checkpoint 续跑

### Layer 3 — 坑 / 边界 / 追问预判

- **OpsPilot 现状 = 开发态，生产不可直接部署**：当前 `checkpointer=None`（自建 checkpoint 但存 SQLite）+ InMemory EventBus + BackgroundTasks 直跑。Pod 重启后所有进行中 run 卡在 RUNNING，既无法恢复也不会失败。这是**已知的生产化 gap**。
- **RedisSaver 是关键基础设施**：LangGraph 0.0.55 没有 RedisSaver（只有 MemorySaver/SqliteSaver），版本升级后 `install langgraph-checkpoint-redis` 即可。
- **checkpoint 恢复 ≠ 无副作用**：即使状态恢复了，已发出的网络调用可能不可逆。需要幂等键兜底（A5）。
- **自建 checkpoint 也能恢复**：虽然没用原生 checkpointer，但自建 `IncidentCheckpoint` 表里有全量 `state_json`——生产环境下从该表读最新快照 + `_resume_from_node` 路由同样可续跑。

**项目印证**：
- OpsPilot：当前用自建 `IncidentCheckpoint` 表落 state_json（`graph_runner.py:252-262`），await 未来版本升级后换 RedisSaver + Redis Pub/Sub + watchdog 任务恢复，架构迁移路径清楚。`approval_runtime.py` 已实现「读 checkpoint → 反序列化 → 设 _resume_from_node → 重新 invoke」的续跑链路。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A8，`battle-plan/dispatcher-resume机制.md` §4

---

## A9：1000 并发 Agent 架构

**Kernel**：API 与 Worker 解耦：POST 写 tasks 表（PENDING）秒回；Worker 池 `FOR UPDATE SKIP LOCKED` 抢任务；单 Worker `Semaphore(20)` 限并发 LLM；RedisSaver 共享 checkpoint；Redis Pub/Sub 跨实例推 SSE。

**展开**：

### Layer 1 — 为什么 / 背景

OpsPilot 当前架构是「API 收到请求 → BackgroundTasks 直接跑图」。1000 个请求同时进来 → 1000 个线程/协程同时跑图 → 内存炸、LLM API 被限流（你的 API Key 每秒几百 token 上限）、数据库连接池耗尽。本质问题是：**接入层（API）和计算层（Worker）耦合在一起**，一个请求的生命周期从 HTTP 入口到图执行结束全程绑定。

### Layer 2 — 怎么做 / 机制

目标架构——接入与计算解耦：

```
POST /incidents/runs  →  INSERT INTO tasks (PENDING)  →  立即返回 run_id (200ms)
                                    ↓
┌──────── 任务队列（PostgreSQL SKIP LOCKED）────────┐
│  Worker-1          Worker-2          Worker-N     │
│  Semaphore(20)     Semaphore(20)     Semaphore(20)│
│       ↓                 ↓                 ↓       │
│  LangGraph + RedisSaver（多 Worker 共享 checkpoint）│
│       ↓                 ↓                 ↓       │
│  工具调用（幂等键 + gateway 统一收口）               │
└───────────────────────────────────────────────────┘
                                    ↓
Redis Pub/Sub → API 推 SSE 到各前端
```

**关键组件**：

1. **任务队列**：`FOR UPDATE SKIP LOCKED` 让多 Worker 并发取任务不冲突——每个 Worker `SELECT ... LIMIT 1 FOR UPDATE SKIP LOCKED` 领走一条 PENDING 任务（原子操作），不同 Worker 领不同的任务。
2. **并发控制**：Worker 内部 `asyncio.Semaphore(20)` 限制单实例并发 LLM 调用数——20 个 Agent 同时跑，更多排队。全局并发 = Worker 数 × 20。
3. **共享状态**：`RedisSaver` 替代 InMemorySaver/自建 checkpoint——所有 Worker 实例共享同一份 langgraph checkpoint 存储。
4. **跨实例 SSE**：事件落 DB（持久化）+ Redis Pub/Sub（实时跨实例推送）→ 前端连任意 API 实例都能收到实时事件，不为 Worker 实例位置所限。
5. **独立扩缩容**：API 实例数按 HTTP 吞吐扩；Worker 实例数按 Agent 并发量扩——解耦后各自独立。

### Layer 3 — 坑 / 边界 / 追问预判

- **SKIP LOCKED 不是 FIFO**：PG 的 `FOR UPDATE SKIP LOCKED` 不保证先入先出——它跳过已锁行后拿到下一条可见行。如果需要严格 FIFO，用 Redis List（`BLPOP`）或 RocketMQ。
- **Semaphore 只能限单 Worker**：全局并发 = Worker 数 × 20，如果 Worker 池动态扩缩，全局并发上限是浮动的。需要加全局令牌桶（Redis 计数器）做全局限流。
- **OpsPilot 当前差距**：BackgroundTasks 直跑、InMemory EventBus、无任务队列、无 Semaphore。是 MVP 架构，非生产架构。但架构路线清楚，每个组件插入点明确。

**项目印证**：
- OpsPilot 当前 MVP：`api/incidents.py:193` 创建 run → `graph_runner.py` 执行。生产化路线：PG SKIP LOCKED 任务队列 + `asyncio.Semaphore` 限流 + RedisSaver 升级 + Redis Pub/Sub 跨实例推送。架构迁移对业务逻辑零侵入（节点代码不动，只换 infra 层）。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A9

---

## A10：Saga 补偿一致性

**Kernel**：每步配正向+补偿，失败按反向补偿。业务级尽力而为，非精确回滚，补偿也要幂等。不用 2PC：外部 API 不支持、性能差。

**展开**：

### Layer 1 — 为什么 / 背景

Agent 调用外部工具是一组连锁操作：查 K8s → 判定需要回滚 → 创建回滚分支 → 触发回滚部署 → 验证恢复。中间任何一步都可能失败（网络超时、权限不足、资源不存在），但前几步可能已经产生了真实副作用（Git 分支已创建、部署已触发）。如果没有补偿机制，系统会处在「半吊子」状态——部分操作生效、部分未生效、无人知道该往哪边靠。

### Layer 2 — 怎么做 / 机制

**Saga 模式**——把长事务拆成一串短事务，每步定义一个正向操作和一个补偿操作：

```
正向链：
  步骤1: 创建 Git 回滚分支 → 步骤2: 触发回滚部署 → 步骤3: 通知告警群

补偿链（反向执行）：
  步骤3: 发「回滚已取消」通知 → 步骤2: 重新部署原版本 → 步骤1: 删除回滚分支
```

任意步骤失败时，**按反向顺序依次执行已完成步骤的补偿操作**，把系统恢复到「近似原状」。

**补偿的几个关键性质**：

- **业务级尽力而为**：不是技术级精确回滚。数据库可以 ROLLBACK 到事务起点，但外部 API 没有这个能力——「发送邮件」无法真正撤回，只能再发一封「取消通知」。
- **补偿本身也要幂等**：补偿可能执行多次（网络超时重试），所以 `delete_branch(branch_name)` 必须支持「分支已不存在 = 成功」，不能因为不存在就报错终止。
- **补偿可能也失败**：如果补偿失败了怎么办？记录到「待人工处理」队列，由运维人员手动介入。

### Layer 3 — 坑 / 边界 / 追问预判

- **为什么不用 2PC / XA 分布式事务？** ① 外部 API（K8s API、Git API、告警 API）都不支持两阶段提交协议；② 2PC 的性能极差——协调者阻塞等待所有参与者响应，参与者也持锁等待；③ Agent 工具调用链天然不适合强事务——有些操作（如发告警）本身就是不可逆的，不存在「prepare 阶段」。
- **Saga 和幂等键的关系**（A5 的延伸）：Saga 的每个正向步带幂等键，确保重试不重复执行同一个操作；补偿步也带幂等键，确保补偿不重复执行。
- **OpsPilot 的实现层级**：remediation 节点出修复方案时，每个 `ActionSpec` 包含 `rollback_plan` 字段（回滚步骤）；executor 的 `ControlledExecutor` 执行前做 dry-run 验证；verify 节点失败时触发回滚序列。不是完整的 Saga 编排引擎，但关键路径上已嵌入补偿思维。

**项目印证**：
- OpsPilot：`ActionSpec.rollback_plan` 字段为每个动作预留回滚步骤（`models/action.py`）；`ControlledExecutor`（`executor.py:62`）用 `call_id` 做幂等键防重复；`verify` 节点（`nodes/__init__.py:1596`）验证失败 → 路由回 executor 重试 / FATAL → 触发回滚 → rca 记录全过程的审计链。remediation 当前只出单方案（无多方案择优），但回滚路径已嵌入。

> 📎 素材：`battle-plan/题库/高危题标准答案.md` — A10，`battle-plan/实战-2026-06-15-Harness控制面vs写路径治理.md` §写路径治理
