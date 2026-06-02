# OpsPilot 行动计划

> 生成时间: 2026-04-06 | 更新时间: 2026-06-01
> Phase 1-7 已全部完成（含 LangSmith 真实控制台验证通过）；Phase 8 启动前 real adapter 收口已完成；LLM 已切换至 DeepSeek，具体模型由 `DEEPSEEK_MODEL` 配置；Phase 8 离线评测尚未启动。

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

## 阶段进度明细

## Phase 5: 阿里云真实数据源接入（P1，预计 5-7 天） — ✅ 已完成（2026-05-28）

> **架构说明**：真实适配器分三类，不要混淆：
> 1. **业务 DB 诊断工具（新增）**：连接线上业务 MySQL（hoo_ai），提供数据库层面的诊断证据（慢查询、连接数、锁等待等）。这些是 evidence_fanout 阶段的**新工具**，与现有 mock 工具并列。→ Task 5.1
> 2. **应用日志查询（替换 query_logs mock）**：线上 SLS 已关停，改为 Yii 应用日志写入 MySQL `common_app_log` 表，OpsPilot 的 `query_logs` 适配器直接查这张表。→ Task 5.1.5
> 3. **替换其他 mock 工具**：`query_metrics` → 阿里云 CMS/K8s 指标，`query_deployments` → K8s deployment 列表与状态，K8s/SLB → Kubernetes / 阿里云 API。→ Task 5.2~5.4
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

### Task 5.3: SLB 适配器（只读，替换现有 mock） — ✅ 已完成（2026-05-11）

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

**完成说明**:
- 已实现 `slb_client.py`，封装 `DescribeLoadBalancers` / `DescribeHealthStatus` / `DescribeLoadBalancerAttribute` API，集成 CMS `DescribeMetricData` 获取 QPS/延迟/5xx 真实指标
- 已实现 `slb_adapter.py`，通过 tag（Service+Env）或 loadBalancerName 模糊匹配定位 SLB 实例
- 已在 `gateway.py` 的 `select_adapter()` 中注册 real 路由
- 已在 `config.py` 中新增 `ALIBABA_ACCESS_KEY_ID` / `ALIBABA_ACCESS_KEY_SECRET` / `ALIBABA_REGION_ID` 配置项
- 已在 `requirements.txt` 中新增 `alibabacloud-slb20140515` / `alibabacloud-tea-openapi` / `alibabacloud-cms20190101` 依赖
- 已补充并通过后端测试：`test_slb_adapter.py`（mock + real 路由 + CMS datapoints 解析全覆盖）
- `verify_outcome_node` 对 `metrics_available=false` 降级为不通过，避免假阳性
- CMS endpoint 按 `ALIBABA_REGION_ID` 构造，与 SLB endpoint 保持一致
- 备注：真实 SLB + CMS 联调依赖阿里云 AK/SK 与 region 配置

### Task 5.4: OSS 适配器（写归档） — ✅ 已完成（2026-05-28）

**目标**: RCA 报告和证据包归档到 OSS

**步骤**:
1. 创建 `backend/app/tools/clients/oss_client.py`：
   - 使用 `oss2` SDK
   - 只允许写入 `rca/` 和 `evidence/` 前缀（硬编码白名单）

2. 创建 `backend/app/tools/adapters/oss_adapter.py`，实现 2 个工具函数：
   - `write_rca_to_oss(params)` — 将 RCA markdown 写入 OSS
   - `write_evidence_to_oss(params)` — 将证据包 JSON 写入 OSS

3. 在 rca_node 中调用 OSS 写入

**验收**:
- RCA 报告在 OSS 对应 bucket 中可查到
- 非 `rca/` / `evidence/` 前缀的写入被拒绝

**完成说明**:
- 已实现 `oss_client.py`，复用阿里云 AK/SK 配置，新增 `ALIBABA_OSS_BUCKET` / `ALIBABA_OSS_ENDPOINT`，并强制只允许写入 `rca/` 与 `evidence/` 前缀
- 已实现 `oss_adapter.py`，提供 `write_rca_to_oss` 和 `write_evidence_to_oss` 两个异步工具函数
- 已在 `adapters/__init__.py` 中补齐 mock OSS 写入函数
- 已在 `gateway.py` 中注册 OSS 工具元数据，并在 real 模式下路由到真实 OSS adapter
- 已在 `rca_node` 中 best-effort 写入 RCA markdown 和 evidence bundle，OSS 失败不阻塞主故障处置流程
- 已补充并通过后端测试：`PYTHONPATH=. pytest app/tests/test_oss_adapter.py -q`（16 passed）
- 备注：真实 OSS 联调依赖 `ALIBABA_ACCESS_KEY_ID` / `ALIBABA_ACCESS_KEY_SECRET` / `ALIBABA_OSS_BUCKET` / `ALIBABA_OSS_ENDPOINT`

