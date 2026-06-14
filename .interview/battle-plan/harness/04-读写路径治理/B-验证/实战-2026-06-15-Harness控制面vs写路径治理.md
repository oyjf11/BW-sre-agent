# 实战沉淀 · Harness 控制面 vs 写路径治理（批判一篇营销文）

> 🎯 一句话 kernel（背这句）：只读 Agent 的 Harness 只是控制面治理（限流/追踪/评测）；有副作用动作才是深水区——幂等键、HITL 审批、loop guard。

## 母题速记
| 触发（面试官会问） | kernel（背这句） | 项目锚点（这次具体对照了什么） | 可能追问 |
|---|---|---|---|
| "你怎么理解 Agent Harness / 治理层？" | Harness 是 Agent 的控制面，和业务逻辑解耦——可观测、流量、安全、评测都不侵入节点代码 | OpsPilot：tracing 独立 span 记录器 + gateway 统一收口 schema 校验/重试/audit，13 节点零侵入 | "解耦具体怎么落？provider 挂了会拖垮主流程吗？"→ tracing.py 所有外部 provider 调用 try/except 包裹 |
| "Harness 最难的部分是什么？" | 只读问答的 Harness 是简单模式；有副作用动作（回滚/重启/改配置）才难：幂等防重放、前置校验、HITL 审批、loop guard 防失控、证据-动作绑定 | OpsPilot 写路径全套：executor 幂等键 + preconditions、risk_gate→approval、critic loop guard max 2 | "幂等键怎么设计的？重复提交同一动作会怎样？"→ idempotency_key 查重，已 COMPLETED/EXECUTING 直接 skip |
| "看到一篇讲 Harness 的文章你怎么判断好坏？"（考批判力） | 三层定位（框架/低代码/治理）站得住；但全文数字是白皮书体、公式是装饰数学、代码是 demo 级（进程内字典限流多副本即失效） | 对照真实实现，逐条证伪：限流状态没共享、hset 覆盖丢步骤、注入检测同步调 LLM 自相矛盾 | "那你项目限流怎么做？"→ 诚实边界见下 |

<details>
<summary>📖 详细复盘 + 面试问答底稿（点开）</summary>

## 详细复盘

**背景**：用户拿一篇 CSDN 文章《AI Agent Harness Engineering 技术白皮书解读》，让我以面试视角做批判性评估，并对照 OpsPilot 真实实现，分清哪些是真知灼见、哪些是营销话术。

**做法**：我先核对 OpsPilot 关键文件（tracing.py / gateway.py / executor.py / critic_node / risk_gate_node），再逐条对照文章主张。

**结论分三层**：

1. **站得住的**：
   - "三层定位"表（开发框架 LangChain＝怎么快速写；低代码 Dify/Coze＝怎么可视化搭；Harness＝怎么让它生产稳定跑）——治理层与业务逻辑解耦的定位正确，OpsPilot 正是这么落的。
   - "零侵入追踪 + 异步上报、延迟影响小"的工程取舍方向对。
   - 安全"双层检测"（先本地正则、匹配不中再调 LLM）方向对。

2. **营销话术 / 存疑数据**：
   - 几乎所有数字无可验证来源："92% demo 无法落地""排查耗时 5~10 倍""安全拦截率 30%→99.2%, +230%""排查 2 小时→5 分钟"——典型厂商软文对照表。
   - 把自造名词包装成既有标准："OpenHarness""《OpenHarness 白皮书 v1.0》""github.com/open-harness"大概率虚构，却和真品牌 LangSmith/AgentOps 并列背书。
   - 生产可用性公式 `A = (T_valid/T_total)×C_consistency×S_safety×P_performance`：四个 0~1 指标强相关却假设独立直接相乘，无理论依据，是"看起来很 PhD、实则不可优化"的装饰数学。

