# 模块一 · 取证与质量门控｜用户旅程与 Agent 设计

> 目标读者：没有经手过 OpsPilot 的工程师、面试官、评审人。
> 这份文档不要求读者先懂 LangGraph，也不假设读者知道项目代码。
> 它回答三个问题：
> 1. 用户如何从一个故障工单走到一个可处置的根因判断？
> 2. Agent 为什么被拆成多个节点？
> 3. 取证、诊断、门控之间如何配合，避免大模型自信地猜错？

---

## 1. 项目一句话

OpsPilot 是一个面向 SRE 故障处置的智能体。它不是聊天机器人，而是一个有状态、有回退、有人工审批、有证据归档的故障处理工作流。

它的核心思想是：

> 故障处置不能先让大模型猜根因，而要先取证、再聚合、再诊断、再门控；只有证据足够可靠，才允许进入处置。

在完整系统里，一次故障会经过：

```text
intake
  -> triage
  -> retrieve_memory
  -> planner
  -> evidence_fanout
  -> evidence_aggregate
  -> diagnose
  -> critic
  -> remediation
  -> risk_gate
  -> approval_interrupt / executor
  -> verify
  -> rca
```

这份文档聚焦中间最关键的一段：

```text
planner -> evidence_fanout -> evidence_aggregate -> diagnose -> critic
```

这段就是 OpsPilot 的“查案子”环节。

---

## 2. 用户旅程总览

从用户视角看，OpsPilot 处理一次故障大致像这样：

```text
用户提交工单或告警
  -> 系统识别故障类型和目标服务
  -> 系统制定调查计划
  -> 多个专家并行只读取证
  -> 系统汇总证据并计算质量分
  -> 系统生成候选根因
  -> 系统审核候选根因是否够可靠
  -> 可靠则进入处置方案
  -> 不可靠则补证、重规划或转人工
```

用户看到的不是“模型随便回答了一个根因”，而是一个逐步收敛的过程：

- 这次事故是什么服务、什么环境、什么严重级别。
- 系统为什么怀疑某类故障。
- 系统查了哪些证据。
- 哪些证据支持当前根因。
- 哪些证据与当前根因冲突。
- 当前结论是否足够可靠。
- 如果不可靠，系统为什么退回补证或转人工。

---

## 3. 用户入口：故障从哪里来

用户可以通过三种方式创建一次故障 run：

### 3.1 手工工单

适合 SRE 或研发手动录入事故。

```json
{
  "ticket": {
    "ticket_id": "INC-001",
    "title": "支付服务5xx升高",
    "description": "发布后部分用户下单失败",
    "service": "payment-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  }
}
```

### 3.2 ticket_id 拉取

适合已有工单系统，用户只提供工单 ID。

```json
{ "ticket_id": "INC-001" }
```

### 3.3 告警事件

适合从 Alertmanager、监控平台或事件系统接入。

```json
{
  "alert_event": {
    "alert_name": "HighErrorRate",
    "service": "payment-service",
    "env": "staging",
    "severity": "P2"
  }
}
```

不管入口是哪一种，进入 Agent 后都会被收敛成统一的 `IncidentTicket` 和 graph state。

---

## 4. 从自然语言到结构化 triage

用户提交的工单里，`title` 和 `description` 是自然语言，比如：

```text
支付服务5xx升高，发布后部分用户下单失败
```

但 planner 不能直接消费自然语言。它需要结构化输入：

```text
incident_type
suspected_services
severity
suggested_time_window
requires_immediate_human
rationale
```

所以在 planner 之前，triage 节点会把工单收敛成 `TriageResult`。

triage 是三段式：

1. **规则优先**
   高确定性关键词直接走规则。比如 `发布 / release / rollback` 对应发布回归，`cpu / memory / oom / disk` 对应资源耗尽，`timeout / 503 / 502 / 依赖` 对应依赖失败。

2. **LLM 补充**
   规则没有命中时，LLM 读取 title、description、service、env、severity，并按 JSON 输出结构化 triage。

3. **fallback 兜底**
   如果 LLM 失败或返回不可解析内容，系统降级成 `service_degradation`，保留服务和严重级别，保证 graph 不会因为模型失败而中断。

