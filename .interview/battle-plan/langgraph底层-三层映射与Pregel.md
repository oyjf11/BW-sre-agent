# OpsPilot — 代码到 LangGraph 的三层映射 & Pregel 引擎原理

> 配套：`作战计划-agent开发.md` Q24/35/42/45。姊妹篇：[条件路由机制.md](./条件路由机制.md) / [dispatcher-resume机制.md](./dispatcher-resume机制.md)。
> **全部基于实测 `langgraph==0.0.55` 源码**，行号可对照 venv 内源文件。
> 一句话内核：**你写的 StateGraph 只是「声明」，compile() 把它编译成一张 Pregel 图；真正跑的是 Pregel 的 BSP（Bulk Synchronous Parallel）引擎——节点是 actor，State 字段是 channel，执行按 super-step 一波一波推进。**

---

## 0. 为什么要懂这层（面试价值）

很多人只会说"LangGraph 是个图编排框架"。能讲到**"它底层是 Pregel/BSP 模型，StateGraph 编译成 channel + actor"** 就直接拉开差距。而且这层知识能**统一解释**好几道高危题：并发写 State 会怎样（Q35）、checkpoint 的 channel_values 是什么（Q24）、条件边本质是什么、为什么你的 fanout 不会撞 State。

源码铁证（`langgraph/pregel/__init__.py:1117-1121` 原文注释）：
```
# Similarly to Bulk Synchronous Parallel / Pregel model
# computation proceeds in steps, while there are channel updates
# channel updates from step N are only visible in step N+1,
# channels are guaranteed to be immutable for the duration of the step,
# channel updates being applied only at the transition between steps
```

---

## 1. 三层映射总览