3. **代码是 demo 级（面试可当反例）**：
   - 限流用进程内 `request_times = {}` 字典 → 多副本部署限流状态不共享，直接失效（且它自己在讲分布式）。
   - `record_trace_step` 用 `hset(..., "steps", json)` 每步覆盖同一 field → 多步只剩最后一步，是 bug。
   - 注入检测同步调 gpt-3.5-turbo 判"是/否"，和它鼓吹的 "<50ms 延迟" 自相矛盾。
   - `check_permission` 直接 `return True`，越权校验是空壳。

## 关键取舍（这次最值钱的一条）

**文章把 Agent 当"只读问答系统"治理**（全程举例客服/知识库 Agent），所以它的 Harness 难点停在限流/追踪/仿真测试这些"读路径"。**OpsPilot 的主战场是写路径**——Agent 要执行有副作用的动作（rollback/restart/改配置），真正的治理难点是：

| 维度 | 文章 | OpsPilot 真实实现 |
|---|---|---|
| 执行幂等 | 没提 | executor.py:62 `idempotency_key` 查重，已 COMPLETED/EXECUTING 直接 skip |
| 前置校验 | 没提 | `_check_preconditions`：执行前查 service_exists / deployment_healthy |
| HITL | 完全没有 | risk_gate_node→approval_interrupt_node，prod/HIGH 风险动作强制人工审批 |
| 循环失控 | 只说"陷入死循环" | critic_node loop guard：max 2 轮，耗尽转 NEEDS_HUMAN + terminal_reason |
| 失败兜底 | 说"熔断降级" | 每节点结构化 terminal_reason（CANNOT_GENERATE_TRUSTED_ACTIONS 等），不 silent fail |

一句话：**只读 Agent 的 Harness 谁都能搭；有副作用动作的 Harness 才是面试深水区。**

## 面试问答底稿

**Q：你怎么理解 Agent Harness / 治理层？**
**A（两层）：**
- 通用层：Harness 是 Agent 的控制面（control plane），不是数据面——把可观测、流量管控、安全、评测从业务逻辑里抽出来，不侵入节点代码。三层区分：开发框架解决"怎么写"，低代码平台解决"怎么可视化搭"，Harness 解决"怎么生产稳定跑"。
- 但这个项目实际上：只读 Agent 的治理是简单模式（限流/追踪/仿真测试）。OpsPilot 是 SRE 故障处置 Agent，要执行有副作用的修复动作，所以真正的 Harness 难点在写路径：幂等键防重放、前置条件校验、HITL 审批门、loop guard 防失控、证据-动作绑定可追溯。

**Q：那篇文章/这套方案你觉得有什么问题？**（考批判力）
**A：** 定位表是对的，但数字全是无来源的白皮书体、公式是相关变量硬相乘的装饰数学、代码是 demo 级——限流用进程内字典多副本就失效，追踪 hset 覆盖同 field 会丢步骤。demo 和生产的差距就在这些细节。

**诚实边界：**
- OpsPilot 代码主要由 coding agent 生成；这次我做的是**审查文章主张 + 核对真实代码 + 拍板哪些站得住**，不是我手写了这套 Harness。我的差异化在判断方向（"这篇是营销文，值得逐条对照证伪"）和验证证据链是否立得住，不在"我从零实现了限流"。
- 限流/分布式状态共享这类，我能指出文章的进程内字典错在哪、该用 Redis 滑动窗口；但要我现场手写一个生产级令牌桶限流器，得查实现细节，不会假装张口就来。

## 关键文件速查
| 关注点 | file:line |
|---|---|
| 执行幂等 + 前置校验 + audit | backend/app/services/executor.py:62、:88、:120 |
| 幂等查重 skip 逻辑 | backend/app/services/executor.py:64-85 |
| critic 4 路裁决 + loop guard max 2 | backend/app/graph/nodes/__init__.py:1074-1133 |
| risk_gate 审批门 | backend/app/graph/nodes/__init__.py:1208 |
| approval_interrupt（HITL 落库） | backend/app/graph/nodes/__init__.py:1321 |
| gateway schema 校验/重试/audit/脱敏 | backend/app/tools/gateway.py:840、:860、:1063、:1082 |
| tracing 独立 span + provider 容错 | backend/app/tracing.py:44-70、:60-69 |

</details>
