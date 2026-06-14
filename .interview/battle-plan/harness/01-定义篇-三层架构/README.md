# 主题1：Harness是什么 / 三层架构 / Agent=Model+Harness（定义篇）

## 一句话定位
模型是商品，包在模型外面那层工程（harness）才是护城河；harness = 信息层 + 执行层 + 反馈层，行业共识"Agent = Model + Harness"。

## A 原始素材
- [`A-原始素材/harness核心定义和行业定位.md`](./A-原始素材/harness核心定义和行业定位.md) —— 核心定义、三代范式(Prompt→Context→Harness)、三层架构、六大组件、Harness vs LLMOps
- 补充：[`../00-共享素材/ai_harness_interview_handbook.md`](../00-共享素材/ai_harness_interview_handbook.md) §0(三十秒开场白)、§1(名词表) —— 同一结论的人话版

## B 验证
- [`../04-读写路径治理/B-验证/实战-2026-06-15-Harness控制面vs写路径治理.md`](../04-读写路径治理/B-验证/实战-2026-06-15-Harness控制面vs写路径治理.md) —— 验证了"Agent=Model+Harness"这个**结论本身是对的**（harness=控制面），但本主题A层里那篇白皮书（见04文件夹）里六大组件的具体代码示例、92%数字等是营销虚构
- [`../00-共享素材/ai_harness_interview_handbook.md`](../00-共享素材/ai_harness_interview_handbook.md) §3 —— 提供"六大组件"的**真实版对照**（Anthropic/OpenAI/LangChain 三个真实代表作各自的招牌设计）

## C 结论/项目落地
- 推导链 Chain A 第一步（见 [`../05-评测方法论/C-结论/推导链-2026-06-15-什么是harness与怎么搭评测.md`](../05-评测方法论/C-结论/推导链-2026-06-15-什么是harness与怎么搭评测.md)）："模型本身不值钱，值钱的是包在模型外面那层工程"
- handbook §0 三十秒开场白是最浓缩的版本

## 状态
**缺口**：没有把"三层架构/六组件"逐项映射到 OpsPilot 13 个节点的项目落地文章（对应母题骨架 M10 的项目锚点说明）。已在 `../../题库/母题骨架-一页纸.md` M10 处加了引用本主题作为"理论背景"的指针，但尚无逐项映射表。
