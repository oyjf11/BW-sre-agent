# 前端详细设计

## 任务信息

- 任务名称：
- 创建日期：
- 负责人：
- 关联分支：
- 关联 Issue / PR：

## 背景

## 目标

## 非目标

## 输入

## 输出

## 详细内容

## E2E Locator Design（必须填写）

> 遵守 `.vibe-workflow/testing/playwright-locator-contract.md`

| 元素 | 定位方式 | data-testid（如有） | 备选定位 |
|------|---------|-------------------|---------|
| {{ELEMENT_NAME}} | getByRole / getByLabel / getByText / getByTestId | {{TESTID}} | {{FALLBACK}} |

### 页面级 testid 清单

```
<!-- 每个关键可交互元素必须注册 -->
{{ELEMENT_1}}: data-testid="{{TESTID_1}}"
{{ELEMENT_2}}: data-testid="{{TESTID_2}}"
```

### 禁止使用的定位方式

- [ ] 无 CSS class 选择器
- [ ] 无 nth-child / first() / last()
- [ ] 无深层 XPath
- [ ] 无框架内部属性（data-reactid 等）

## 验收标准

## 风险与回滚

## 待确认问题
