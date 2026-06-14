# 主题4：读路径 vs 写路径治理（幂等键 / 前置校验 / HITL / loop guard）

## 一句话定位
harness = 控制面，干 5 件事；只读 agent（读路径）只需要限流/追踪/测试这三件就够了；一旦涉及写操作（写路径），必须再加 4 件——**幂等键、前置校验、HITL、loop guard**。

## A 原始素材
- [`A-原始素材/harness demo.md`](./A-原始素材/harness%20demo.md) —— SecurityGateway / COMMAND_WHITELIST 等代码雏形，个人3天harness搭建checklist
- [`A-原始素材/AI Agent Harness Engineering 技术白皮书.md`](./A-原始素材/AI%20Agent%20Harness%20Engineering%20技术白皮书.md) —— 安全治理章节（`check_permission`空壳、`detect_prompt_injection`），**后被证实大部分是营销虚构**（见 B 层）

## B 验证（核心文章）
- [`B-验证/实战-2026-06-15-Harness控制面vs写路径治理.md`](./B-验证/实战-2026-06-15-Harness控制面vs写路径治理.md) —— 完整批判白皮书（92%数字/OpenHarness/A_agent公式/进程内字典限流/hset覆盖bug/check_permission空壳均查无实据），提出读写路径框架，并逐条映射到 OpsPilot 真实代码：
  - `backend/app/services/executor.py:62,64-85,88,120`（幂等键查重 + 前置校验 + 审计）
  - `backend/app/graph/nodes/__init__.py:1074-1133`（critic 4路裁决 + loop guard max 2）
  - `backend/app/graph/nodes/__init__.py:1208`（risk_gate 审批门）
  - `backend/app/graph/nodes/__init__.py:1321`（approval_interrupt HITL 落库）
  - `backend/app/tools/gateway.py:840,860,1063,1082`（schema 校验/重试/audit/脱敏）

## C 结论/项目落地
- 推导链 Chain A 后半段（见 [`../05-评测方法论/C-结论/推导链-2026-06-15-什么是harness与怎么搭评测.md`](../05-评测方法论/C-结论/推导链-2026-06-15-什么是harness与怎么搭评测.md)）：harness=控制面5件事 → 读路径 vs 写路径 → 写路径多4件

## 状态
覆盖**最完整**的主题之一。已 patch 进 [`../../题库/母题骨架-一页纸.md`](../../题库/母题骨架-一页纸.md) **扩展母题候选①**（挂在 A6/A9 下）。
