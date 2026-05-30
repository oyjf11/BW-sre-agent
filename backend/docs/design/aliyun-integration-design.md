# 阿里云平台对接设计

更新时间：2026-05-30

进度说明：本文是阿里云平台接入的设计与联调参考，不是项目进度源。Phase / Task 完成状态以根目录 `ACTION_PLAN.md` 为准。

## 1. 目标

将当前 OpsPilot 后端从 `mock tools` 逐步接入真实阿里云运维平台，优先完成只读能力，覆盖以下场景：

- 工单与告警查询
- 服务元数据查询
- Kubernetes 排障证据查询
- 负载均衡健康与流量指标查询
- RCA 与证据包归档到 OSS

本阶段目标不是直接做高风险自动执行，而是让 Agent 的 `ticket -> triage -> evidence -> diagnose -> remediation -> rca` 主链路能够消费真实平台数据。

---

## 2. 当前现状

当前工程已经具备：

- FastAPI 主入口与工单/审批 API
- LangGraph 故障处理主图
- Tool Gateway 统一工具调用入口
- mock adapters 与基础测试
- MySQL 诊断 client/adapter：`backend/app/tools/clients/mysql_client.py`、`backend/app/tools/adapters/mysql_adapter.py`
- MySQL 应用日志 `query_logs` real 路由：读取业务库 `common_app_log`
- K8s 只读 client/adapter：`backend/app/tools/clients/k8s_client.py`、`backend/app/tools/adapters/k8s_adapter.py`
- `query_metrics` real 路由：通过 `backend/app/tools/clients/cms_client.py` 与 `backend/app/tools/adapters/metrics_adapter.py` 查询阿里云 CMS/K8s 指标
- `query_deployments` real 路由：通过 K8s deployment 列表与状态提供发布/部署侧证据
- SLB client/adapter：`backend/app/tools/clients/slb_client.py`、`backend/app/tools/adapters/slb_adapter.py`
- OSS client/adapter：`backend/app/tools/clients/oss_client.py`、`backend/app/tools/adapters/oss_adapter.py`

当前工程仍缺少：

- 真实环境凭证、白名单、region、bucket、namespace 等配置的联调验收记录
- service metadata normalization
- `ticket_id` 真实自动查询、service metadata 真实查询
- 独立 CI/CD 发布记录平台接入（当前 `query_deployments` 使用 K8s deployment 状态）
- 真实受控执行动作接入

当前 `TOOL_ADAPTER_MODE=real` 已接入 MySQL、应用日志、K8s、指标、SLB、OSS 的真实路由；`query_runbook` 与 `execute_action` real 模式仍保持 fail-closed，不能返回伪造成功结果。

---

## 3. 接入范围

## 3.1 MySQL

用途：

- `query_ticket_by_id`
- `query_alerts_by_service`
- `query_recent_deploy_records`
- `query_service_metadata`

说明：

- 优先使用只读账号
- 只允许参数化查询
- 不允许 LLM 直接生成 SQL

## 3.2 Kubernetes

用途：

- `query_k8s_pods`
- `query_k8s_events`
- `query_k8s_deployment_status`
- `query_k8s_pod_logs_summary`

说明：

- 优先使用已有运维平台 API
- 如果直接连集群，建议只读 `RBAC`
- 日志能力优先做摘要，不直接返回大段原始日志

## 3.3 SLB / ALB

用途：

- `query_lb_health_status`
- `query_lb_traffic_metrics`

说明：

- 优先接你现有平台的统一查询 API
- 如果没有统一 API，再考虑云 SDK

## 3.4 OSS

用途：

- `write_rca_to_oss`
- `write_evidence_to_oss`
- `read_oss_log_object`（可选）

说明：

- 先做写入 RCA 与 evidence bundle
- bucket 仅允许写 `rca/`、`evidence/` 前缀

---

## 4. 设计原则

1. `LLM` 不直接接触阿里云凭证或数据库密码。
2. 所有外部平台能力统一通过 `Tool Gateway` 暴露。
3. 先只读，后执行；先低风险，后高风险。
4. 所有工具调用必须显式带 `env`。
5. 所有资源访问必须走白名单：`service / namespace / bucket prefix`。
6. 所有工具响应必须结构化、可审计、可落库。

---

## 5. 代码落点