---

## Phase 6: RAG 知识检索与写回（P1，预计 3-4 天） — ✅ 已完成（2026-05-28）

### Task 6.1: 知识库索引与检索 — ✅ 已完成（2026-05-28）

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

**完成说明**:
- 已新增 `backend/app/rag/schemas.py`，定义 `KnowledgeDocument`、`RetrievedChunk`、`IndexingResult`
- 已新增 `backend/app/rag/embeddings.py`，提供 BGE embedding lazy factory，默认模型为 `BAAI/bge-small-zh-v1.5`
- 已新增 `backend/app/rag/store.py`，使用 ChromaDB `PersistentClient` + LlamaIndex `ChromaVectorStore` / `VectorStoreIndex`
- 已新增 `backend/app/rag/indexer.py`，使用 `SimpleDirectoryReader` 读取本地 Runbook，使用 `SentenceSplitter` 切分，并支持批量索引 DB 中 `confirmed_by_human=1` 的 RCA
- 已新增 `backend/app/rag/retriever.py` 与 `backend/app/rag/reranker.py`，支持 LlamaIndex semantic retrieval、metadata filter、可选 BGE CrossEncoder rerank、以及转换为 `category="history"` 的 `EvidenceItem`
- 已新增 `backend/app/rag/writer.py`，人工确认 RCA 后可增量写回知识库
- 已在 `retrieve_memory_node` 中接入 RAG，检索命中会同时写入 `memory_hits` 和 `evidence_items`
- 已在 `KnowledgeWritebackService._do_writeback()` 中接入 `write_back_confirmed_rca(...)`
- 已补充并通过后端测试：`test_rag_embeddings.py`、`test_rag_indexer.py`、`test_rag_retriever.py`、`test_rag_writer.py`、`test_retrieve_memory_rag.py`
- 验证命令：`/Users/ouyangjinfeng/miniconda3/bin/python -m pytest app/tests/test_rag_embeddings.py app/tests/test_rag_retriever.py app/tests/test_rag_indexer.py app/tests/test_rag_writer.py app/tests/test_retrieve_memory_rag.py -q`（14 passed）
- 全量验证命令：`/Users/ouyangjinfeng/miniconda3/bin/python -m pytest app/tests/ -x -q`（155 passed）
- 备注：RAG 生产代码中已移除 `InMemoryKnowledgeStore` / `JsonKnowledgeStore` 替身；测试只在边界处 monkeypatch LlamaIndex 调用，避免下载真实模型但不替代生产实现

---

## Phase 7: 可观测性接入（P1，预计 1-2 天） — ✅ 已完成，LangSmith 真实验证通过

### Task 7.1: Tracing 集成

**目标**: 每次 run 的执行路径可在 LangSmith 或 Langfuse 中回放

**当前进度（2026-05-31）**:
- 已完成本地 tracing 基础闭环：
  - `backend/app/tracing.py` 已支持 span / event 记录与 run 级上下文
  - `GraphRunner`、`ToolGateway`、`LLMClient` 已接入关键 span 埋点
  - 新增 `GET /incidents/runs/{run_id}/trace`
  - `RunDetailPage` 已增加 `View Trace` 快捷入口
