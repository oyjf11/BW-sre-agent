# 当前工程缺口

更新时间：2026-05-11

本文只记录当前仍需要处理的问题。历史审查和已完成修复已移动到 `backend/docs/archive/2026-03/`。

## P1：Phase 5 剩余真实适配器

### SLB 适配器

状态：未实现。

目标：

- `query_lb_health_status` 切到真实阿里云 SLB/ALB 查询
- `query_lb_traffic_metrics` 切到真实流量、5xx、延迟指标查询

注意：

- mock 版本仍在 `backend/app/tools/adapters/__init__.py`
- real 路由尚未在 `backend/app/tools/gateway.py` 接入真实实现
- 需要阿里云访问凭证、region、负载均衡产品类型和只读权限

### OSS 归档适配器

状态：未实现。

目标：

- `write_rca_report_to_oss`
- `write_evidence_bundle_to_oss`

注意：

- 只能允许写入 `rca/` 和 `evidence/` 前缀
- `backend/app/services/knowledge_writeback.py` 目前归档逻辑仍是 stub

## P1：Phase 6 RAG 知识检索与写回

状态：未实现正式向量库。

当前已有：

- `backend/app/graph/nodes/retrieve_memory.py` 通过 `query_runbook` 获取基础 memory
- `backend/app/graph/nodes/writeback_knowledge.py`
- `backend/app/services/knowledge_writeback.py`

缺口：

- `backend/app/rag/` 目录存在但为空，暂无 indexer/retriever/writer 实现
- 没有 `chromadb` 或 `pgvector` 依赖
- RCA 写回目前只记录 writeback 记录，未写入真实向量库

## P1：Phase 7 Tracing

状态：进行中，已完成本地 tracing 闭环，外部 provider 未接入。

当前已有：

- `backend/app/tracing.py`
- `GET /incidents/runs/{run_id}/trace`
- GraphRunner / ToolGateway / LLMClient tracing 埋点
- RunDetailPage trace 外链入口

缺口：

- LangSmith / Langfuse 依赖仍未启用
- 外部 tracing provider 还没有真实上报
- 还缺少外部 trace id / public trace url 的真实回传

## P2：Phase 8 离线评测

状态：未实现。

缺口：

- `backend/app/evals/` 目录存在但为空，暂无 replay runner、dataset 或 metrics 实现
- 没有 replay dataset
- 没有 Top1/Top3、风险等级、步骤数等评测指标

## 文档维护规则

- 当前进度只改 `ACTION_PLAN.md`
- 当前缺口只改本文档
- 历史问题解决后移动到 `backend/docs/archive/`
- 不要在多个文档里重复维护同一份 Phase 状态