```
┌─ 第 1 层：你写的声明式 API（builder.py / state.py）────────────┐
│  IncidentAgentState(TypedDict)  +  add_node ×14               │
│  add_edge / add_conditional_edges / set_entry_point          │
│  → graph.compile(checkpointer=None)                          │
└──────────────────────────┬───────────────────────────────────┘
                           │ compile() 编译
┌─ 第 2 层：Pregel 拓扑（channels + PregelNode）─────────────────┐
│  47 个 State 字段 → 47 个 LastValue channel                   │
│  14 个节点 → 14 个 PregelNode(triggers=订阅, writers=写回)      │
│  静态边 → channel 触发订阅                                      │
│  条件边 → branch:* channel + 路由函数                          │
│  多入边汇聚 → NamedBarrierValue(等齐才触发)                     │
│  START → EphemeralValue                                       │
└──────────────────────────┬───────────────────────────────────┘
                           │ astream() 驱动
┌─ 第 3 层：Pregel/BSP 运行时（super-step 循环）─────────────────┐
│  for step in range(recursion_limit+1):                       │
│    1. _prepare_next_tasks: 找出被 channel 更新触发的节点        │
│    2. 没有任务 → 结束                                          │
│    3. _should_interrupt 检查中断点                            │
│    4. 并行执行本波所有节点 (asyncio.create_task + wait)         │
│    5. 汇总 pending_writes                                     │
│    6. _apply_writes: 写回 channel（step 之间的"屏障"）          │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 第 1 层 → 第 2 层：你的代码被编译成了什么

### 2.1 State 字段 → Channel（默认 LastValue）

`graph/state.py:436-463` 的 `_get_channels()`：遍历 TypedDict 每个字段建一个 channel。

- **默认 → `LastValue`**（`state.py:463`）：通道里只存"最后一次写入的值"，**一个 super-step 内只允许被写一次**，否则报错（`channels/last_value.py:47-51`）：
  ```python
  def update(self, values):
      if len(values) != 1:
          raise InvalidUpdateError("LastValue can only receive one value per step.")
  ```
- **若字段是 `Annotated[T, reducer]` → `BinaryOperatorAggregate`**：用 reducer（如 `operator.add`）**累加合并**多个写入，允许一步内多写（这就是 `add_messages` 的原理）。

> **你项目的关键事实**：`IncidentAgentState` 的 **47 个字段全是普通 TypedDict 字段，没有一个用 Annotated reducer** → **全部是 LastValue channel**。这个事实直接决定了下面 Q35 的答案。

所以 LangGraph 原生 checkpoint 里的 **`channel_values` 就是"每个 channel 当前值"的快照** = 你这 47 个字段的当前值。这正是 Q24 要的答案。

### 2.2 节点 → PregelNode

`graph/state.py:316` 每个 `add_node` 编译成一个 `PregelNode`，带两个核心属性：
- **triggers / channels（订阅）**：这个节点"读哪些 channel"、"被哪些 channel 的更新唤醒"。
- **writers（写回）**：节点返回的 dict 会被写回对应 channel。

你的节点函数 `def diagnose_node(state) -> state`：入参是从订阅 channel 读出的快照、返回值被拆成对各 channel 的写。**节点之间不直接传参，全靠 channel 间接通信**——这是 Pregel "actor 通过消息通信" 的本质。

### 2.3 边 → channel 订阅关系

| 你写的 | 编译成 |
|--------|--------|
| `add_edge("A","B")` | B 订阅 A 完成后写的触发 channel |
| `add_conditional_edges("A", fn, {...})` | 建 `branch:*` channel；A 跑完先调 `fn(state)` 决定写哪个分支 channel，从而触发对应下游（`state.py` branch 逻辑） |
| 多条边指向同一节点（fan-in） | `NamedBarrierValue`（`state.py:367`）：**等所有上游都到齐**才触发，实现汇聚同步 |
| `set_entry_point` | 入口节点订阅 `START`（`EphemeralValue`，`state.py:242`） |

> 所以[条件路由机制.md](./条件路由机制.md)里那 5 处 `add_conditional_edges`，在 Pregel 层都是"路由函数写一个 branch channel → 触发对应下游节点"。条件路由 = **动态决定下一步往哪个 channel 写**。

---

## 3. 第 3 层：Pregel / BSP 引擎怎么跑（super-step）

`pregel/__init__.py:1123-1192` 的主循环，就是 BSP 三段式，每个 super-step：

```
┌─────────────── 一个 super-step ───────────────┐
│ ① Plan:  _prepare_next_tasks                  │
│    扫描 channel 版本,找出"输入 channel 被更新"   │
│    的节点 = 本波要跑的 tasks                     │
│    （没有 tasks → 整图结束 break）               │
│                                               │
│ ② Execute: 并行跑本波所有 task                  │
│    futures = [create_task(node) for task]     │
│    await asyncio.wait(FIRST_EXCEPTION,         │
│                       timeout=step_timeout)   │
│    ★ 本波内 channel 不可变(immutable),          │
│      各 task 读到的是同一份冻结快照              │
│                                               │
│ ③ Apply:  _apply_writes(checkpoint, channels, │
│           所有 task 的 pending_writes)         │
│    ★ 写入只在 step 之间的"屏障"统一生效          │
│      → step N 的写,step N+1 才可见              │
└───────────────────────────────────────────────┘
   循环上限 = recursion_limit + 1（你传的 50）
