# OpsPilot Phase 8 离线评测设计

> 生成时间: 2026-06-06
> 对应 ACTION_PLAN Phase 8 / Task 8.1
> 范围: 单 spec，内部分两阶段交付 —— Phase 8.0（结构化根因生产改动）→ Phase 8.1（评测框架）

## 目标

为 OpsPilot 建立离线评测能力：用固定证据输入、真实 LLM 推理，量化 graph 的故障诊断质量
（根因分类准确率、风险判定、终态正确性等），并让「Prompt / 模型 / graph 改动前后」的对比
建立在**可归因、可复现结构上的稳定指标**之上。

核心设计判断：

- **评测时打真实 DeepSeek**，测的是端到端真实推理质量；工具层用 fixture 固定证据，使评测
  变量只剩 LLM 推理本身。
- **根因评测对象与标签空间必须对齐**：让 diagnose 节点显式输出封闭枚举 `incident_type`，
  主指标用枚举等值比较，而非事后用关键词或 LLM 猜测自由文本属于哪一类。
- **两层评测分层不混指标**：第一层 Graph Quality（测诊断准不准）与第二层 Runtime Fidelity
  （测生产链路跑得对不对）是两类不同问题，永不合并成一个综合数字。

## 范围

### 本轮包含

**Phase 8.0 — 结构化根因输出（生产改动，先交付）**

- 新增共享枚举 `IncidentType`（11 个一级类型，含 `unknown` / `other`）。
- 收敛 `triage` 现有 magic-string incident_type 到该枚举（仅引用对齐，不重写判断逻辑）。
- 扩展 `RootCauseCandidate`：新增 `incident_type` 字段，保留 `hypothesis` / `confidence`。
- 改造 diagnose：prompt 要求输出 `{incident_type, hypothesis, confidence}`；解析时校验枚举、
  非法降级 `other`；候选按 confidence 降序排序；LLM 失败 fallback 给 `unknown`。

**Phase 8.1 — 评测框架（后交付，依赖 8.0）**

- `GraphExecutor` Protocol + `DirectGraphExecutor`（第一层，做扎实）+ `RunnerGraphExecutor`
  （第二层，搭骨架）。
- 作用域化 fixture 注入（ContextVar，复刻 `app/graph/context.py` 模式）。
- 数据集格式 + case 加载校验 + 确定性 scorer + 指标聚合 + JSON/Markdown 报告。
- CLI 入口 `replay_runner.py`，三模式 `--mode direct|runner|compare`，`--repeat N` 多轮求
  均值+波动。
- 首期数据集 10-15 个高质量 case（每类至少 1 个 + 关键风险/审批场景），设计成易扩展。
- 评测框架自身的单元测试（mock LLM，确定、进 CI）。

### 本轮不包含

- 第二层 Runtime Fidelity 的完整实现（首期仅 executor 接口 + RunnerGraphExecutor +
  1-2 个冒烟 case + compare 模式留接口）。
- LLM-as-judge 评 hypothesis 质量（首期 hypothesis 只采集不评分，留接口）。
- 数据集扩充到 30-50（按类别统计意义补齐，留待后续）。
- Prompt 版本管理与回放对比（Phase 9.2 范畴）。
- 把评测纳入 CI 跑真实 LLM（真实评测始终手动离线）。

---

## Phase 8.0：结构化根因输出

### 现状与问题

- diagnose 输出 `RootCauseCandidate.hypothesis` 是自由文本，无封闭分类字段。
- `triage` 已在用一套 incident_type 标签，但全是 magic string，散落在 prompt 与规则中
  （`deployment_regression` / `resource_exhaustion` / `dependency_failure` /
  `security_incident` / `service_degradation`），且 planner 的证据调度已在按这些字符串分支。
- 评测的标签空间是封闭枚举，与自由文本不对齐 —— 若用关键词或 LLM-judge 事后归类，评判器
  本身会引入波动，无法干净归因。

