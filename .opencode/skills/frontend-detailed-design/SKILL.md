---
name: frontend-detailed-design
description: 前端详细设计技能，负责页面、组件、状态、路由、请求、异常态、选择器和前端测试设计。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

任何涉及前端 UI、页面、组件、路由、状态、接口调用、表单、权限可见性的任务。

## 检查清单

- 页面入口和路由
- 组件树和职责
- props / emits / callbacks / hooks
- 状态来源：URL、服务端、全局 store、本地 state
- API 调用封装和错误处理
- loading / empty / error / permission / success states
- 表单校验和提交防抖
- 可访问性：label、role、键盘操作
- 稳定选择器：data-testid
- 单元测试和 Playwright 场景

## 禁止事项

- 禁止为了方便测试而破坏用户可见文案。
- 禁止新增全局状态而不说明必要性。
- 禁止在组件中硬编码接口地址。

