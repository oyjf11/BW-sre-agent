# SRE Agent 重构实施计划

## 项目背景

基于 `review.md` 的分析，本项目是一个典型的"骨架先行、血肉缺失"型工程：
- 目录结构完整
- API、Repo、模型、Mock 都已搭建
- 但核心闭环未落地：LangGraph 未真正执行、节点是硬编码占位、真实适配器未接通

---

## 重构策略：7 阶段从假到真收敛

### 核心原则
1. **Golden Path First** - 先做一条可跑通的真实链路，再扩展
2. **DoD 驱动** - 每个模块定义明确的"真实现"标准
3. **反空壳测试** - 用集成测试证明系统真正可工作

---

## Phase 1: 定义"真实现"的 DoD

### 目标
先终止"写了文件=实现完成"的幻觉。为每个关键模块定义明确的验收标准。

### 任务清单

- [ ] **1.1 GraphBuilder DoD**
  - [ ] 返回 `StateGraph` 对象，而非 dict
  - [ ] 定义 start / end 节点
  - [ ] 实现 edge / conditional edge
  - [ ] 至少一条 incident 流程可 `invoke()` 成功
  - [ ] 集成 LangGraph persistence / checkpoint

- [ ] **1.2 节点逻辑 DoD**
  - [ ] triage_node: 引入 LLM 调用或明确的 deterministic engine
  - [ ] planner_node: 基于 triage 结果动态生成任务
  - [ ] diagnose_node: 基于证据合成根因假设
  - [ ] critic_node: 真实证据评估逻辑
  - [ ] remediation_node: 基于诊断结果生成动作

- [ ] **1.3 Tool Gateway DoD**
  - [ ] Mock adapter 和 Real adapter 明确分层
  - [ ] runtime 可切换（环境变量控制）
  - [ ] 日志能显示本次调用的是 mock 还是 real
  - [ ] 至少 1 个真实 adapter 端到端打通

- [ ] **1.4 API 层 DoD**
  - [ ] `POST /incidents/runs` 触发 graph 执行
  - [ ] 异步任务调度（非阻塞）
  - [ ] 事件流推进（SSE 或 WebSocket）
  - [ ] 支持 interrupt / resume

- [ ] **1.5 Checkpoint/Approval DoD**
  - [ ] CheckpointService 与 LangGraph persistence 集成
  - [ ] 支持 human-in-the-loop interrupt
  - [ ] 支持 resume 后继续执行

---

## Phase 2: 重建主链路 (Golden Path)

### 目标
先只做一条最小但真实的 golden path，而非一次性补全所有模块。

### 目标链路
1. 创建 incident run
2. 进入 graph
3. intake
4. triage (真实 LLM 调用)
5. evidence retrieval (真实工具调用)
6. diagnose
7. remediation proposal
8. approval interrupt
9. resume
10. 输出 RCA / action result / audit trail

### 要求
- [ ] graph 真执行（不是 dict）
- [ ] 至少 1 次真实 LLM 调用
- [ ] 至少 1 次真实工具调用
- [ ] 至少 1 次 interrupt / resume
- [ ] 全链路有 trace / run log

### 任务清单

- [ ] **2.1 重构 GraphBuilder**
  - [ ] 使用 `langgraph.graph.StateGraph` 替代 dict
  - [ ] 定义 `IncidentAgentState` 作为 graph 的 state 类型
  - [ ] 实现 START → intake → triage → END 的最小链路
  - [ ] 添加 conditional edge 示例（severity 判断）

- [ ] **2.2 重构 API 触发机制**
  - [ ] 修改 `POST /incidents/runs` 触发 `graph.invoke()`
  - [ ] 添加异步任务队列（Celery / asyncio.create_task）
  - [ ] 实现 `GET /runs/{run_id}/status` 实时状态查询
  - [ ] 实现 SSE 事件流 `/runs/{run_id}/events/stream`

- [ ] **2.3 集成 LLM 调用**
  - [ ] 在 triage_node 中引入 LLM 调用
  - [ ] 定义 triage prompt template
  - [ ] 处理 LLM 失败回退逻辑

- [ ] **2.4 集成真实 Tool**
  - [ ] 选择一个工具作为真实 adapter 试点（如 query_logs）
  - [ ] 实现真实的日志查询（如调用 Loki、ES 或云服务）
  - [ ] 配置 mock/real 切换机制

- [ ] **2.5 实现 Interrupt/Resume**
  - [ ] 在 approval 节点使用 `interrupt()`
  - [ ] 实现 `/runs/{run_id}/approve` API
  - [ ] 实现 resume 后继续执行

---

## Phase 3: Mock 降级为正式测试资产

### 目标
把 mock 从"伪实现"降级为"正式测试资产"，明确区分 dev/demo/prod 行为。

### 任务清单

- [ ] **3.1 Adapter 分层架构**
  - [ ] 创建 `adapters/contracts/` - 统一接口与 schema
  - [ ] 创建 `adapters/mock/` - 测试/本地演示用
  - [ ] 创建 `adapters/real/` - 生产接入
  - [ ] 迁移现有 adapters 代码到 mock 目录

- [ ] **3.2 运行时 Adapter 选择**
  - [ ] 配置 `TOOL_ADAPTER_MODE` 环境变量（mock/real）
  - [ ] ToolGateway 初始化时根据环境加载对应 adapter
  - [ ] 启动时打印当前 adapter 类型和数据源