- 已完成外部 provider 代码接入 + 真实验证：
  - 新增 `backend/app/tracing_providers.py`（含 `LangfuseTraceProvider`、`LangSmithTraceProvider`、工厂函数）
  - 新增 `backend/app/tests/test_tracing_providers.py`（9 个测试全部通过）
  - `backend/app/core/config.py` 增加 langsmith/langfuse 配置字段 + production 校验
  - `backend/requirements.txt` 已安装 langsmith/langfuse SDK
  - API 返回 `external_trace_id`、`external_root_span_id`、`external_trace_url`
  - FastAPI shutdown 会 flush provider
  - 前端 View Trace 链结优先使用 `external_trace_url`
  - **LangSmith 真实控制台验证通过**：创建工单后 trace 上报成功，trace URL 包含正确 org/project ID，可在控制台查看 graph.run、node.*、tool.*、llm.* span
  - URL 格式：`https://smith.langchain.com/o/{org_id}/projects/p/{project_id}/r/{run_id}`
  - LLM 已切换至 DeepSeek（`LLM_PROVIDER=deepseek`，具体模型由 `DEEPSEEK_MODEL` 配置）
- 后续待做：
  - Langfuse 真实环境验证（代码已就绪，配置即用）
  - 详见 `docs/superpowers/plans/2026-05-30-external-tracing-provider.md`

---

## Phase 8 启动前收口 — ✅ 已完成（2026-06-01）

**目标**: 在进入离线评测前，收紧 real adapter 边界，避免真实模式静默回退到 mock 数据或生成伪工单。

**完成说明**:
- `ToolGateway` 的 adapter 模式统一从 `Settings.tool_adapter_mode` 读取；`TOOL_ADAPTER_MODE=real` 时，未配置真实 adapter 的工具不再回退 mock。
- `query_ticket_by_id`、`query_service_metadata`、`query_runbook`、`execute_action` 的 real 路由已显式 fail-closed，需接入真实平台后才能使用。
- ticket ID 拉取失败时不再生成 synthetic ticket；`service_exists` 预检会同时校验工具调用是否成功和服务是否真实存在。
- `MySQLClient` 统一从 `Settings` 读取连接配置；MySQL 真实适配器不再吞掉连接或查询异常，由 gateway 返回失败。
- `RAG_ENABLED=false` 时检索直接返回空结果，不再初始化向量索引。
- RCA 人工确认后的归档路径已从 synthetic path 改为通过 `write_rca_to_oss` gateway 调用。
- `backend/.env.example` 已同步 DeepSeek、RAG、tracing、CMS/K8s 和 real adapter 示例配置。

**验证**:
- 后端：`cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q`（166 passed）
- 前端：`cd frontend && npx vitest run`（22 个测试文件，145 passed）

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

## Phase 9: 大厂 Agent 岗位短板补齐（P1，预计 5-8 天）

> 来源：`jobs/agent开发大厂面试标准调研.md` 的“短板也明显”章节。
> 当前项目已经覆盖 Workflow Agent、Tool Use、审批、checkpoint、SSE、Mock/Real Adapter。
> 本阶段重点补齐：完整 RAG 链路、hybrid search、rerank、RAG/Agent 评测、业务场景迁移表达、推荐/预测/NLP 算法模块。

### Task 9.1: RAG 增强为可评测知识库链路（基于 Phase 6 扩展）

**目标**: 将 Phase 6 的基础向量检索升级为“可解释、可评测、可调优”的生产 RAG 链路，覆盖向量检索、关键词检索、hybrid search、rerank、引用与召回评估。

**上下文**:
- Phase 6.1 已规划 Chroma/pgvector 基础索引与检索，本任务在其上扩展，不重复实现基础 writer/retriever。
- 面试标准明确要求不能只说“把文档放进向量库”，需要讲清楚 chunk、embedding、索引、召回、重排、引用、评测。
- SRE 场景的 RAG 数据源优先使用 RCA、Runbook、故障复盘、告警处理 SOP；暂不引入外部知识库平台。

**步骤**:
1. 扩展 `backend/app/rag/indexer.py`：
   - 为每个 chunk 写入 `doc_id`, `chunk_id`, `doc_type`, `service`, `env`, `incident_type`, `severity`, `source_url`, `created_at`
   - chunk 策略支持 `paragraph` 和 `token_window` 两种模式，默认 `token_window`，窗口 512 tokens，overlap 80 tokens
   - 保存 chunk 原文摘要，便于前端展示引用

2. 新增 `backend/app/rag/keyword_index.py`：
   - 使用 SQLite FTS5 或轻量 BM25 实现关键词检索
   - 查询入参：`query`, `filters`, `top_k`
   - 返回统一 `RetrievedDocument` 结构，字段包含 `score`, `retrieval_source="keyword"`

