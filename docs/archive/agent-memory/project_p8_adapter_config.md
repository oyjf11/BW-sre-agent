---
name: P8 Adapter Config Pending
description: P8 real adapters require Alibaba Cloud config from user - must ask before implementing
type: project
---

P8 真实适配器实现前，必须向用户索要阿里云配置信息：

- **MySQL**: 连接信息、表名/字段、接入方式（直连 vs API）
- **K8s**: 集群接入方式（kubeconfig / ACK API）、namespace 规范
- **SLB/ALB**: 产品类型、OpenAPI SDK、认证方式、指标名
- **OSS**: Bucket/endpoint/目录结构、认证方式
- **通用**: Region、统一认证方案、是否有内部网关代理

**Why:** 没有这些信息无法实现真实适配器，只能写接口契约和 mock。
**How to apply:** 进入 P8.1 真实适配器任务时，主动询问用户提供以上配置。
