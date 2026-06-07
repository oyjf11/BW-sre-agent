---
name: technical-detailed-design
description: 系统详细设计技能，负责模块边界、数据流、接口、存储、权限、风险、回滚和任务拆分。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

需求设计完成，需要进入技术实现前使用。

## 工作步骤

1. 阅读当前项目结构和相关代码。
2. 识别涉及模块。
3. 定义数据流和状态流。
4. 定义接口交互。
5. 定义存储变化。
6. 识别权限、安全、并发、事务风险。
7. 拆成最小实现切片。
8. 设计验证方式。

## 输出必须包含

- 模块边界
- 文件影响清单
- 数据流
- 接口契约
- 测试策略
- 回滚方案
- 风险清单