### 设计

**1. 新增 `app/models/incident_type.py`**

```python
class IncidentType(str, Enum):
    deployment_regression = "deployment_regression"   # 发布变更(代码/配置/镜像/依赖版本)直接引入
    configuration_error   = "configuration_error"     # 非发布的配置错误(手工改动/环境漂移/配置中心)
    resource_exhaustion   = "resource_exhaustion"     # CPU/内存/连接池/磁盘耗尽
    dependency_failure    = "dependency_failure"      # 下游/第三方依赖不可用
    database_failure      = "database_failure"        # DB 层故障(慢查询/锁/连接/主从)
    network_failure       = "network_failure"         # 网络/DNS/LB 链路
    traffic_anomaly       = "traffic_anomaly"         # 流量突增/异常请求模式
    security_incident     = "security_incident"       # 安全事件(入侵/漏洞利用/异常访问)
    service_degradation   = "service_degradation"     # 服务自身退化(非以上明确归因)
    unknown               = "unknown"                 # 证据不足，无法判断
    other                 = "other"                   # 已判因但超出标签体系
```

- 边界原则：互斥、有定义。`deployment_regression` vs `configuration_error` 按「是否由发布
  变更引入」切分。
- `unknown`（证据不足）与 `other`（已判因但超纲）区分，避免模型被迫错选造成虚假准确率。
- triage 现有 5 个 magic-string 值（`deployment_regression` / `resource_exhaustion` /
  `dependency_failure` / `security_incident` / `service_degradation`）在此枚举中均有对应，
  收敛为纯引用对齐、零语义丢失。
- **可扩展**：新增类型 = 加一行枚举 + 数据集补该类 case，不动评测框架代码（scorer 按枚举值
  动态比对，不硬编码类型清单）。详见末尾「如何新增一个 incident_type」。

**2. 扩展 `RootCauseCandidate`（`app/models/root_cause.py`）**

- 新增 `incident_type: IncidentType = IncidentType.unknown`（带默认值）。
- 保留 `hypothesis` / `confidence` / `supporting_evidence_ids` 等全部现有字段。
- 向后兼容：新字段有默认值，旧 checkpoint 反序列化不报错。

**3. 改造 diagnose（`app/graph/nodes/__init__.py`）**

- prompt 要求 LLM 输出 JSON：`{incident_type(从枚举选), hypothesis, confidence}`，并说明
  unknown/other 的区别。
- 解析校验 `incident_type` 在枚举内；非法值降级为 `other` 并记 warning。
- **候选按 confidence 降序排序**，保证 `root_cause_candidates[0]` 是最可信候选（评测 Top1
  定义依赖此，critic/remediation 读 `[0]` 也受益）。
- LLM 失败时现有规则 fallback 仍跑，给 `incident_type = unknown`。

**4. triage / planner 引用收敛**

- triage 输出与 planner 分支逻辑中的 incident_type magic string 改为引用 `IncidentType` 常量。
- 只做引用对齐，不重写判断逻辑，改动面最小。

### 下游兼容

- critic / remediation / rca 目前只读 `hypothesis` / `confidence`，新字段纯增量，不受影响。

### 影响文件

`models/incident_type.py`(新)、`models/root_cause.py`、`models/triage.py`、
`graph/nodes/__init__.py`（diagnose + triage + planner 引用收敛）。

### 测试（mock LLM，进 CI）

- diagnose 输出 `incident_type` 一定在枚举内。
- LLM 返回枚举外乱值 → 降级 `other`。
- 候选按 confidence 降序。
- LLM 失败 → fallback 给 `unknown`，不崩。

---

## Phase 8.1：评测框架

### 执行架构（两层，共享一切，只在「怎么执行 graph」分叉）

**`GraphExecutor` Protocol（`app/evals/executors.py`）**

```python
class GraphExecutor(Protocol):
    async def execute(self, case_id: str, initial_state: dict) -> dict: ...
```