这样 planner 拿到的就不是“原始描述”，而是类似：

```python
TriageResult(
    incident_type="deployment_regression",
    severity="P2",
    suspected_services=["payment-service"],
    suggested_time_window={"start": "2h ago", "end": "now"},
    requires_immediate_human=False,
    rationale="发布后错误率升高，疑似发布回归"
)
```

---

## 5. 为什么要工作流，而不是一个大 Prompt

故障处置和普通问答不同。普通问答错了可以重问，故障处置错了可能会触发错误回滚、错误重启、扩大事故。

所以 OpsPilot 不把所有逻辑塞进一个 ReAct agent，而是拆成工作流节点。

这样做有四个目的：

1. **顺序可控**
   必须先取证，再诊断，再门控，再修复。模型不能跳过证据直接给处置动作。

2. **风险隔离**
   取证阶段全是只读工具，执行阶段才允许写操作。读和写必须分开。

3. **可回退**
   证据不够回 fanout；调查方向错回 planner；风险高进 approval；验证失败进 retry 或 RCA。

4. **可审计**
   每个节点都有状态、事件、checkpoint、证据持久化记录。复盘时能知道系统在哪一步做了什么判断。

节点多不是目的，控制点清晰才是目的。

---

## 6. 五个核心节点如何协作

### 6.1 planner：决定查什么

planner 的输入是结构化后的 `ticket + triage`。

它不调用 LLM，而是按 `incident_type` 选择确定性调查模板。

例如 `deployment_regression` 会优先查：

- deployment 历史
- 应用日志
- K8s rollout、pod、event、replicaset、configmap
- metrics
- DB slow query
- runbook

planner 输出的是受控的调查任务，而不是自然语言计划：

```python
InvestigationTask(
    task_id="task_001",
    category="deployments",
    tool_name="query_deployments",
    priority=1,
    params={"service": "payment-service", "env": "staging"}
)
```

它的设计原则是：

> “该查哪”这种关键路由决策交给确定性系统，不交给模型临场发挥。

### 6.2 evidence_fanout：派专家并行取证

fanout 根据 planner 的计划派出多个 specialist agent。

常见专家包括：

```text
k8s / db / logs / metrics / deployments
```

这些专家按观测域划分，不按根因划分。

例如：

- logs 专家看应用异常和错误日志。
- metrics 专家看错误率、延迟和资源趋势。
- k8s 专家看 Pod、事件、HPA、rollout。
- db 专家看连接、慢查询、锁等待。
- deployments 专家看发布历史和版本变化。

fanout 有三个关键约束：

1. **并行**
   多个专家同时取证，整体耗时接近最慢的那一路，而不是所有路径串行相加。

2. **只读**
   取证阶段只查不改，不触碰线上写操作。

3. **单路失败不拖垮整体**
   某个专家失败或超时，只影响该领域质量，不阻断其他专家返回。

### 6.3 evidence_aggregate：把多专家证据合成全局材料包

aggregate 不产出根因。它负责把多个专家看到的局部证据合成一个全局证据包。

它主要输出：

```text
evidence_summary
evidence_quality_score
specialist_analyses
cross_agent_causal_chains
contradiction_signals
```

如果 fanout 派了 3 个专家，不代表 aggregate 输出 3 条根因。

正确关系是：

```text
N 个专家分析 -> 1 个全局证据包 -> diagnose 生成 2-3 个根因候选
```

因为专家是按观测面划分的，不是按根因划分的。同一个根因往往需要多个专家互相印证。

### 6.4 diagnose：基于全局证据生成候选根因

diagnose 才是真正让 LLM 参与根因归纳的节点。

但它不是凭空猜，而是读取 aggregate 输出的证据包：

```text
evidence_summary
evidence_items
contradiction_signals
triage.incident_type
```

然后生成 2-3 个 `RootCauseCandidate`：

