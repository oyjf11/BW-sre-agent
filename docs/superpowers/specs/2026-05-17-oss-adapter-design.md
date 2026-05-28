# OSS 适配器设计（Task 5.4）

> 日期: 2026-05-17 | 状态: 已确认

## 目标

RCA 报告和证据包归档到阿里云 OSS。

## 架构

```
rca_node  ──ToolGateway────> write_rca_to_oss       ──> oss_client.py ──> 阿里云 OSS
           ──ToolGateway────> write_evidence_to_oss  ──> oss_client.py ──> 阿里云 OSS
```

## 文件变更

| # | 文件 | 操作 |
|---|------|------|
| 1 | `backend/requirements.txt` | 新增 `oss2>=2.18.0` |
| 2 | `backend/app/core/config.py` | 新增 `alibaba_oss_bucket`、`alibaba_oss_endpoint` |
| 3 | `backend/app/tools/clients/oss_client.py` | **新建** OssClientWrapper |
| 4 | `backend/app/tools/adapters/oss_adapter.py` | **新建** 2 个 async 工具函数 |
| 5 | `backend/app/tools/adapters/__init__.py` | 新增 2 个 mock 函数 |
| 6 | `backend/app/tools/gateway.py` | 注册 handler/select_adapter/ToolMetadata |
| 7 | `backend/app/graph/nodes/__init__.py` | rca_node 中通过 ToolGateway 调用 OSS 写入 |
| 8 | `backend/app/tests/test_oss_adapter.py` | **新建** 单元测试 |

## OssClientWrapper 设计

- 复用现有 `ALIBABA_ACCESS_KEY_ID/SECRET/REGION_ID` 配置
- 新增 `ALIBABA_OSS_BUCKET`、`ALIBABA_OSS_ENDPOINT`
- 前缀白名单：仅允许 `rca/` 和 `evidence/`
- SDK: oss2，按现有 client 模式 lazy 初始化 + try/except 保护

## 工具接口

### write_rca_to_oss

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| run_id | string | 是 | 运行 ID |
| service | string | 否 | 服务名 |
| env | string | 否 | 环境 |
| content | string | 是 | RCA 报告内容 |
| content_type | string | 否 | "markdown" 或 "json"，默认 "markdown" |

OSS key: `rca/{service}/{run_id}.{ext}`

### write_evidence_to_oss

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| run_id | string | 是 | 运行 ID |
| service | string | 否 | 服务名 |
| env | string | 否 | 环境 |
| content | string | 是 | 证据包 JSON 内容 |

OSS key: `evidence/{service}/{run_id}.json`

## rca_node 集成

在 RcaReport 构造完成后、赋值 `state["rca_report"]` 前，best-effort 通过 ToolGateway 调用写入 OSS，失败不阻塞主流程。

## 配置

```env
ALIBABA_OSS_BUCKET=haoxuezhuli
ALIBABA_OSS_ENDPOINT=oss-cn-shenzhen.aliyuncs.com
```