| 实现 | 调用方式 | 副作用 | 用途 | 本轮深度 |
|------|----------|--------|------|----------|
| `DirectGraphExecutor` | `create_incident_graph().ainvoke(state, config={"configurable":{"thread_id": f"eval-{case_id}"}})` | 无 DB / 无事件 | 第一层 Graph Quality（全量 case） | **做扎实** |
| `RunnerGraphExecutor` | `GraphRunner.run(run_id=f"eval-{case_id}", initial_state)` → 返回 final_state dict | 完整生产链路 | 第二层 Runtime Fidelity（代表性子集） | **搭骨架** |

> 已核实：`GraphRunner.run` 直接返回 final_state dict（用 `astream` 逐节点累积），不是带
> `.final_state` 属性的对象。`RunnerGraphExecutor` 取返回值本身。

**前置生产改动（已核实当前不支持）**

- `create_incident_graph()` 当前硬编码无参 `graph.compile()`（builder.py:272）。改签名为
  `create_incident_graph(checkpointer=None)`，透传 `compile(checkpointer=checkpointer)`。
  默认 `None` → 生产行为完全不变；direct 模式可传 `MemorySaver()` 测 resume 语义。这是唯一
  为评测动的 graph 构建改动，向后兼容。

**本项目 interrupt/resume 的真实机制（非通用 LangGraph 原生 interrupt）**

- 机制：`node_approval_interrupt → END` + 状态 `WAITING_HUMAN`，resume 由
  `approval_runtime.py` 重建 state 再从 `node_risk_gate` 续跑。
- 因此第二层 Fidelity 测的是：① 终态正确落到 `WAITING_HUMAN`；② 自有 checkpoint 表写入成功；
  ③ 经 `approval_runtime` resume 能从 `node_risk_gate` 续跑到终态；④ 事件顺序/数量；
  ⑤ direct vs runner 终态业务字段一致（compare 模式）。

**CLI 三模式（`replay_runner.py`）**

- `--mode direct`（默认）：全量质量评测，只走 graph。
- `--mode runner`：子集保真评测，只走 GraphRunner。
- `--mode compare`：同 case 跑两条路径，diff 终态 `incident_type` / `status`，抓 GraphRunner
  改变 graph 语义或状态序列化丢字段。

两层指标永不合并成一个综合数字。

### 作用域化 Fixture 注入

**目标**：固定证据输入，按 case 隔离，并发安全，生产路径零影响。复刻项目已有的
`app/graph/context.py` ContextVar 模式（GraphRunner 通过 ContextVar 注入 event hook 到节点），
不发明新机制。

**机制（`app/evals/fixture_context.py`）**

```python
_fixture_hook: ContextVar[Optional[dict]] = ContextVar("eval_fixtures", default=None)

@contextmanager
def fixture_scope(fixtures: dict):      # fixtures: {tool_name: result_dict}
    token = _fixture_hook.set(fixtures)
    try:
        yield
    finally:
        _fixture_hook.reset(token)
```

**gateway 读取点**：`gateway.call_tool` 开头加一段 —— 若 `_fixture_hook.get()` 非空且含该
`tool_name`，直接返回 fixture 包装的 `ToolResponse(success=True, result=...)`，短路真实/mock
adapter。无 fixture context 时（生产/普通单测）走原逻辑，零行为变化。短路发生在 mock/real
判断之前，与 autouse conftest 强制 mock adapter 不冲突。

**为何用 ContextVar 而非 monkeypatch / 全局模式开关**

- ContextVar 跟随 async 任务自动隔离 → 并发评测多 case 不串数据（gateway 保持无状态）。
- 不翻转全局单例状态 → 无「改了模式忘改回」的污染。
- 与现有 `graph/context.py` / `tracing.py`（run_id_var）同构，团队心智一致。

**fixture 粒度与缺失策略**

