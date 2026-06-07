---
name: backend-detailed-design
description: 后端详细设计技能，负责 API、数据库、权限、事务、幂等、异常、日志、审计和集成测试设计。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

任何涉及服务端接口、数据库、权限、业务规则、任务状态、队列、缓存、外部服务的任务。

## 检查清单

- API path / method / request / response
- DTO / schema / validation
- 数据表 / 字段 / 索引 / 迁移
- 权限：user_id / tenant_id / role / scope
- 事务边界
- 幂等 key
- 并发冲突
- 错误码
- 日志和审计
- 集成测试和回滚策略

## 禁止事项

- 禁止绕过权限检查。
- 禁止无说明地修改接口协议。
- 禁止无迁移方案地修改数据结构。