3. 扩展 `backend/app/rag/retriever.py`：
   - 增加 `retrieval_mode`: `vector | keyword | hybrid`
   - `hybrid` 模式同时取向量 top_k 与关键词 top_k，按 RRF（Reciprocal Rank Fusion）合并
   - 输出每条 evidence 的 `citations`，包含 `doc_id`, `chunk_id`, `score`, `source_url`

4. 新增 `backend/app/rag/reranker.py`：
   - 默认实现为规则 rerank：service/env/incident_type 精确匹配加权，标题命中加权，过期文档降权
   - 预留 LLM rerank 接口，但默认不开启，避免引入额外成本和不稳定性

5. 新增 `backend/app/rag/eval.py`：
   - 读取 `backend/app/rag/eval_datasets/*.json`
   - 指标：Recall@3、Recall@5、MRR、Citation Coverage、No-Answer Precision
   - CLI：`python -m app.rag.eval --dataset backend/app/rag/eval_datasets/sre_rag.json`

6. 在 `RunDetailPage` 的 Evidence Tab 中展示历史知识引用：
   - 展示标题、doc_type、score、source_url
   - citation 缺失时不展示空链接

**验收**:
- 同一条查询在 `vector`、`keyword`、`hybrid` 三种模式下均可返回结构化结果
- `hybrid` 模式输出包含 RRF 合并后的 score 和 citations
- RAG eval CLI 输出 Recall@3、Recall@5、MRR、Citation Coverage
- Evidence Tab 能看到历史 RCA/Runbook 的引用来源
- mock 环境无需外部向量服务即可跑通单元测试

### Task 9.2: Prompt / Agent 版本管理与回放对比

**目标**: 补齐 Prompt 版本管理和 Agent 改动回放能力，回答“Prompt 改了怎么判断变好还是变坏”。

**步骤**:
1. 新增 `backend/app/prompts/registry.py`：
   - 集中管理 planner、diagnose、critic、remediation、rca 等节点的 system prompt
   - 每个 prompt 带 `prompt_id`, `version`, `checksum`, `description`

2. 在 graph state 或 run metadata 中记录：
   - 每个节点实际使用的 `prompt_id/version/checksum`
   - LLM provider、model、temperature、token usage（如果 provider 返回）

3. 扩展 Phase 8 的 `backend/app/evals/replay_runner.py`：
   - 支持 `--prompt-version old,new` 对比回放
   - 输出每个版本的根因命中率、风险等级准确率、平均 token、平均耗时

4. 在 `backend/app/evals/reports/` 输出 Markdown 报告：
   - 列出 improved/regressed/unchanged case
   - 对 regressed case 保留诊断摘要和工具调用路径

**验收**:
- 任意 run 能追溯每个关键节点使用的 prompt 版本
- 同一评测集可对比两个 prompt 版本的指标差异
- 回放报告能明确列出回归 case

### Task 9.3: 泛业务场景迁移 Demo（电商/跨境/供应链表达补齐）

**目标**: 不改变 OpsPilot 的 SRE 主线，但新增“业务场景迁移包”，证明当前 Workflow Agent 架构可以迁移到电商客服、跨境履约、库存补货等大厂常见业务。

**上下文**:
- 调研短板指出项目不是电商/跨境/供应链业务场景。
- 不建议把主系统硬改成电商系统；更稳妥的做法是沉淀可配置 Scenario Profile，让同一套 intake/planner/tool/risk/eval 思路可迁移。

**步骤**:
1. 新增 `backend/app/scenarios/profiles.py`：
   - 定义 `ScenarioProfile`：`scenario_id`, `domain`, `intake_schema`, `tool_catalog`, `risk_rules`, `success_metrics`
   - 内置 `sre_incident`, `ecommerce_customer_service`, `cross_border_fulfillment`, `inventory_replenishment` 四个 profile

2. 新增 `backend/app/scenarios/examples/*.json`：
   - 每个业务场景提供 2 个样例任务
   - 样例包含输入、可用工具、风险边界、期望输出

3. 新增 `backend/app/scenarios/mapper.py`：
   - 将非 SRE 场景映射到统一 Agent 概念：intake、planning、tool evidence、decision、risk gate、human approval、verification
   - 输出面试可展示的结构化 Mermaid / Markdown 说明

