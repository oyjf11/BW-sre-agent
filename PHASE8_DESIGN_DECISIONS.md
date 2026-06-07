# Phase 8 离线评测框架 — 设计决策与取舍

> 面试素材：记录 Phase 8 中几个真正有「方案选择」的地方，以及为什么这样设计。
> 覆盖 Graph Quality 评测框架（结构化根因 + fixture 注入 + 指标体系）。

---

## 1. 根因分类：封闭枚举 vs 自由文本

### 问题

diagnose 节点原来输出的 `hypothesis` 是自由文本（如"近期发布引入 NPE"）。要评测「AI 判断对了没有」，就必须比较模型输出和 expected label。

**自由文本的困境**：

- 关键词匹配（contains "deploy"）：brittle，换个说法就漏。
- LLM-as-judge 事后归类：把不确定性引入评判器本身，无法干净归因——指标变化到底是模型变了还是 judge 飘了？
- 两种方式都无法做到「可复现的稳定指标」。

### 方案选择

**方案 A（弃）**：事后用 LLM 把自由文本映射到类别。
- 引入第二个 LLM 调用，eval 波动来源变成两个，根本无法分离诊断质量和归类质量。

**方案 B（选）**：让 diagnose 节点在 prompt 里直接要求输出封闭枚举值，解析时校验合法性。
- 主指标变成纯 enum 等值比较：`actual[0].incident_type == expected.incident_type`。
- 完全确定、可复现，波动只剩真实 LLM 推理本身。

### 关键取舍

引入封闭枚举会限制表达力——「数据库主从切换失败」和「数据库慢查询锁等待」都落进 `database_failure`。但这是可接受的：枚举是「一级分类」，`hypothesis` 自由文本依然保留做人工抽查；评测主指标是分类准确率，不是文字质量。

### 防陷阱设计：`unknown` vs `other` 的区分

如果只有一个兜底值，模型会被迫在「证据不足」和「真的不在枚举里」两种情况里乱选，造成虚假准确率。
- `unknown`：证据不足，无法判断。
- `other`：模型已判定根因，但超出当前枚举体系。

这个区分让评测能准确识别「模型在保守回避」vs「模型在诚实报告超纲情况」。

---

## 2. Fixture 注入：ContextVar 作用域 vs 全局开关

### 问题

评测要「固定证据输入，让 LLM 推理成为唯一变量」。graph 的 evidence_fanout 节点会并发调用 15+ 个工具，这些调用都经过 ToolGateway。需要一种机制让这些调用在评测时返回固定数据，而不打扰生产路径。

### 备选方案对比

**方案 A：全局开关 `EVAL_MODE = True`**
- 不是并发安全的。多个 eval case 并发跑时，全局状态被所有协程共享，case 之间会互相污染 fixture。
- 不用，除非单线程串行跑，但这会让评测变慢。

**方案 B：monkeypatch gateway**
- 测试框架（pytest monkeypatch）作用在单个测试函数。但 eval runner 是应用层，不是 pytest 上下文。
- 如果手动 replace 函数，作用域不好控制，且污染 gateway 单例状态。

**方案 C（选）：ContextVar 作用域注入**
```python
_fixture_var: ContextVar[Optional[Dict]] = ContextVar("eval_fixtures", default=None)

with fixture_scope({"query_logs": {...}}):
    await executor.execute(case_id, state)
```
- ContextVar 在 Python asyncio 里会随 Task 自动继承：`fixture_scope` 内 spawn 的所有子协程（包括 asyncio.gather 并发的工具调用）都能看到同一份 fixture。
- scope 退出后自动 reset（利用 token），无论是否有异常。
- 不同 case 的并发运行在各自 Task 上下文里，互不干扰。

### 为什么这符合项目已有模式

项目里已经用了两处相同机制：
- `graph/context.py`：ContextVar 把 event hook 从 GraphRunner 注入到节点 wrapper，节点函数不需要额外参数。
- `tracing.py`：ContextVar 传递 run_id / span_id，跨异步调用保持追踪上下文。

ContextVar 是项目「跨异步上下文透明传递状态」的标准工具，再加一个 `eval_fixtures` 是 zero-surprise 的扩展。

### Gateway 短路点的选择

短路插入在 `call_tool` 的开头，在 mock/real adapter 判断**之前**。

这很重要：CI 测试用 `autouse conftest` 强制 `TOOL_ADAPTER_MODE=mock`，如果短路插在 mock 判断之后，fixture 和 mock adapter 就会发生顺序依赖。插在之前，两者完全正交——eval fixture 覆盖一切，生产/单测路径不受影响。

---

## 3. 两层评测分层：Graph Quality vs Runtime Fidelity

### 问题的本质

一个 SRE agent 系统有两类正确性，它们是完全不同的问题：

1. **诊断质量**：LLM 推理出的根因准不准？（和具体代码/基础设施无关）
2. **运行保真**：生产链路（事件、checkpoint、DB 持久化、审批 resume）跑对了没有？

如果合并成一个综合指标，任何一类问题都会掩盖另一类：诊断质量高不代表 checkpoint 序列化没有丢字段；反之 runtime 运转正常不代表 LLM 在判断根因。

### 两层设计

| | Layer 1: Graph Quality | Layer 2: Runtime Fidelity |
|---|---|---|
| 跑什么 | `graph.ainvoke()` | 完整 `GraphRunner.run()` |
| 副作用 | 无 DB / 无事件 | 写 DB / 写事件 / 写 checkpoint |
| 数据集规模 | 全量 10-12 case | 代表性子集 2-3 case |
| 本期深度 | 做扎实 | 搭骨架 |

