# 当前工程缺口

更新时间：2026-05-31

本文只记录当前仍需要处理的问题。Phase / Task 完成状态以根目录 `ACTION_PLAN.md` 为唯一事实源；历史审查和已完成修复已移动到 `backend/docs/archive/2026-03/`。

## 已关闭的旧缺口

以下内容已经不再是当前缺口：

- Phase 5 阿里云真实数据源接入：MySQL 诊断、MySQL 应用日志、K8s、SLB、OSS 已完成基础代码接入。
- Phase 6 RAG 知识检索与写回：`backend/app/rag/` 已实现 indexer / retriever / reranker / writer，并接入 `retrieve_memory_node` 与 RCA 写回链路。
- 本地 tracing 闭环：`backend/app/tracing.py`、GraphRunner / ToolGateway / LLMClient 埋点、`GET /incidents/runs/{run_id}/trace`、前端 `View Trace` 入口已完成。

## P1：Phase 7 外部 Tracing Provider

状态：✅ 已完成。LangSmith 真实控制台验证通过，Langfuse 代码已就绪待验。

当前已有：

- `backend/app/tracing.py`
- `backend/app/tracing_providers.py`
- `GET /incidents/runs/{run_id}/trace`
- GraphRunner / ToolGateway / LLMClient tracing 埋点
- RunDetailPage trace 外链入口
- LangSmith / Langfuse provider 配置和 best-effort 上报
- API 返回 `external_trace_id`、`external_root_span_id`、`external_trace_url`
- LangSmith 真实验证：span 上报成功，trace URL 包含正确 org/project ID

剩余验收（低优先级）：

- Langfuse 真实环境验证（代码已就绪，配置即用）

## P2：Phase 8 离线评测

状态：未实现。

缺口：

- `backend/app/evals/` 目录当前无 replay runner、dataset 或 metrics 实现
- 没有 replay dataset
- 没有 Top1/Top3 根因命中率、风险等级准确率、步骤数/延迟/token 消耗等评测指标
- 没有 `python -m app.evals.replay_runner ...` CLI

## P1：Phase 9 面试短板补齐

状态：未启动。

缺口：

- RAG hybrid search / keyword index / citation eval 尚未实现
- Prompt 版本管理与回放对比尚未实现
- 泛业务场景迁移 Demo 尚未实现
- 相似故障推荐、风险预测、轻量 NLP 抽取尚未实现

## P1：Phase 10 生产工程能力

状态：未启动。

缺口：

- Redis 缓存与分布式锁尚未实现
- 后台任务队列与 worker 尚未实现
- 成本、延迟与质量指标看板尚未实现

## 谨慎项

- 各 real adapter 的代码路径已接入，但真实环境联调仍依赖外部凭证、白名单、region、bucket、K8s namespace 白名单和线上数据可用性。
- `query_ticket_by_id`、`query_service_metadata` 的真实数据源尚未单独接入；当前重点仍是手工工单 / 告警事件入口与已接入的证据源。
- `query_runbook` 的 gateway real 模式仍 fail-closed；当前图内历史知识检索通过 `backend/app/rag/` 完成。
- `execute_action` 的 real 模式仍 fail-closed；真实执行动作需要另行设计审批、幂等、审计和非生产白名单策略。

## 文档维护规则

- 当前进度只改 `ACTION_PLAN.md`
- 当前缺口只改本文档
- 设计文档、PRD、历史 plan/spec 不作为完成状态依据
- 已解决问题移动到 `backend/docs/archive/`
- 不要在多个文档里重复维护同一份 Phase 状态