```python
RootCauseCandidate(
    hypothesis="v2.8.3 发布后引入空指针异常，导致支付接口 5xx 升高",
    confidence=0.72,
    incident_type="deployment_regression",
    supporting_evidence_ids=["ev_deploy_001", "ev_logs_001", "ev_metrics_001"],
    contradicting_evidence_ids=["ev_k8s_001"],
    next_checks=[
        "检查新旧版本 Pod 的错误分布",
        "对比 v2.8.3 与上一版本的支付参数处理逻辑"
    ]
)
```

这里输出的是“候选根因”，不是最终裁决。

### 6.5 critic：决定候选根因能不能进入处置

critic 是门控节点。

它不重新取证，也不重新诊断。它读取：

```text
evidence_quality_score
contradiction_signals
root_cause_candidates
candidate confidence
contradicting_evidence_ids
loop_count
```

然后做路由裁决：

| 裁决 | 含义 | 下一步 |
|---|---|---|
| PASS | 证据和候选根因足够可靠 | 进入 remediation |
| NEED_MORE_EVIDENCE | 方向大致对，但证据不足 | 回 evidence_fanout |
| REPLAN / CONTRADICTION | 方向或证据链有问题 | 回 planner 或重新取证 |
| NEEDS_HUMAN | 循环耗尽或风险太高 | 转人工/RCA |

critic 的意义是：

> diagnose 负责提出假设，critic 负责判断这个假设是否可靠到可以推进。

---

## 7. 质量分：多专家证据链的可信完成度

质量分不是工具调用成功率，也不是模型拍出的分数。

它衡量的是：

> 这一轮多专家取证是否足够完整、可信、可用于下游诊断。

质量分由四类信号组成：

### 7.1 专家覆盖度

看 5 类关键专家是否都有有效输出：

```text
k8s / db / logs / metrics / deployments
```

只靠一个日志专家，即使它置信度很高，也不能代表全局可靠。

### 7.2 专家置信度

每个 `SpecialistAnalysis` 有自己的 `confidence`。

aggregate 会对有效 agent 的 confidence 做平均，作为基础质量。

### 7.3 降级惩罚

如果某个 agent 是 `partial=True`，说明它只产出了降级分析，不是完整分析。

这种结果会被打折。

### 7.4 截断惩罚

如果某个 agent 是 `truncated=True`，说明它因为超时、轮次限制或上下文限制没有完整分析。

这种情况会对整体质量施加惩罚。

所以质量分可以理解为：

```text
平均专家置信度 × 专家覆盖度 × 降级惩罚 × 截断惩罚
```

这背后的 SRE 原则是：

> 根因判断必须依赖多个观测面互相印证，不能让单点高置信掩盖全局证据缺口。

---

## 8. 矛盾检测：不是阻止诊断，而是约束诊断

矛盾检测放在 aggregate 阶段。

原因很简单：只有 aggregate 同时看得到多个专家视角，才能判断跨域冲突。

例如：

```text
logs 异常 + k8s 正常
```

这不是说证据无效，而是说明：

```text
应用层异常存在，但缺少基础设施异常支撑，所以根因可能不是 K8s 资源层。
```

aggregate 会把这种信号写入：

```python
state["contradiction_signals"]
```

然后 diagnose 在这个约束下生成候选根因，critic 再判断是否放行。

正确链路是：

```text
aggregate 发现矛盾
  -> diagnose 生成带不确定性的候选根因
  -> critic 判断是否补证、重规划或转人工
```

不是：

```text
证据有矛盾 -> 还强行修复
```

---

## 9. 一个带矛盾信号的完整例子

事故：

```text
支付服务 5xx 升高，用户下单失败
```

fanout 派出 4 个专家：

```text
logs_agent
metrics_agent
k8s_agent
deployments_agent
```

专家返回：

```text
logs_agent:
  异常：payment-service 出现大量 NullPointerException
  时间点：14:05 开始
  证据：ev_logs_001

metrics_agent:
  异常：5xx 从 0.2% 升到 8%，p95 latency 升高
  时间点：14:06 开始
  证据：ev_metrics_001

k8s_agent:
  正常：Pod 没有重启，CPU/Memory 正常，HPA 正常，没有 OOM
  证据：ev_k8s_001

deployments_agent:
  异常：payment-service 在 14:00 发布了 v2.8.3
  证据：ev_deploy_001
```