**两层指标永不合并成一个综合数字**。

Layer 2 的核心问题是：当 approval_interrupt 触发后，`GraphRunner` 的 `astream` 返回了 `WAITING_HUMAN`，approval_runtime 重建 state 后从 `node_risk_gate` 续跑，最终 Layer 1 和 Layer 2 的终态是否一致？—— 这是 compare 模式 diff 的意义。

### compare 模式的价值

`--mode compare` 对同一个 case 同时跑 DirectGraphExecutor 和 RunnerGraphExecutor，diff 终态的 `incident_type` / `status`。这会暴露：
- GraphRunner 的 checkpoint/serde 序列化是否丢字段（如新增的 `incident_type` 字段反序列化失败）
- approval resume 路径是否改变了诊断语义

---

## 4. Fixture 粒度策略：Minimal Fixture vs Strict Fail-Loud

### 矛盾的来源

Spec 原文写了两条互斥的要求：
1. Case JSON 示例只提供 3 个 fixture（`query_logs`/`query_metrics`/`query_deployments`）。
2. 「case 未提供某工具 fixture → fail-loud」。

实际上 `planner` 对 `deployment_regression` 会调度 15+ 个工具（一堆 `query_k8s_*`、`query_db_*`、`query_runbook`）。严格遵守 fail-loud 意味着每个 case JSON 必须写满所有工具，文件膨胀到 60+ 行，新增 case 成本极高。

### 决策：Minimal Fixture + Controlled Empty

未提供 fixture 的只读工具返回 `{}`（受控空结果，`success=True`），不 fail-loud。

**关键论证**：受控空结果依然是 100% 确定的。

- 证据稀疏（`{}`）不等于随机数据。graph 的 critic 节点看到质量低的证据会做相应决策——这本身就是真实行为，不是作弊。
- 每个 case 只需要提供「承载诊断信号的证据」（比如 query_logs 有 500 条错误日志、query_deployments 有一次近期部署）。其他工具的空返回代表「这个维度没有信号」，是真实场景。
- 对比 mock adapter（返回随机仿真数据）：minimal fixture 反而更干净，因为未提供的工具明确返回空，而非返回 mock 随机数据。

**例外**：写类工具（`write_rca_to_oss` 等）和 `execute_action` 默认返回成功桩——不需要这些有副作用的工具的「结果」来评测诊断质量。

---

## 5. 非确定性处理：真实 LLM + --repeat N 的分布式指标

### 为什么用真实 LLM 而不是 mock

这个框架测的是「LLM 推理质量」，不是「框架代码质量」。mock LLM 会 100% 通过每个案例，和不跑一样——框架对 LLM 输出的评估是空转。

框架代码本身的正确性用 mock LLM 在 pytest 里验证（速度快、确定、进 CI）；LLM 推理质量用真实 DeepSeek 离线验证（慢、非确定、手动跑）。两者完全分离，不混用。

### 非确定性的处理方式

同一套数据集跑 N 轮（`--repeat N`），每轮独立评分，报告给出均值 + min/max（或标准差）。

**为什么这比单点更有意义**：

- 单点：「Top1 准确率 75%」可能是运气好或运气差的一次。
- 分布：「3 轮均值 72%，min 67% / max 78%」才是可比较的。

当改了 prompt（Phase 9）或换了模型后，对比的是**分布**，不是单点。一次改动让 mean 从 72% 到 80%，同时 variance 收窄，才是真实的改善信号。

### 为什么明确标注「非 CI 指标」

- 真实 LLM 需要 API key，不能在 CI 里跑。
- 非确定性指标不能作为 merge gate（否则会有随机红绿）。
- 这个框架的定位是「开发者主动跑，用来指导 prompt/模型选型」，不是自动门禁。

报告顶部的声明是有意为之：防止未来有人把这个数字当成 CI 指标来用。

---

## 总结：几个面试常问的 follow-up 答法

**Q: 为什么不用 LLM-as-judge 评测 hypothesis 文字质量？**

A: 首期故意不做。原因是：LLM-as-judge 引入第二个 LLM 变量，指标变化时无法归因（是被评测模型变了还是 judge 变了？）。首期先把「分类准确率」这个可归因指标做扎实，等需要评文字质量时再加 judge 接口——接口已预留，但不实现。

**Q: ContextVar 在 asyncio 里是怎么继承的？**

A: Python 3.7+ 中，`asyncio.create_task()` 会 copy 当前 context 给新 Task。所以 `fixture_scope` 内用 `asyncio.gather()` 并发跑的所有工具调用，都继承了 `_fixture_var` 里的 fixture map，无需显式传参。`ContextVar.set()` 返回 token，`reset(token)` 精确回滚，无论 scope 内是否有异常。

**Q: 为什么不把评测 case 的 fixture 放在 conftest 里？**

A: conftest 是 pytest 测试框架的概念，但真实 DeepSeek 评测是在应用层跑的（`python -m app.evals.replay_runner`），不经过 pytest。fixture_scope 是纯应用层的上下文管理器，独立于测试框架，两者不耦合。

**Q: 如果新增一个 incident_type，需要改哪些地方？**

A: 只需要两步：
1. `app/models/incident_type.py` 枚举加一行。
2. `app/evals/datasets/` 补至少一个该类型的 case JSON。

scorer、metrics、report 都按枚举值动态比对聚合，不硬编码类型清单，无需修改。planner 的证据调度分支按需可选扩展。这是「对扩展开放」的典型设计。
