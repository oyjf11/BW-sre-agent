# OpsPilot 行动计划

> 生成时间: 2026-04-06 | 更新时间: 2026-04-08
> Phase 1-4 已完成，当前处于 Phase 5；Task 5.1、Task 5.1.5 与 Task 5.2 已完成。

---

## ✅ 已完成阶段（Phase 1-4，勿重复执行）

<details>
<summary>Phase 1: 前端核心体验补全 — ✅ 已完成（2026-04-06）</summary>

- **Task 1.1**: RunDetailPage 接入后端数据 + 已有组件（Stepper + Tabs + 证据/诊断/方案面板）
- **Task 1.2**: 修复 38 个前端失败测试
</details>

<details>
<summary>Phase 2: 后端 API 补全 — ✅ 已完成（2026-04-06）</summary>

- **Task 2.1**: 新增 `/runs/{run_id}/diagnosis` 和 `/runs/{run_id}/remediation` API 端点，从 checkpoint state_json 提取结构化数据
</details>

<details>
<summary>Phase 3: 端到端 Demo 可跑通 — ✅ 已完成（2026-04-06）</summary>

- **Task 3.1**: 全链路 Happy Path 验证通过（NEW → COMPLETED）
- **已修复 bug**: 审批 resume 逻辑——`prepare_resume_state` 原先加载 `node_approval_interrupt` 的 checkpoint（不在 `_RESUME_ALLOWED_NODES` 白名单），导致 dispatcher 回退到 `node_intake` 重跑全流程。修复为优先加载 `node_risk_gate` checkpoint。见 `backend/app/services/approval_runtime.py`。
</details>

<details>
<summary>Phase 4: 前端测试修复 — ✅ 已完成（2026-04-06）</summary>

- **Task 4.1**: RunDetailPage 新布局测试覆盖完成
</details>

---

## 当前待执行阶段

## Phase 5: 阿里云真实数据源接入（P1，预计 5-7 天）

> **架构说明**：真实适配器分三类，不要混淆：
> 1. **业务 DB 诊断工具（新增）**：连接线上业务 MySQL（hoo_ai），提供数据库层面的诊断证据（慢查询、连接数、锁等待等）。这些是 evidence_fanout 阶段的**新工具**，与现有 mock 工具并列。→ Task 5.1
> 2. **应用日志查询（替换 query_logs mock）**：线上 SLS 已关停，改为 Yii 应用日志写入 MySQL `common_app_log` 表，OpsPilot 的 `query_logs` 适配器直接查这张表。→ Task 5.1.5
> 3. **替换其他 mock 工具**：`query_metrics` → Prometheus/ARMS，`query_deployments` → CI/CD API，K8s/SLB → 阿里云 API。→ Task 5.2~5.4
>
> **前置依赖**：Task 5.1.5 依赖 admin-sys 侧先完成日志写入改造（建表 + Yii DbTarget 配置）。改造方案见 `admin-sys/ACTION_PLAN_LOG_TO_MYSQL.md`。
>
> 线上业务数据库里没有工单/告警/部署表（那些数据在 OpsPilot 自身的 SQLite 或外部监控系统中）。

### Task 5.1: MySQL 业务数据库诊断适配器（只读） — ✅ 已完成（2026-04-08）

**目标**: 新增业务 MySQL 诊断工具，在 evidence_fanout 阶段从线上数据库采集 DB 层面的故障证据

**上下文**:
- 线上业务数据库是阿里云 RDS MySQL（如 hoo_ai，CRM/教育管理系统，约 400 张表）
- 该库**不包含**工单、告警、部署记录等 SRE 数据——那些在 OpsPilot 自身 SQLite 或外部系统中
- MySQL 适配器的价值：故障排查时从 DB 层面取证（是不是慢查询导致的？连接池打满了？有锁等待？）
- Tool Gateway 已支持 adapter 注册（`backend/app/tools/gateway.py`）
- 需要在 `backend/app/tools/adapters/` 下新增适配器
- **安全要求**：只读账号，参数化查询，禁止拼接 SQL，查询结果截断

