# 主题3：Guides & Sensors / Computational vs Inferential / 三种Harness类型（Birgitta独立框架）

## 一句话定位
Guides=事前引导（feedforward），Sensors=事后检测（feedback）；Computational（代码判定）vs Inferential（语义判断）；三种 Harness 类型 = Maintainability / Architecture Fitness / Behaviour。

## A 原始素材
- [`A-原始素材/harness for code agent.md`](./A-原始素材/harness%20for%20code%20agent.md) —— Birgitta Böckeler 精读全篇（Martin Fowler 原文中文精读，2026-04-02）：Guides/Sensors、Computational/Inferential 检查、三种Harness类型、Steering Loop、Harnessability、Ambient Affordances、Harness Templates

## B 验证
- 本身已是 B 层质量（对原文的精读转述），不需要额外批判文章。

## C 结论/项目落地
- 无直接项目映射文章。但有一条潜在连接：[`../05-评测方法论/B-验证/e2e测试-何为自愈？.md`](../05-评测方法论/B-验证/e2e测试-何为自愈？.md) 里"真红 vs 假红"的分诊判断，本质就是一次 **Inferential check**——Computational vs Inferential 这对概念，和评测体系里"能用代码判的绝不用模型判"其实是同一件事的两种说法。

## 状态
**候选缺口**，但优先级低。这个连接本身可能是面试中的一个加分项，但不构成独立母题。除非面试明确单独问"Maintainability/Architecture Fitness/Behaviour Harness 怎么分类"这类纯概念题，否则不需要单独 patch。