当前工程内已落地以下文件，后续维护仍按 client / adapter / gateway 分层：

```text
backend/app/tools/clients/mysql_client.py
backend/app/tools/clients/k8s_client.py
backend/app/tools/clients/slb_client.py
backend/app/tools/clients/oss_client.py

backend/app/tools/adapters/mysql_adapter.py
backend/app/tools/adapters/k8s_adapter.py
backend/app/tools/adapters/slb_adapter.py
backend/app/tools/adapters/oss_adapter.py
```

职责划分：

- `clients/*`：真正发起外部请求，管理认证、连接、超时、重试
- `adapters/*`：将外部平台原始结果转成 OpsPilot 内部统一响应结构
- `gateway.py`：根据工具名路由到真实 adapter

---

## 6. 配置设计

`app/core/config.py` 中应维护以下配置项：

```env
TOOL_ADAPTER_MODE=mock

MYSQL_DSN=
MYSQL_POOL_SIZE=5
MYSQL_READONLY=true

K8S_CONFIG_PATH=
K8S_CONTEXT=
K8S_ALLOWED_NAMESPACES=["default"]

ALIBABA_ACCESS_KEY_ID=
ALIBABA_ACCESS_KEY_SECRET=
ALIBABA_REGION_ID=
K8S_CLUSTER_ID=

ALIBABA_OSS_BUCKET=
ALIBABA_OSS_ENDPOINT=
```

OSS 写入前缀当前在客户端中硬编码白名单为 `rca/` 与 `evidence/`，不要通过环境变量放宽。

同时建议增加这些结构化配置：

- `allowed_services`
- `allowed_namespaces`
- `allowed_bucket_prefixes`
- `service_registry_source`

---

## 7. 工具映射设计

建议将真实工具分为两层：

1. 平台原生工具
2. Agent 通用工具

平台原生工具示例：

- `query_ticket_by_id`
- `query_service_metadata`
- `query_recent_deploy_records`
- `query_k8s_pods`
- `query_k8s_events`
- `query_lb_health_status`
- `write_rca_to_oss`

Agent 通用工具示例：

- `query_logs`
- `query_metrics`
- `query_deployments`
- `query_runbook`

推荐做法：

- `query_logs` 映射到 `k8s pod logs summary` 或 `oss log object`
- `query_metrics` 映射到 `slb traffic metrics` 或平台统一监控 API
- `query_deployments` 映射到 `mysql deploy records` + `k8s deployment status`
- `query_runbook` 先保留本地/知识库实现，不依赖阿里云

这样前层 Agent 不需要感知底层平台差异。

---

## 8. Normalization 设计

真实平台最大的问题通常不是“连不上”，而是“同一个服务在多个系统里叫法不同”。

建议通过 `query_service_metadata` 建立统一映射：

- `service_name`
- `env`
- `namespace`
- `deployment_name`
- `cluster_id`
- `lb_id`
- `owner_team`
- `log_source_type`
- `aliases`

Graph 中的使用方式：

1. `intake`/`triage` 后，先查 `service metadata`
2. 再根据 metadata 决定 fanout 查询哪些真实数据源
3. 所有 evidence 都带上 `source_ref` 和 `metadata`

---

## 9. Graph 改造建议

## 9.1 intake

新增：

- 支持只传 `ticket_id`
- 若存在 `ticket_id`，优先调用 `query_ticket_by_id`

## 9.2 planner

新增：

- 先查 `query_service_metadata`
- 再把 `namespace/deployment/lb_id` 写入 `plan`

## 9.3 evidence_fanout

改为根据 metadata 动态 fanout：

- K8s：pods / events / deployment
- SLB：health / traffic metrics
- MySQL：deploy records / alerts
- OSS：必要时读归档日志

## 9.4 verify_outcome

使用真实只读工具校验：

- deployment 状态是否恢复
- pod 异常是否消失
- LB 5xx/健康状态是否恢复

## 9.5 rca

增加可选归档：

- `write_rca_to_oss`
- `write_evidence_to_oss`

OSS 失败不应阻塞 RCA 主流程。

---

## 10. 分阶段实施计划

## Phase A：MySQL 只读接入

状态：部分完成。MySQL 诊断工具与应用日志 `query_logs` 已完成；`ticket_id`、service metadata、独立 deploy records 的真实查询仍可作为后续扩展。

目标：

