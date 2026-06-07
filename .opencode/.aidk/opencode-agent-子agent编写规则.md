# OpenCode Agent/Subagent 编写规则

## 1、全局配置 — `opencode.json`

```json
{
  "instructions": ["AGENTS.md", ".vibe-workflow/templates/*.md"],
  "permission": {
    "*": "ask",
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "edit": "ask",
    "bash": {
      "git status*": "allow",
      "git diff*": "allow",
      "npm run lint*": "allow",
      "npm run test*": "allow",
      "*": "ask"
    }
  },
  "agent": {
    "plan": {
      "mode": "primary",
      "permission": { "edit": "deny", "bash": "deny" }
    },
    "build": {
      "mode": "primary",
      "permission": { "edit": "ask", "bash": { "*": "ask" } }
    }
  }
}
```

- **instructions** — 加载为 system prompt 的 Markdown 文件列表
- **permission** — 全局工具权限，支持 `allow` / `ask` / `deny`，支持通配符 `*`
- **agent** — 定义 `primary` 模式 Agent（plan/build），可覆盖全局权限

## 2、Subagent 定义 — `.opencode/agents/*.md`

每个 subagent 一个 Markdown 文件，YAML frontmatter + 正文 body：

```yaml
---
description: 代码实现工程师，只按已批准设计进行小步实现，不做计划外重构
mode: subagent
permission:
  edit: ask
  bash:
    "git status*": allow
    "npm run test*": allow
    "*": ask
---
你是代码实现 Agent。你的职责是严格按照设计文档完成一个最小垂直切片。

每次实现前必须列出：
- 本次切片目标
- 要改的文件
- 不改的文件
- 验收方式

每次实现后必须输出：
- 修改摘要
- 关键设计说明
- 测试结果
- 风险和回滚方式

禁止计划外重构。
```

### 关键规则

- `mode: subagent` — 只能被 command 或 Task 工具调度，不直接与用户对话
- `permission` — subagent 级权限覆盖（只读 agent 设置 `edit: deny`）
- `hidden: true` — 可选，设为 true 则对用户不可见
- `temperature` — 可选，控制随机性（如 0 = 确定性输出，0.1 = 低随机性）
- body 正文 — subagent 的 system prompt，定义行为约束和输出格式

### 禁止行为声明（建议）

在 body 中明确禁止事项，例如：
```
禁止行为：
- 禁止不经过复现直接修复
- 禁止小修小补跳过根因分析
- 禁止验证不通过仍宣布完成
- 禁止编辑未 review 的代码进行下一步
```

### 工具白名单（建议）

在 body 中声明精准的 task 白名单，防止越权调度：
```
允许的工具：
  task: frontend-bug-reproducer: allow
  task: frontend-bug-fixer: allow
  task: frontend-bug-reviewer: allow
  task:* : deny
```

## 3、命令定义 — `.opencode/commands/*.md`

调度 subagent 的入口：

```yaml
---
description: 代码编写：只按设计文档执行一个最小垂直切片
agent: implementation-engineer   # 指定调度到哪个 subagent
subtask: true                    # 标记为子任务
metadata:
  toolkit: vibe-dev-toolkit
  version: v2
---
请使用 `implementation-slice` skill。

任务参数：$ARGUMENTS

执行规则：
1. 先读取需求/设计/详细设计/前后端设计产物
2. 只执行一个最小垂直切片
3. 实现前列出：目标、修改文件、不修改文件、验收方式
4. 不做计划外重构
5. 改完后运行可用的 lint/typecheck/test/build 命令
6. 输出修改摘要、测试结果、风险、下一步
```

### 关键规则

- `agent` — 必填，指定目标 subagent 名称（对应 `agents/` 下的文件名，不含 `.md` 后缀）
- `subtask: true` — 该命令执行时为子任务 dispatch（独立会话）
- `deprecated: true` + `replaced_by: xxx` — 标记废弃 + 迁移目标命令
- `$ARGUMENTS` — 用户输入参数占位符
- `metadata` — 版本和工具包信息