4. 新增文档 `docs/interview/scenario-migration.md`：
   - 说明 OpsPilot 架构如何迁移到电商客服、跨境履约、库存补货
   - 每个场景列出业务目标、数据源、工具接口、风险边界、人工审核、评估指标

**验收**:
- `python -m app.scenarios.mapper --scenario ecommerce_customer_service` 能输出完整迁移说明
- 文档能直接支撑面试表述，不需要口头临场补齐
- 不影响现有 SRE run 创建、审批、执行 API

### Task 9.4: 轻量推荐 / 预测 / NLP 算法模块

**目标**: 补齐“推荐 / 预测 / NLP 算法模块”短板，用 SRE 业务内生算法能力展示，而不是生造无关电商推荐系统。

**步骤**:
1. 新增 `backend/app/analytics/incident_features.py`：
   - 从历史 runs/events/evidence 中抽取特征：service、env、severity、incident_type、tool_failures、duration、approval_required、root_cause
   - 输出 pandas DataFrame 或纯 Python list[dict]，优先保持轻依赖

2. 新增 `backend/app/analytics/similarity.py`：
   - 实现相似故障推荐：基于 service/env/severity/root_cause/evidence keywords 的加权相似度
   - 输出 top_k 历史 run，作为 planner/diagnose 的候选参考

3. 新增 `backend/app/analytics/risk_prediction.py`：
   - 实现规则 + 简单统计模型的风险预测
   - 输入当前 run 特征，输出 `predicted_escalation_risk`, `confidence`, `top_factors`
   - 默认不依赖训练服务；有足够历史数据后再切换 sklearn baseline

4. 新增 `backend/app/analytics/nlp.py`：
   - 从工单 title/description 中抽取 service、symptom、metric、time_range、suspected_change
   - 作为 intake/triage 的辅助信息，不替代现有 schema 校验

5. 在 diagnose 或 planner 节点中接入：
   - 相似故障推荐写入 `evidence_items`，category=`historical_similarity`
   - 风险预测写入 state，供 `risk_gate` 参考

**验收**:
- 有历史 run 时，新工单能返回 top_k 相似故障
- 风险预测输出可解释 top_factors
- NLP 抽取失败不影响 graph 主流程
- 单元测试覆盖空历史、低相似度、多服务混合、中文工单描述

---

## Phase 10: 大规模生产工程能力展示（P1，预计 4-6 天）

> 对应调研短板：缺少消息队列、缓存、分布式任务调度等大规模生产能力展示。
> 目标不是过度工程化，而是把长任务执行从“单进程可跑”推进到“可水平扩展、可观测、可恢复”的架构。

### Task 10.1: Redis 缓存与分布式锁

**目标**: 为 run 状态、审批 pending 列表、RAG 检索结果和幂等执行增加缓存与分布式锁能力。

**步骤**:
1. 在 `backend/app/core/config.py` 新增：
   - `REDIS_URL`
   - `CACHE_TTL_SECONDS`
   - `ENABLE_REDIS_CACHE`

2. 新增 `backend/app/core/cache.py`：
   - 提供 `get_json`, `set_json`, `delete`, `get_or_set`
   - Redis 不可用时降级为进程内 no-op cache，并记录 warning event

3. 新增 `backend/app/core/locks.py`：
   - 基于 Redis SET NX PX 实现 run 级别锁
   - 锁 key：`opspilot:run:{run_id}:lock`
   - 获取失败时返回明确错误，避免重复执行同一 run

4. 接入点：
   - `GraphRunner` 开始执行 run 前获取 run lock
   - approvals pending 列表使用短 TTL 缓存
   - RAG hybrid 检索结果按 query+filters 缓存

**验收**:
- 同一 run 被并发触发时只有一个执行流继续
- Redis 不可用时系统仍可运行，只是缓存/锁能力降级并有日志
- 缓存命中不会改变 API response schema

### Task 10.2: 后台任务队列与 Worker

**目标**: 将 graph run 执行从 API 请求线程中解耦，展示长任务 API、队列、失败重试和水平扩展能力。

**步骤**:
1. 选择轻量方案：
   - 默认：RQ + Redis，符合当前 Python/FastAPI 项目体量
   - 暂不引入 Celery，避免 broker/result backend/worker 配置过重

2. 新增 `backend/app/jobs/queue.py`：
   - `enqueue_graph_run(run_id: str)`
   - `enqueue_rag_reindex(doc_id: str | None)`
   - `get_job_status(job_id: str)`