aggregate 输出：

```python
{
    "evidence_summary": "logs/metrics/deployments 异常，k8s 正常",
    "evidence_quality_score": 0.82,
    "contradiction_signals": [
        {
            "anomaly_category": "logs",
            "normal_category": "k8s",
            "reason": "应用层故障，非基础设施"
        }
    ],
    "cross_agent_causal_chains": [
        {
            "chain": ["deployments", "logs", "metrics"],
            "anomalies_along_path": [
                "new_release",
                "NullPointerException",
                "high_5xx"
            ]
        }
    ]
}
```

diagnose 输出候选：

```python
[
    {
        "incident_type": "deployment_regression",
        "hypothesis": "v2.8.3 发布后引入空指针异常，导致支付接口 5xx 升高",
        "confidence": 0.72,
        "supporting_evidence_ids": [
            "ev_deploy_001",
            "ev_logs_001",
            "ev_metrics_001"
        ],
        "contradicting_evidence_ids": ["ev_k8s_001"],
        "next_checks": [
            "检查新旧版本 Pod 的错误分布",
            "对比 v2.8.3 与上一版本的支付参数处理逻辑"
        ]
    },
    {
        "incident_type": "configuration_error",
        "hypothesis": "发布同时带入配置变更，导致支付参数为空",
        "confidence": 0.48,
        "supporting_evidence_ids": ["ev_logs_001", "ev_metrics_001"],
        "contradicting_evidence_ids": [],
        "next_checks": [
            "检查配置中心在 14:00 附近的变更记录"
        ]
    }
]
```

critic 决策：

```text
存在矛盾信号和反证，不直接进入高风险处置。
要求补查新旧版本 Pod 的错误分布、deployment diff 或配置变更。
```

这个例子说明：

> 矛盾不是让系统停止思考，而是让系统降低置信度、保留反证、提出下一步验证，并由 critic 阻止它直接进入处置。

---

## 10. next_checks：候选根因的验证清单

`next_checks` 不是执行计划，也不是自动修复动作。

它是每个候选根因附带的“假设验证清单”：

```text
如果这个根因是真的，下一步应该看到什么证据？
如果这个根因是假的，什么证据会推翻它？
```

来源有三层：

1. **证据反推**
   根据当前 supporting evidence 和 contradicting evidence 找证据缺口。

2. **故障类型模板**
   发布回归查 deployment diff、新旧版本对比、错误时间线。
   资源耗尽查 CPU、memory、HPA、DB 连接。
   依赖失败查下游超时、SLB、调用链和错误码分布。

3. **结构化 LLM 补全**
   LLM 根据证据摘要补全现场相关检查项，但输出必须落到固定结构。

当前实现里，diagnose prompt 要求候选根因包含：

```json
{
  "incident_type": "...",
  "hypothesis": "...",
  "confidence": 0.72,
  "next_checks": ["..."]
}
```

更生产化的形态可以把 `next_checks` 从字符串数组升级成结构化对象：

```json
{
  "check": "检查 v2.8.3 发布后错误是否集中在新版本 Pod",
  "purpose": "验证发布回归假设",
  "target_hypothesis": "deployment_regression",
  "expected_signal": "新版本 Pod 的 5xx 明显高于旧版本",
  "tool_hint": "query_logs / query_k8s_pods / query_deployments",
  "priority": 1,
  "read_only": true
}
```

关键边界：

> next_checks 只能驱动后续只读取证或人工排查，不能直接驱动 rollback/restart。

---

## 11. 多个根因候选最后怎么进入处置

diagnose 可以输出 2-3 个候选根因，用来表达不确定性。

但处置动作必须收敛到一个主假设，否则动作可能互相冲突。

所以候选会按 `confidence` 降序排序：

```text
1. deployment_regression confidence=0.82
2. configuration_error confidence=0.61
3. dependency_failure confidence=0.44
```

critic 放行后，remediation 只读取：

```python
candidates[0]
```

也就是 top candidate。

后两条不会驱动动作，但会保留在 state 和 RCA 中，表示系统当时考虑过这些可能性。

这样做的原因：