- 按 `tool_name` 提供。
- **fail-loud**：case 未提供某工具 fixture → 报错「case X 未提供 tool Y 的 fixture」，作为该
  case 的 error 捕获（不静默回退 mock），强制数据集证据 100% 可控。
- 例外：写类工具（`write_rca_to_oss` 等）和 `execute_action` 默认返回成功桩，不强制 fixture。

### 数据集格式（`app/evals/datasets/*.json`，一文件一 case）

```json
{
  "case_id": "case_001_deploy_regression",
  "description": "用于人类阅读的场景说明",
  "ticket": {
    "ticket_id": "INC-EVAL-001", "title": "...", "description": "...",
    "service": "payment-service", "env": "staging",
    "severity": "P2", "source": "manual"
  },
  "tool_fixtures": {
    "query_logs":        { "logs": [], "count": 12 },
    "query_metrics":     {},
    "query_deployments": {}
  },
  "expected": {
    "incident_type": "deployment_regression",
    "risk_decision":  "NEEDS_APPROVAL",
    "final_status":   "WAITING_HUMAN"
  }
}
```

- `ticket` 复用现有 `IncidentTicket` 结构。
- `expected` 各字段可选 —— 只填的参与评分，没填的跳过（数据集可渐进完善）。

### Scorer（`app/evals/scorer.py`，确定性，无 LLM）

- **主指标命中**：`actual.root_cause_candidates[0].incident_type == expected.incident_type`
  （Top1）；任一候选命中 = Top3。纯枚举等值。
- **风险**：`actual.risk_decision == expected.risk_decision`。
- **终态**：`actual.status == expected.final_status`。
- 每 case 产出 `CaseResult{case_id, hit_top1, hit_top3, risk_match, status_match,
  actual_type, expected_type, confidence, latency_ms, error}`。

### 指标（`app/evals/metrics.py`，纯 stdlib，无 pandas）

| 指标 | 作用 |
|------|------|
| Incident Type Accuracy (Top1 / Top3) | 主指标 |
| Macro F1 | 各类别 F1 平均，防大类掩盖小类 |
| Per-class Recall | 每类漏诊率 |
| Confusion Matrix | 哪些根因易混淆（嵌套 dict） |
| Unknown Rate | 模型判 unknown 比例（是否过度保守） |
| 风险准确率 / 终态准确率 / 平均 confidence / 平均 latency | 辅助 |

**Hypothesis Quality**：首期只采集不评分 —— 把每个 case 的 hypothesis 文本连同 incident_type
落进报告供人工抽查。LLM-as-judge 留接口、首期不实现。

**真实 LLM 非确定性处理**：

- 报告显式标注「真实 LLM、结果有波动、非 CI 指标」。
- `--repeat N`：同数据集跑 N 轮，报告给每指标的均值 + 波动范围（min/max 或标准差），让
  Prompt 改动对比建立在分布而非单点。首期实现，默认 N=1。

### 目录结构（`app/evals/`，当前空目录）

```
app/evals/
  __init__.py
  datasets/          # 10-15 个 case JSON
  executors.py       # GraphExecutor Protocol + Direct + Runner(骨架)
  fixture_context.py # ContextVar fixture 注入 + fixture_scope()
  case_loader.py     # 读取 + 校验 dataset JSON
  scorer.py          # 单 case 评分(确定性)
  metrics.py         # 聚合指标
  report.py          # JSON + Markdown 报告生成
  runner.py          # 编排: 加载 → fixture_scope → execute → score → repeat → 聚合
  replay_runner.py   # CLI 入口(--mode/--repeat/--dataset/--output)
```

对齐 ACTION_PLAN Task 8.1 命名（`replay_runner.py` / `metrics.py` / `datasets/`），按职责拆分
到单一用途小文件。

### 错误处理（评测框架自身要稳）

