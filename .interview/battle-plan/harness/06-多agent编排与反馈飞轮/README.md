# 主题6：多 Agent 编排与反馈飞轮（critic 仲裁 / deepagents 范式 / 数据反馈飞轮）

## 一句话定位
Shallow agent = 纯 ReAct 工具循环；Deep agent = 循环外加规划 + 文件系统（卸上下文）+ 子agent（隔离上下文）+ 长期记忆 + HITL —— OpsPilot 是手搓的 deep agent。

## A 原始素材
- [`../00-共享素材/ai_harness_interview_handbook.md`](../00-共享素材/ai_harness_interview_handbook.md) §4（架构怎么选：用"招人"常识，0-4级分级表）+ §2（理论根基：Brooks定律、"多agent是不是悖论"的完整答案）

## B 验证
- [`B-验证/实战-2026-06-10-deepagents范式与项目对标.md`](./B-验证/实战-2026-06-10-deepagents范式与项目对标.md) —— 验证 OpsPilot 是手搓的 deep agent：Planning→planner节点、Sub-agents→evidence_fanout、File system→evidence持久化、HITL→risk_gate+approval_interrupt、Long-term memory→retrieve_memory+RAG、自我纠错→critic回边

## C 结论/项目落地
- [`C-结论/实战-2026-06-10-critic仲裁打分机制.md`](./C-结论/实战-2026-06-10-critic仲裁打分机制.md) —— critic 4路裁决 + 质量分公式 avg×penalty×coverage，对应 M16 Reflection
- [`C-结论/实战-2026-06-10-数据反馈飞轮.md`](./C-结论/实战-2026-06-10-数据反馈飞轮.md) —— 四层飞轮：写回闭环 / 在线人工打分 / LLM-as-Judge补覆盖 / 离线Golden Set防回退

## 状态
覆盖**最完整**的主题。已 patch 进 [`../../题库/母题骨架-一页纸.md`](../../题库/母题骨架-一页纸.md) **扩展母题候选③**（挂在 M16/M17 下）。