- 处置动作必须有唯一主假设。
- 候选列表是诊断信息，不是执行队列。
- 低置信候选用于审计和复盘。
- 如果后续验证失败，RCA 能回看系统当时是否忽略了其他候选。

---

## 12. Loop guard：为什么默认两轮

证据不足时，critic 会让系统回到 fanout 或 planner。

但系统不能无限循环。

默认最多两轮，含义是：

```text
首轮取证 + 一次纠偏
```

两轮不是数学唯一正确值，而是工程阈值，平衡：

- 补证收益
- 时间成本
- 自动化误判风险
- 人工介入时机

如果两轮后仍然无法形成可靠结论，通常意味着：

- 工具接入失败
- 权限或配置缺失
- 故障类型判断不准
- 观测面缺失
- 事故需要人工上下文

这时继续第三轮、第四轮，很可能只是重复消耗时间。

所以系统会转人工，并写入：

```text
terminal_reason = EVIDENCE_LOOP_EXHAUSTED
```

同时降低候选根因置信度，避免下游误以为系统很确定。

---

## 13. 和裸 ReAct agent 的区别

裸 ReAct agent 的特点是：

```text
模型自己决定查什么
模型自己决定什么时候停
模型自己决定下一步动作
```

这在低风险问答里可以接受，但在故障处置里风险很高：

- 容易越查越偏。
- 上下文越塞越满。
- 缺少硬门控。
- 难以中途人工截停。
- 难以解释为什么进入处置。

OpsPilot 的设计是：

```text
确定性系统掌控流程
LLM 只做理解和归纳
高风险动作必须过门控和审批
```

planner 不是 LLM 生成的，critic 不是 LLM 自己给自己放行，risk_gate 和 approval_interrupt 负责把写操作控制住。

这就是“控制权归工作流，归纳权给模型”。

---

## 14. 给新人的一条主线

如果你第一次接触这个项目，只需要先记住这条主线：

```text
用户提交故障
  -> triage 把自然语言收敛成结构化故障类型
  -> planner 按故障类型决定查什么
  -> fanout 派多个专家只读取证
  -> aggregate 汇总多专家证据、算质量分、发现矛盾
  -> diagnose 基于证据生成候选根因
  -> critic 判断候选是否可靠到可以进入处置
  -> 不可靠就补证/重规划/人工
  -> 可靠才进入 remediation 和后续风险门控
```

这套设计的核心不是“让模型更会猜”，而是：

> 让模型在证据约束下归纳，让系统在工作流约束下放行。

---

## 15. 关键设计决策

| 设计点 | 决策 | 原因 |
|---|---|---|
| 根因生成 | 不直接让 LLM 看工单猜 | 避免幻觉直接进入处置链路 |
| 调查计划 | planner 确定性模板生成 | “该查哪”是关键路由，必须可复现 |
| 取证方式 | 多专家并行只读 | 快、互不拖累、低风险 |
| 证据聚合 | aggregate 独立成层 | 证据工程和根因推理分离 |
| 质量分 | 多专家可信完成度 | 覆盖度、置信度、降级、截断都影响可靠性 |
| 矛盾检测 | 放在 aggregate | 只有聚合层能看到跨专家冲突 |
| 根因候选 | diagnose 输出 2-3 个 | 表达不确定性，保留审计信息 |
| 处置输入 | 只吃 top candidate | 避免多个候选驱动冲突动作 |
| 门控 | critic 独立仲裁 | 避免“提出结论的人自己放行自己” |
| 循环上限 | 默认两轮 | 首轮取证 + 一次纠偏，避免无限消耗 |
| 写操作 | risk_gate + approval | 高风险动作必须受控 |

---

## 16. 最终一句话

OpsPilot 的取证与质量门控模块，本质是把 SRE 的排障经验工程化：

> 先把故障结构化，再按类型规划调查；多专家并行只读取证；聚合证据并计算可信完成度；让模型只在证据上提出候选根因；再由 critic 判断这个候选是否可靠到可以进入处置。证据不够就补证，方向不对就重规划，循环耗尽就转人工。

这就是这个模块的用户旅程和 Agent 设计。