- **单 case 隔离**：某 case 抛异常 → 记为 error，继续跑其余，报告单列 error cases。
- **fixture 缺失**：fail-loud，作为该 case 的 error 捕获，不中断整批。
- **LLM 调用失败**：graph 节点有 fallback，评测照常拿终态（可能是 fallback 的 unknown），
  如实计入，反映降级质量。
- **数据集 schema 非法**：加载阶段 fail-fast，明确报「哪个 case 哪个字段不对」。
- **API key 缺失**：真实 LLM 跑前预检 `DEEPSEEK_API_KEY`，缺失直接报错。

### 测试策略

区分两种「测试」：

| | A. 真实评测运行 | B. 评测框架单元测试 |
|---|---|---|
| 测谁 | graph 诊断准不准 | 评测框架代码本身写对没 |
| LLM | 真实 DeepSeek | 假 LLM（写死返回） |
| 跑法 | 手动 `python -m app.evals.replay_runner` | 跟 pytest 自动跑，进 CI |

**B. 评测框架单元测试（mock LLM，确定，进 `app/tests/`）**

- `scorer` / `metrics`：纯函数，喂造好的 `CaseResult` 验算 Top1/3、Macro F1、混淆矩阵、
  per-class recall。
- `fixture_context`：验证 `fixture_scope` 内 `gateway.call_tool` 返回 fixture、退出后恢复、
  并发 case 隔离。
- `case_loader`：合法/非法 schema 的加载行为。
- `DirectGraphExecutor`：mock LLM（复用 `test_graph_integration.py` 的 `fake_complete_sync/async`
  手法）跑 1 个端到端 case，验证 fixture 注入 + 终态提取链路通 —— 不打真实 LLM。
- 全部遵守 autouse mock adapter 约定。

**边界**：单测全程 mock LLM（进 CI）；真实 DeepSeek 评测是手动离线跑，不进 CI、不进 pytest。

---

## 如何新增一个 incident_type（扩展指引）

1. 在 `app/models/incident_type.py` 的 `IncidentType` 枚举加一行（值用 snake_case）。
2. 若该类型需要专属证据调度，在 planner 分支补对应逻辑（可选）。
3. 在 `app/evals/datasets/` 补至少 1 个该类型的 case JSON（`expected.incident_type` 填新值）。
4. 无需改动 scorer / metrics / 报告代码 —— 它们按枚举值动态比对与聚合。
5. 跑 `python -m app.evals.replay_runner --mode direct` 确认新类型纳入混淆矩阵与 per-class
   recall。

---

## 交付顺序

```
Phase 8.0  结构化根因输出(生产改动)
  ├─ IncidentType 枚举 + triage/planner 引用收敛
  ├─ RootCauseCandidate.incident_type
  ├─ diagnose prompt/解析/排序/fallback
  └─ 8.0 单测通过                              ← 地基稳固后再进 8.1
        │
Phase 8.1  评测框架
  ├─ create_incident_graph(checkpointer=None)
  ├─ fixture_context + gateway 读取点
  ├─ executors(Direct 扎实 / Runner 骨架)
  ├─ case_loader / scorer / metrics / report / runner
  ├─ replay_runner CLI(--mode/--repeat)
  ├─ 10-15 个 case 数据集
  └─ 评测框架单测通过
```

## 验收

- `python -m app.evals.replay_runner --mode direct --dataset app/evals/datasets/ --repeat 3`
  输出 JSON + Markdown 报告，含 Top1/Top3 准确率、Macro F1、混淆矩阵、per-class recall、
  unknown rate、风险/终态准确率，以及 N 轮均值 + 波动范围。
- 报告显式标注「真实 LLM、非 CI 指标」。
- 某 case fixture 缺失时 fail-loud，不污染整批。
- 评测框架单元测试全部通过（mock LLM，确定）。
- 8.0 结构化根因单测通过，生产 graph 行为不变（checkpointer 默认 None）。
- compare 模式可运行（骨架），diff 终态业务字段。
```
