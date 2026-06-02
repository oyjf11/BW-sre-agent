# Superpowers 兼容性说明

> vibe-dev-toolkit v2 与 Superpowers 的共存约定

## 目录边界

| 目录 | 所有者 | 规则 |
|------|--------|------|
| `.opencode/` | vibe-dev-toolkit | opencode 配置、commands、agents、skills |
| `.vibe-workflow/` | vibe-dev-toolkit | 工作流模板、脚本、产物、证据 |
| `.agents/` | Superpowers | Agent skills（用户级） |
| `docs/` | Superpowers | 文档模板，**vibe-dev-toolkit 不得写入** |
| `AGENTS.md` | 项目 | 主规则文件，**vibe-dev-toolkit 不得覆盖** |

## 冲突预防

### AGENTS.md
- vibe-dev-toolkit 不会覆盖此文件
- v2 新增规则写入 `AGENTS.vibe-dev-toolkit.md`（如项目启用）
- 或写入 `.vibe-workflow/SUPERPOWERS_COMPAT.md` 本文档

### docs/ 目录
- vibe-dev-toolkit 不会创建项目根目录下的 `docs/` 目录
- 所有工作流产物使用 `.vibe-workflow/tasks/` 路径
- 如需生成文档，默认输出到 `.vibe-workflow/` 下

### Skills 命名空间
- opencode skills 使用 `.opencode/skills/<name>/SKILL.md`
- Superpowers skills 使用 `.agents/skills/<name>/SKILL.md`
- 两者命名不冲突，openCode 和 Superpowers 各管各的

### Commands
- v1 命令名：`/clarify-requirements` 等（已 deprecated）
- v2 命令名：`/vibe-clarify-requirements` 等（vibe- 前缀）
- 不会与 Superpowers 提供的 commands 冲突

## 迁移路径

### 从 v1 迁移到 v2
1. 旧命令仍可用但标记 `deprecated: true`
2. 新任务使用 `/vibe-*` 命令
3. v2 的 MANIFEST.yaml、stage-gates、evidence 包为新增能力
4. v1 的 SKILL.md 内容不变，v2 增加标准化段

### Superpowers 升级
- vibe-dev-toolkit 不会修改 `.agents/` 或 `~/.cache/opencode/` 下的任何内容
- 如果 Superpowers 自身升级导致冲突，请在 SUPEROWERS_COMPAT.md 记录

## known issues

- `using-superpowers` skill 自动注入的指令可能和 vibe-dev-toolkit 的阶段闸门理念有重叠。目前两者互补不冲突。
- opencode 的 `skill` 工具加载 `.opencode/skills/` 下的 skills，也加载用户级 Superpowers skills，两者可以共存。

## 版本历史

- v2 (2026-06-03): vibe- 前缀统一、MANIFEST、stage-gates、evidence pack、agent 权限增强
- v1 (2026): 初始版本，从 docs/ai-workflow 迁移到 .vibe-workflow/