## 4、Skill 定义 — `.opencode/skills/*/SKILL.md`

可被 `skill` 工具加载到当前 agent 上下文的指令模块：

```yaml
---
name: implementation-slice
description: 代码实现切片技能，按已批准设计执行一个最小垂直切片并完成验证
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---
## 何时使用
设计已明确，需要开始写代码时使用。

## 执行步骤
1. 读取设计文档
2. 选择一个最小垂直切片
3. 明确本次修改文件和禁止修改文件
4. 实现代码
5. 补充测试
6. 运行验证命令
7. 输出结果和风险

## 垂直切片示例
- 一个 API + 一个页面调用 + 一个测试
- 一个表单校验规则 + 一个组件测试 + 一个 E2E 断言
- 一个 Bug 根因修复 + 一个回归测试

## 禁止事项
- 禁止顺手重构
- 禁止一次性做完整大需求
- 禁止测试失败仍声称完成
```

### Command vs Skill 区别

| 维度 | Command | Skill |
|------|---------|-------|
| 执行方式 | dispatch 到 subagent（新会话） | 加载到当前 agent 上下文 |
| 是否有独立权限 | 是（subagent 权限） | 否（继承当前 agent） |
| 是否有独立会话 | 是 | 否 |
| 定义位置 | `commands/` | `skills/` |
| 用户调用 | `/command-name` | agent 自动判断或显式加载 |

## 5、权限层级体系

```
用户指令 > Agent 级 permission > 全局 permission
```

- **全局 permission** — `opencode.json` 中定义，所有 agent/skill 的基础权限
- **Agent 级 permission** — 在 agent 定义的 frontmatter 中覆盖，只能收紧不能放大
- **用户指令** — 用户直接告诉 agent 做某事，最高优先级

### 不可逾越的规则

- subagent 的 permission 只能收紧（如 `code-reviewer` 设置 `edit: deny`），不能放大超出全局范围的权限
- 如果全局设置了 `bash: ask`，subagent 不能设为 `bash: allow`（除非全局对应项也是 allow）
- 只读 agent（reviewer、analyst）必须设置 `edit: deny`


```
.opencode/
├── opencode.json              # 全局配置 + 权限 + primary agent
├── agents/                     # subagent 定义
│   ├── req-analyst.md
│   ├── solution-architect.md
│   ├── backend-architect.md
│   ├── frontend-architect.md
│   ├── implementation-engineer.md
│   ├── unit-test-engineer.md
│   ├── integration-test-engineer.md
│   ├── e2e-playwright-engineer.md
│   ├── code-reviewer.md
│   └── knowledge-curator.md
├── commands/                   # 命令入口 → 调度 agent
│   ├── implement-code.md
│   ├── vibe-implement-code.md
│   ├── vibe-route-skill.md
│   ├── full-flow.md
│   └── ...
├── skills/                     # Skill 定义（加载到上下文）
│   ├── implementation-slice/SKILL.md
│   ├── requirements-clarification/SKILL.md
│   ├── requirements-design/SKILL.md
│   ├── stage-gate-workflow/SKILL.md
│   └── ...
└── .aidk/                      # 知识库（本文档所在目录）
    ├── bug修复agent构建思路.md
    ├── bug修复工作流.md
    └── opencode-agent-子agent编写规则.md  ← 本文档
```

## 6、快速创建 Checklist

创建一个新 subagent 需要：

- [ ] 在 `agents/` 下创建 `<name>.md`
- [ ] YAML frontmatter 声明 `mode: subagent`、`description`、`permission`
- [ ] body 写明职责、输入输出、禁止行为、工具白名单
- [ ] 如需命令入口，在 `commands/` 下创建对应 `.md`，声明 `agent: <name>` + `subtask: true`
- [ ] 如需可复用流程，在 `skills/` 下创建对应 `SKILL.md`
- [ ] 确认权限只能收紧（不超过全局 permission）
- [ ] 确认只读 agent 设置了 `edit: deny`