- [ ] **3.3 强制日志标注**
  - [ ] 每次 tool 调用记录 adapter 类型
  - [ ] 在 audit log 中标注 `adapter_mode: mock/real`
  - [ ] 在响应中包含 `X-Adapter-Mode` header

---

## Phase 4: 配置体系正规化

### 目标
遵循 Twelve-Factor App 原则，配置与代码彻底分离。

### 任务清单

- [ ] **4.1 配置分层**
  - [ ] 实现 `settings/base.py` - 基础配置
  - [ ] 实现 `settings/dev.py` - 开发环境
  - [ ] 实现 `settings/staging.py` - 预发布环境
  - [ ] 实现 `settings/prod.py` - 生产环境

- [ ] **4.2 环境变量迁移**
  - [ ] `OPENAI_API_KEY` - 必需，环境变量
  - [ ] `DATABASE_URL` - 必需，环境变量
  - [ ] `TOOL_ADAPTER_MODE` - mock/real
  - [ ] `LOG_LEVEL` - INFO/WARNING/ERROR
  - [ ] `CORS_ORIGINS` - 白名单
  - [ ] `LLM_MODEL`, `LLM_TIMEOUT`, `LLM_MAX_RETRIES`

- [ ] **4.3 Fail-Fast 校验**
  - [ ] prod 环境禁止 `CORS=*`
  - [ ] prod 环境禁止 mock executor
  - [ ] 缺 API key 启动失败
  - [ ] 缺 real adapter endpoint 降级并告警

- [ ] **4.4 文档**
  - [ ] 创建 `.env.example` 文件
  - [ ] 启动时打印非敏感配置摘要

---

## Phase 5: 补"反空壳测试"

### 目标
证明系统真正可工作，而非只有单元测试。

### 任务清单

- [ ] **5.1 Graph Contract Tests**
  - [ ] 测试图能构建
  - [ ] 测试节点可执行
  - [ ] 测试边能转移
  - [ ] 测试 interrupt/resume 生效

- [ ] **5.2 Tool Adapter Contract Tests**
  - [ ] 同一份输入，对 mock/real adapter 都跑契约校验
  - [ ] 验证返回 schema 一致

- [ ] **5.3 Golden-Path Integration Test**
  - [ ] 从创建 run 到输出 RCA 跑通一遍
  - [ ] 包含 1 次 LLM 调用
  - [ ] 包含 1 次真实 tool 调用
  - [ ] 包含 1 次 interrupt/resume

- [ ] **5.4 Smoke Test**
  - [ ] 配置加载正常
  - [ ] graph 真执行
  - [ ] trace 真上报

---

## Phase 6: 可观测性接入

### 目标
让 agent 系统可追踪，参考 OpenTelemetry 最佳实践。

### 任务清单

- [ ] **6.1 三层 ID 统一**
  - [ ] `run_id` - 贯穿整个 incident 生命周期
  - [ ] `graph_step_id` - 每个 graph 步骤
  - [ ] `tool_call_id` - 每次 tool 调用

- [ ] **6.2 Node 级别 Tracing**
  - [ ] 记录 node 名称
  - [ ] 记录输入摘要
  - [ ] 记录输出摘要
  - [ ] 记录 token/latency
  - [ ] 记录使用模型

- [ ] **6.3 Tool Call Auditing**
  - [ ] 记录 adapter 类型
  - [ ] 记录请求/响应
  - [ ] 记录异常信息

- [ ] **6.4 人工审批点追踪**
  - [ ] 记录审批等待点
  - [ ] 记录 resume 来源
  - [ ] 记录审批结果

- [ ] **6.5 OpenTelemetry 集成**
  - [ ] 集成 opentelemetry-sdk
  - [ ] 配置 trace exporter
  - [ ] 配置 log exporter

---

## Phase 7: 文档与实现对齐

### 目标
解决"文档写得像已经做完"的问题。

### 任务清单

- [ ] **7.1 文档分类**
  - [ ] `design/` - 设计意图
  - [ ] `implemented/` - 已落地能力
  - [ ] `gaps/` - 设计-实现差距清单

- [ ] **7.2 模块状态追踪**
  - [ ] 每个模块标注：planned / partial / production-ready
  - [ ] 每个模块提供证据：代码入口、测试、运行截图或日志
  - [ ] 每个模块列出未完成项

- [ ] **7.3 定期同步**
  - [ ] 每次发布前更新 gaps 清单
  - [ ] 代码变更必须更新对应文档状态

---

## 实施优先级

### P0 (立即开始)
1. Phase 1: 定义 GraphBuilder DoD
2. Phase 2: 重构 GraphBuilder 使用 StateGraph
3. Phase 2: API 触发 graph 执行

### P1 (Golden Path 完成后)
4. Phase 2: 集成 LLM 调用
5. Phase 3: Adapter 分层
6. Phase 4: 配置正规化

### P2 (后续迭代)
7. Phase 2: 真实 tool adapter
8. Phase 5: 反空壳测试
9. Phase 6: 可观测性
10. Phase 7: 文档对齐

---

## 验收标准

每个阶段完成后，必须满足：
1. 对应的 DoD 标准已达成
2. 有可运行的代码证明
3. 有测试证明功能工作
4. 文档已更新状态

---

## 依赖关系

```
Phase 1 (DoD)
    ↓
Phase 2 (Golden Path) ← Phase 3, Phase 4
    ↓
Phase 5, Phase 6, Phase 7 (可并行)
```

---

*创建时间: 2026-03-07*
*基于 review.md 分析生成*