**步骤**:
1. 创建 `backend/app/tools/clients/mysql_client.py`：
   - 使用 pymysql 连接池（`pymysql.cursors.DictCursor`）
   - **只读账号**，参数化查询（禁止拼接 SQL）
   - 从环境变量读取连接信息：`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
   - 连接超时 5s，查询超时 10s
   - **注意**：阿里云 RDS 需要将客户端 IP 加入白名单才能连接

2. 创建 `backend/app/tools/adapters/mysql_adapter.py`，实现 4 个诊断工具函数：
   - `query_db_processlist(params)` — 查活跃连接、锁等待（`SHOW PROCESSLIST`，过滤 Sleep 状态）
   - `query_db_slow_queries(params)` — 查慢查询（`SHOW FULL PROCESSLIST` 中 Time > 阈值的，或查 `information_schema` 相关表）
   - `query_db_table_status(params)` — 查表状态（行数、大小、碎片）（`SHOW TABLE STATUS`，结果截断 top 20）
   - `query_db_variables(params)` — 查关键数据库状态变量（连接数、缓冲池命中率、锁等待计数等）（`SHOW GLOBAL STATUS` 过滤关键指标）
   - 每个函数返回 `dict`，格式与现有 mock adapter 一致（含 `_adapter_info` 字段）
   - 查询结果必须截断，`response_size_limit_kb: 64`

3. 在 `backend/app/tools/adapters/__init__.py` 新增对应的 mock 版本（返回仿真数据），确保 mock 模式下不依赖真实 MySQL 连接

4. 在 Tool Gateway 中注册 4 个新工具：
   - mock 模式：使用 mock 函数（步骤 3）
   - real 模式：使用真实 MySQL 适配器（步骤 2）
   - 在 `select_adapter()` 中添加对应路由

5. 在 `backend/app/graph/nodes/__init__.py` 的 `evidence_fanout` 节点中，将 MySQL 诊断工具加入可选的调查任务类别（当 planner 判断需要 DB 层面证据时触发）

**验收**:
- 设置 `TOOL_ADAPTER_MODE=mock`（默认），4 个新工具返回仿真数据，不需要真实 MySQL 连接
- 设置 `TOOL_ADAPTER_MODE=real`，`query_db_processlist` 能返回真实活跃连接列表
- 参数不合法时返回错误而不是执行 SQL
- 查询结果 < 64KB
- 新工具不影响现有 10 个 mock 工具的正常运行

**完成说明**:
- 已实现 `mysql_client.py`、4 个 `query_db_*` 真实适配器和对应 mock 适配器
- 已在 `gateway.py` 中注册 4 个新工具，并补齐 mock/real 路由
- 已在 `planner_node` 中加入 DB 诊断任务生成逻辑，`evidence_fanout` 可直接并行调度
- 已在 `ToolGateway` 增加基础参数校验，非法参数会在入口返回错误，不会继续执行工具
- 已补充并通过后端测试：`test_mysql_adapter.py`、`test_tool_gateway.py`、`test_mysql_planning.py`
- 备注：真实 RDS 联调仍依赖环境白名单与线上凭据，本地已完成代码与测试闭环

### Task 5.1.5: 应用日志适配器（替换 query_logs mock） — ✅ 已完成（2026-04-08）

**目标**: 用真实应用日志替换现有 `query_logs` 的 mock 适配器，数据源为业务 MySQL 的 `common_app_log` 表

**前置条件**:
- admin-sys 侧已完成改造：建表 `common_app_log` + Yii DbTarget 配置（方案见 `admin-sys/ACTION_PLAN_LOG_TO_MYSQL.md`）
- 表中已有日志数据（部署后自动写入）

**上下文**:
- 线上 SLS 已关停省钱，应用日志改为写入业务 MySQL `common_app_log` 表
- 表结构：`id, level(int), category(varchar), log_time(double), prefix(varchar), message(text), created_at(datetime)`
- `level` 含义：1=error, 2=warning, 4=info（Yii Logger 常量）
- 该表与 Task 5.1 的 MySQL 诊断工具共用同一个 MySQL 连接（`mysql_client.py`）
- 现有 mock `query_logs` 的接口签名：`query_logs(service, env, time_range, query, limit) -> {logs, count, query}`

**步骤**:
1. 在 `backend/app/tools/adapters/mysql_adapter.py` 中新增 `query_logs_from_db` 函数：
   - 复用 Task 5.1 创建的 `mysql_client.py` 连接池
   - 将 `service`/`env` 映射为 `category` 的 LIKE 查询（如 `category LIKE '%payment-service%'`）
   - 将 `time_range` 映射为 `created_at` 的范围查询
   - 将 `query` 映射为 `message` 的 LIKE 查询（如果 query != '*'）
   - `level` 字段映射：1 → 'ERROR', 2 → 'WARNING', 4 → 'INFO'
   - 结果 limit 上限 200 条，返回格式与现有 mock 一致：
     ```json
     {
       "logs": [
         {"timestamp": "...", "level": "ERROR", "message": "...", "source": "category值"}
       ],
       "count": 10,
       "query": "原始query参数"
     }
     ```
   - 参数化查询，禁止 SQL 拼接

2. 在 `gateway.py` 的 `select_adapter()` 中，为 `query_logs` 添加 real 路由，指向 `query_logs_from_db`

**验收**:
- `TOOL_ADAPTER_MODE=mock`：`query_logs` 行为不变（返回仿真数据）
- `TOOL_ADAPTER_MODE=real`：`query_logs(service="crm-service", env="prod")` 返回 `common_app_log` 表中的真实日志
- `query="Lock wait timeout"` 能过滤出包含该关键词的日志
- 结果 ≤ 200 条，格式与 mock 一致
- SQL 注入测试：`query="'; DROP TABLE--"` 不执行破坏性操作

**完成说明**:
- 已实现 `query_logs_from_db`，复用 `mysql_client.py` 查询 `common_app_log`
- 已补齐 `service/env -> category LIKE` 的安全过滤，并保留 `time_range` / `message` 关键字过滤
- 已在 `gateway.py` 中将 `query_logs` 的 real 模式路由到该实现
- 已补充并通过后端测试：`backend/app/tests/test_mysql_adapter.py`

---

### Task 5.2: K8s 适配器（只读，替换现有 mock） — ✅ 已完成（2026-04-08）

**目标**: 用真实 K8s 数据替换现有 mock 的 `query_k8s_deployment_status`，并新增 pod/events/日志诊断工具

**上下文**:
- 现有 mock 已有 `query_k8s_deployment_status`（在 `adapters/__init__.py`），本任务是将其替换为真实实现
- 同时新增 3 个诊断工具（pods/events/logs），丰富 K8s 层面的证据采集能力

**步骤**:
1. 创建 `backend/app/tools/clients/k8s_client.py`：
   - 使用 `kubernetes` Python SDK
   - 从 kubeconfig 或 service account 加载配置
   - 只允许白名单 namespace 查询（从配置读取 `K8S_ALLOWED_NAMESPACES`）

2. 创建 `backend/app/tools/adapters/k8s_adapter.py`，实现 4 个工具函数：
   - `query_k8s_deployment_status(params)` — **替换现有 mock**，查 deployment 副本状态
   - `query_k8s_pods(params)` — **新增**，查指定 namespace/deployment 的 pod 状态
   - `query_k8s_events(params)` — **新增**，查指定 namespace 的 events（聚合 top reason）
   - `query_k8s_pod_logs_summary(params)` — **新增**，查 pod 日志摘要（tail 100 行 + 提取 top error patterns）
   - 强制限制 namespace 白名单
   - 日志必须截断，`response_size_limit_kb: 128`

3. 在 `adapters/__init__.py` 中为 3 个新工具添加 mock 版本
4. 在 Tool Gateway 中注册新工具 + 在 `select_adapter()` 中为 `query_k8s_deployment_status` 添加 real 路由

**验收**:
- `query_k8s_pods({"namespace": "default", "service": "payment-service"})` 返回真实 pod 列表
- 查询非白名单 namespace 被拒绝
- pod_logs_summary 结果 < 128KB
- mock 模式下所有工具正常返回仿真数据

**完成说明**:
- 已实现 `k8s_client.py`，支持 lazy 加载 kube config，优先 in-cluster，再 fallback 到 kubeconfig
- 已新增 `query_k8s_pods`、`query_k8s_events`、`query_k8s_pod_logs_summary`，并将 `query_k8s_deployment_status` 接到 real 路由
- 已增加 `K8S_ALLOWED_NAMESPACES` fail-closed 配置，未配置时拒绝所有真实查询
- 已在 planner 中接入 K8s 证据任务生成，resource/dependency/deployment 类故障可自动调度 K8s 工具
- 已修复 `deployment_healthy` 预检逻辑，现会校验部署状态而不只是看 tool 是否调用成功
- 已补充并通过后端测试：`test_k8s_adapter.py`、`test_tool_gateway.py`、`test_mysql_planning.py`、`test_executor_preconditions.py`
- 备注：真实集群联调仍依赖 kubeconfig / service account 与 namespace 白名单配置

### Task 5.3: SLB 适配器（只读，替换现有 mock）

**目标**: 用真实阿里云 SLB 数据替换现有 mock 的 `query_lb_health_status` 和 `query_lb_traffic_metrics`

**上下文**:
- 现有 mock 已有 `query_lb_health_status` 和 `query_lb_traffic_metrics`（在 `adapters/__init__.py`）
- 本任务是将其替换为真实的阿里云 SLB API 实现，接口签名保持不变

**步骤**:
1. 创建 `backend/app/tools/clients/slb_client.py`：
   - 使用阿里云 SDK（`alibabacloud-slb20140515`）
   - 从环境变量读取 `ALIBABA_ACCESS_KEY_ID`, `ALIBABA_ACCESS_KEY_SECRET`, `ALIBABA_REGION_ID`

2. 创建 `backend/app/tools/adapters/slb_adapter.py`，实现 2 个工具函数：
   - `query_lb_health_status(params)` — **替换现有 mock**，查后端实例健康状态
   - `query_lb_traffic_metrics(params)` — **替换现有 mock**，查 5xx/QPS/延迟趋势

3. 在 `select_adapter()` 中添加 real 路由（mock 版本已存在，无需新增）

**验收**:
- real 模式下能返回真实 SLB 健康状态和流量指标
- mock 模式下行为与之前一致（无需改动）

### Task 5.4: OSS 适配器（写归档）

**目标**: RCA 报告和证据包归档到 OSS

**步骤**:
1. 创建 `backend/app/tools/clients/oss_client.py`：
   - 使用 `oss2` SDK
   - 只允许写入 `rca/` 和 `evidence/` 前缀（硬编码白名单）

2. 创建 `backend/app/tools/adapters/oss_adapter.py`，实现 2 个工具函数：
   - `write_rca_report_to_oss(params)` — 将 RCA markdown 写入 OSS
   - `write_evidence_bundle_to_oss(params)` — 将证据包 JSON 写入 OSS

3. 在 rca_node 中调用 OSS 写入

**验收**:
- RCA 报告在 OSS 对应 bucket 中可查到
- 非 `rca/` / `evidence/` 前缀的写入被拒绝

---

## Phase 6: RAG 知识检索与写回（P1，预计 3-4 天）

### Task 6.1: 知识库索引与检索

**目标**: planner/diagnose 节点能检索历史 RCA 和 Runbook

**步骤**:
1. 安装 `chromadb`（或 `pgvector`），在 `backend/requirements.txt` 添加依赖

2. 实现 `backend/app/rag/indexer.py`：
   - 从 DB 读取已确认的 RCA 报告（`confirmed_by_human=True`）
   - 切分文档（按段落或固定 chunk size 512）
   - 存入 Chroma collection，metadata 含 service/env/incident_type/severity

3. 实现 `backend/app/rag/retriever.py`：
   - `retrieve(query: str, filters: dict, top_k: int = 5) -> List[EvidenceItem]`
   - 支持 metadata filter（service/env/doc_type）
   - 返回格式与 EvidenceItem 一致（category="history"）

4. 实现 `backend/app/rag/writer.py`：
   - `write_back(run_id: str)` — 将已确认 RCA 写入向量库
   - 只写入 `confirmed_by_human=True` 的报告

5. 在 `graph/nodes/retrieve_memory.py` 中调用 retriever，将结果加入 state.evidence_items

6. 在 `graph/nodes/writeback_knowledge.py` 中调用 writer

**验收**:
- 提交一条工单后，如果有历史同类 RCA，evidence 中出现 category="history" 的条目
- 手工确认 RCA 后，下次同类工单能检索到

---

## Phase 7: 可观测性接入（P1，预计 1-2 天）

### Task 7.1: Tracing 集成

**目标**: 每次 run 的执行路径可在 LangSmith 或 Langfuse 中回放

**步骤**:
1. 检查 `backend/app/tracing.py` 现有实现
2. 选择 LangSmith 或 Langfuse：
   - LangSmith: 设置 `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY`
   - Langfuse: `pip install langfuse` + 配置 `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`
3. 确保 graph_runner 和 tool gateway 的调用都被 trace 捕获
4. 在 RunDetailPage 右侧边栏添加 "View Trace" 外链（如果配置了 tracing）

**验收**:
- 运行一条工单后，在 LangSmith/Langfuse 控制台能看到完整 trace
- 包含每个节点的 input/output、LLM 调用、tool 调用

---

## Phase 8: 离线评测（P2，预计 2-3 天）

### Task 8.1: 评测框架搭建

**目标**: 一键回放测试案例，输出命中率等指标

**步骤**:
1. 在 `backend/app/evals/datasets/` 创建 10-20 个测试案例 JSON：
   ```json
   {
     "case_id": "case_001",
     "ticket": { "description": "...", "service": "payment-service", ... },
     "expected_root_cause": "deployment_regression",
     "expected_risk_level": "HIGH",
     "tool_fixtures": {
       "query_logs": { "返回的 mock 数据" },
       "query_metrics": { "返回的 mock 数据" }
     }
   }
   ```

2. 实现 `backend/app/evals/replay_runner.py`：
   - 读取 dataset，用 fixture 替换 tool gateway 的真实调用
   - 运行 graph，收集 root_cause_candidates 和 remediation_plan
   - 与 expected 对比

3. 实现 `backend/app/evals/metrics.py`：
   - Top1/Top3 根因命中率
   - 风险等级判断准确率
   - 平均步骤数/延迟/token 消耗

4. 添加 CLI 入口：`python -m app.evals.replay_runner --dataset datasets/ --output report.json`

**验收**:
- 运行命令输出 JSON 格式的评测报告
- 报告包含命中率、平均步骤数等指标

---

## 执行顺序总结

```
Phase 1-4                  ── ✅ 已完成（2026-04-06）

Phase 5 执行顺序:
  Task 5.1  (MySQL 诊断工具)     ── ✅ 已完成（2026-04-08）
  Task 5.1.5(应用日志 query_logs) ── ✅ 已完成（2026-04-08）
  Task 5.2  (K8s 适配器)         ── ✅ 已完成（2026-04-08）
  Task 5.3  (SLB 适配器)         ─┤── 互相独立，可并行
  Task 5.4  (OSS 适配器)         ─┘

Phase 6 (Task 6.1)          ─┐
Phase 7 (Task 7.1)          ─┤── 与 Phase 5 后半段并行
                             ─┘

Phase 8 (Task 8.1)         ── 最后，2-3 天
```

**跨仓库依赖**: Task 5.1.5 需要 admin-sys 先部署日志写入改造（见 `admin-sys/ACTION_PLAN_LOG_TO_MYSQL.md`）
**注意**: Task 5.1 是新增 MySQL 诊断工具，Task 5.1.5 是替换 query_logs mock，5.2/5.3 是替换 K8s/SLB mock
