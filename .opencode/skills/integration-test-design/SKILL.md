---
name: integration-test-design
description: 集成测试技能，验证前后端/服务/数据库/权限/外部依赖之间的真实协作。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

单元测试无法覆盖模块协作时使用。

## 典型场景

- Controller + Service + DB
- 前端请求 + mock server
- 权限中间件 + API
- 队列生产与消费
- 缓存读写
- 外部服务 mock

## 用例矩阵

| 场景 | 输入 | 依赖 | 预期结果 | 断言 |
|---|---|---|---|---|

## 原则

- 核心链路尽量真实。
- 不稳定外部服务使用 mock。
- 测试数据可重复构造和清理。