- 工单、服务元数据、部署记录可查

交付：

- `mysql_client.py`
- `mysql_adapter.py`
- `query_ticket_by_id`
- `query_service_metadata`
- `query_recent_deploy_records`

验收：

- 用真实 `ticket_id` 能自动拉单
- service 能映射到 namespace / deployment / lb_id

## Phase B：K8s 只读接入

状态：已完成基础接入。

目标：

- K8s 成为主证据源

交付：

- `k8s_client.py`
- `k8s_adapter.py`
- `query_k8s_pods`
- `query_k8s_events`
- `query_k8s_deployment_status`
- `query_k8s_pod_logs_summary`

验收：

- 指定服务能返回 pod 状态摘要
- events 能返回 top reason 聚合

## Phase C：SLB 只读接入

状态：已完成基础接入，真实联调依赖阿里云 AK/SK 与 region 配置。

目标：

- 获取入口层证据

交付：

- `slb_client.py`
- `slb_adapter.py`
- `query_lb_health_status`
- `query_lb_traffic_metrics`

验收：

- 至少能查到健康状态或 5xx 趋势中的一个

## Phase D：OSS 归档接入

状态：已完成基础接入，真实联调依赖 OSS bucket / endpoint / AK/SK 配置。

目标：

- RCA 和证据包可归档

交付：

- `oss_client.py`
- `oss_adapter.py`
- `write_rca_to_oss`
- `write_evidence_to_oss`

验收：

- RCA 成功写入 `rca/`
- evidence bundle 成功写入 `evidence/`

## Phase E：受控执行（后续）

目标：

- 在非生产或白名单环境中接入真实执行

说明：

- 这一步不建议和只读接入同时推进
- 必须在审批、幂等、审计链路补齐后再做

---

## 11. 安全与权限

必须满足：

1. MySQL 使用只读账号。
2. Kubernetes 使用只读 `RBAC` 或平台只读代理。
3. OSS 仅允许特定 bucket 和 prefix。
4. 所有凭证只保存在后端，不进入前端和 Prompt。
5. 所有工具调用记录审计日志。
6. 所有查询都受 `env + service whitelist` 限制。

---

## 12. 测试策略

## 12.1 单元测试

- client 参数构造测试
- adapter 结果规范化测试
- gateway 路由测试
- config 白名单与校验测试

## 12.2 集成测试

- 用测试环境 MySQL 跑 `ticket_id -> ticket`
- 用测试环境 K8s 跑 `service -> pods/events/deployment`
- 用测试环境 OSS 跑 RCA 写入

## 12.3 失败场景测试

- 凭证缺失
- namespace 不在白名单
- bucket prefix 非法
- 外部接口超时
- 平台部分不可用时降级

---

## 13. 后续建议

MySQL、K8s、SLB、OSS 的基础接入已经完成，后续不应再按“从零实现四个数据源”的旧顺序推进。

更合理的顺序是：

1. 补真实环境联调记录：MySQL / K8s / CMS / SLB / OSS 各跑一条受控查询或写入。
2. 补 service metadata normalization，让服务名、namespace、deployment、lb_id、owner 等映射统一。
3. 视需要补 `ticket_id` 真实自动查询与独立 CI/CD 发布记录平台。
4. 继续推进 Phase 7 外部 tracing provider 与 Phase 8 离线评测。

注意：

- `query_deployments` 当前来自 K8s deployment 状态，不等价于完整 CI/CD 发布记录。
- OSS 归档仍是 best-effort，失败不能阻塞 RCA 主流程。
- 所有真实执行动作仍应保持 fail-closed，直到审批、幂等、审计与非生产白名单策略补齐。

---

## 14. 对当前工程的直接结论

当前工程已经完成多源阿里云接入的基础代码闭环，后续重点是按“真实 adapter + fail closed + 分阶段联调”的方式补齐线上验证、服务元数据映射和评测闭环。

不建议继续在 `gateway.py` 中追加伪真实函数，也不建议直接把阿里云 SDK 调用写进 Graph 节点。正确做法是：

- Graph 只关心工具名和状态流转
- Gateway 只关心路由和审计
- Client/Adapter 负责具体平台对接

这样后续无论继续扩展 MySQL、K8s、SLB、OSS、CMS 指标还是 CI/CD 发布记录，都不会把主流程再次耦死。