3. 新增 `backend/app/jobs/worker.py`：
   - worker 入口：`python -m app.jobs.worker`
   - 执行 `GraphRunner.run(run_id)`，失败后按指数退避重试，最多 3 次

4. 修改 `POST /incidents/runs`：
   - 创建 run 后入队
   - response 增加 `job_id`（前端类型同步更新）
   - 保留本地同步执行 fallback：`ENABLE_JOB_QUEUE=false`

5. 新增 API：
   - `GET /jobs/{job_id}` 返回 queued/started/failed/finished/retry_count

**验收**:
- API 创建 run 后立即返回，不阻塞等待 graph 完成
- worker 能消费队列并推进 run 状态
- worker crash 后任务可重试
- `ENABLE_JOB_QUEUE=false` 时现有测试仍能同步跑通

### Task 10.3: 成本、延迟与质量指标看板

**目标**: 将大厂常问的 Agent 指标沉淀到系统内：任务完成率、人工接管率、工具失败率、平均耗时、token 成本、RAG 命中率。

**步骤**:
1. 新增 `backend/app/metrics/collector.py`：
   - 从 runs/events/evidence/evals 汇总指标
   - 输出按天、service、env 聚合的数据

2. 新增 API `GET /metrics/agent-quality`：
   - 返回 `success_rate`, `human_handoff_rate`, `tool_failure_rate`, `avg_duration_ms`, `avg_token_cost`, `rag_recall_at_5`

3. 前端新增 `frontend/src/pages/MetricsPage.tsx`：
   - 展示核心指标卡片和按 service 的表格
   - 保持运维工具风格，避免营销化页面

4. 将 Phase 8/9 的 eval report 接入指标：
   - 离线评测结果写入 metrics snapshot
   - 看板展示最近一次离线评测摘要

**验收**:
- mock 数据下页面可展示完整指标
- 至少包含任务完成率、人工接管率、工具失败率、平均耗时、RAG Recall@5
- 后端 API 有单元测试，前端页面有 Vitest 覆盖

---

## 执行顺序总结

```
Phase 1-4                  ── ✅ 已完成（2026-04-06）

Phase 5 执行顺序:
  Task 5.1  (MySQL 诊断工具)     ── ✅ 已完成（2026-04-08）
  Task 5.1.5(应用日志 query_logs) ── ✅ 已完成（2026-04-08）
  Task 5.2  (K8s 适配器)         ── ✅ 已完成（2026-04-08）
  Task 5.3  (SLB 适配器)         ── ✅ 已完成（2026-05-11）
  Task 5.4  (OSS 适配器)         ── ✅ 已完成（2026-05-28）

Phase 6 (Task 6.1)          ── ✅ 已完成（2026-05-28）
Phase 7 (Task 7.1)          ── ✅ 已完成，LangSmith 真实验证通过（2026-05-31）
Phase 8 启动前收口          ── ✅ 已完成（2026-06-01）

Phase 8 (Task 8.1)         ── 最后，2-3 天

Phase 9 短板补齐:
  Task 9.1  (RAG hybrid/rerank/eval)      ─┐
  Task 9.2  (Prompt 版本与回放对比)        ─┤── 依赖 Phase 6/8，可并行推进
  Task 9.3  (泛业务场景迁移 Demo)          ─┤
  Task 9.4  (推荐/预测/NLP 算法模块)       ─┘

Phase 10 生产工程能力:
  Task 10.1 (Redis 缓存与分布式锁)         ─┐
  Task 10.2 (后台任务队列与 Worker)        ─┤── 建议在 Phase 9 后执行
  Task 10.3 (成本/延迟/质量指标看板)       ─┘
```

**跨仓库依赖**: Task 5.1.5 需要 admin-sys 先部署日志写入改造（见 `admin-sys/ACTION_PLAN_LOG_TO_MYSQL.md`）
**注意**: Task 5.1 是新增 MySQL 诊断工具，Task 5.1.5 是替换 query_logs mock，5.2/5.3 是替换 K8s/SLB mock；`query_metrics` real 路由当前使用阿里云 CMS/K8s 指标，`query_deployments` real 路由当前使用 K8s deployment 列表与状态，若后续需要独立 CI/CD 发布记录平台可另列 backlog。