```

**三条 BSP 铁律（源码注释原话，面试可背）**：
1. **step N 的 channel 更新，只有 step N+1 能看到**（更新不在波内即时可见）。
2. **一个 step 期间 channel 不可变**（所有并行节点读同一份冻结快照）。
3. **更新只在 step 之间的过渡（屏障）统一 apply**（先收集所有 writes，再一次性写回）。

**checkpoint 的本质**：每个 super-step 结束后那份 `channels` 快照 = 一个 checkpoint。`thread_id` 标识一条执行线，每个 step 一个版本，所以 LangGraph 原生支持 time-travel/断点续跑。
> ⚠️ 但你项目**没用**这套原生 checkpoint（compile 时 `checkpointer=None`），是 GraphRunner 在 `astream` 外层每个节点后手动落自建表——见 [dispatcher-resume机制.md](./dispatcher-resume机制.md)。

---

## 4. 这套原理统一解释了你的几道高危题

### Q35：两个节点并发更新同一份 State 会发生什么？乐观锁怎么做？

**两层答**：
> 「**框架层**：LangGraph 是 BSP 模型,同一个 super-step 内并行的节点读的是**冻结的同一份快照**,各自的写先暂存为 pending_writes,step 末尾才统一 apply。如果两个并行节点在同一步写**同一个 LastValue channel**,`LastValue.update` 会直接抛 `InvalidUpdateError: can only receive one value per step`——框架强制你要么用 `Annotated[..., reducer]` 声明合并语义(变成 BinaryOperatorAggregate),要么保证一步只有一个写者。
>
> **我项目层**:`IncidentAgentState` 47 个字段全是 LastValue(无 reducer),但我的拓扑基本是**线性的、每个 super-step 只有一个活跃节点**,不存在两个 Pregel 节点同步写同一 channel,所以不会触发这个冲突。真正的并发(evidence_fanout 并发查多个工具)是**在单个节点内部用 asyncio.gather** 做的,对 Pregel 不可见——所以也绕过了 channel 写冲突。
>
> **如果上多 Worker 跨进程**:那是另一层问题,DB 级别用乐观锁 `UPDATE ... WHERE version=:old`,影响行数 0 即冲突重试。」

> 💡 这个答案的杀手锏:把"框架层 BSP 屏障""我项目用 gather 绕过""跨进程 DB 乐观锁"三层分清,显示你真懂边界。

### Q24/45：checkpoint 的 channel_values 是什么？

> 「channel_values 就是 Pregel 里每个 channel 的当前值快照。State 的每个字段编译成一个 channel(默认 LastValue),channel_values 就是这些字段的当前值集合;channel_versions 记录各 channel 被更新到第几版,versions_seen 记录每个节点已消费到的版本——用来在下个 super-step 判断哪些节点该被重新触发。」（再接：但我项目用的是自建 checkpoint,见 dispatcher 篇）

### Q42：LangGraph 和 LangChain 的区别？

> 「LangChain 是 LLM 应用的组件库(Runnable/LCEL,本质是 DAG 链)。LangGraph 把编排换成了 **Pregel/BSP 的有状态图模型**——支持**环、条件分支、并行、断点续跑**,这些是 DAG 链做不到的。我项目里 critic 退回 evidence_fanout 的回边、verify 重试环,就是 LangGraph 相对 LangChain 的核心增量。」

---

## 5. 一张图记住三层

| 你的代码（声明） | Pregel 拓扑（编译产物） | BSP 运行时（执行） |
|------------------|------------------------|--------------------|
| `IncidentAgentState` 字段 | LastValue channel ×47 | step 末尾 `_apply_writes` 写回 |
| `add_node(fn)` ×14 | PregelNode(triggers, writers) | 被 channel 更新触发,并行执行 |
| `add_edge` | channel 订阅 | `_prepare_next_tasks` 据此选下一波 |
| `add_conditional_edges` | branch:* channel + 路由函数 | 路由函数写哪个 branch 决定下游 |
| fan-in 多入边 | NamedBarrierValue | 等齐才触发 |
| `set_entry_point` | 订阅 START(EphemeralValue) | 第一个 super-step 的种子 |
| `compile(checkpointer)` | CompiledStateGraph→Pregel | 每 step 一个 checkpoint 快照 |

---

## 6. 源码速查（venv/langgraph 0.0.55）

| 概念 | 文件:行 |
|------|--------|
| BSP/Pregel 模型注释（原话） | `pregel/__init__.py:1117-1121` |
| super-step 主循环 | `pregel/__init__.py:1123-1192` |
| `_prepare_next_tasks`（选下一波） | `pregel/__init__.py:1513+` |
| `_apply_writes`（屏障写回） | `pregel/__init__.py:1476+` |
| StateGraph→PregelNode 编译 | `graph/state.py:316-329` |
| State 字段→channel | `graph/state.py:436-463`（默认 LastValue:463） |
| LastValue 一步一写约束 | `channels/last_value.py:47-51` |
| 多入边 barrier | `graph/state.py:367` |
| START EphemeralValue | `graph/state.py:242` |
