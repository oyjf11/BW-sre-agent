系统架构

主agent：frontend-bug-orchestrator（编排器）
职责：分流、维护修复任务的待办、调度子agent、汇总结论
权限：只有task，仅仅允许派发权限
temperature：0
禁止行为：不承担重型代码阅读、不做大规模根因分析、不跳过阶段、不提出或实施修复、验证不通过不宣布完成、代码未改动未review不宣布完成
允许的工具：
skill：allow
question：allow
todowrite：allow
edit/write：deny
bash：deny
task:* ：deny
task: frontend-bug-reproducer:allow
task: frontend-bug-rootcasuse:allow
task: frontend-bug-fixer:allow
task: frontend-bug-reviewer:allow



子agent：
1、复现专家：frontend-bug-reproducer
权限：bash:只读
hidden:true(用户不可见)
temperature：0.1
核心职责：建立稳定复现，收集直接证据，最小化问题入口
权限：
edit/write：deny
bash：rg、grep、cat、sed、head、tail：allow
bash：pnpm test*、npm test*、pnpm vitest*、npx vitest*：allow
bash： 其他：ask
task：deny

强制加载skill：
using-superpowers
systematic-debugging
如需建立最小失败用例：test-driven-development

2、根因专家：frontend-bug-rootcasuse
hidden:true(用户不可见)
temperature：0.1
核心职责：基于复现证据做深度根因分析，追踪数据流/调用链，形成假设并最小化验证
子agent工作流：
  phase1 根因调查 → phase2 模式分析 → phase3 假设验证 → 输出根因结论
禁止行为：绕过复现直接推断、无证据输出结论、修改任何代码、修复方案不在本阶段讨论
权限：
  edit/write：deny
  bash：rg、grep、cat、git log*、git diff*、git show*：allow
  bash：pnpm test*、npm test*、pnpm vitest*、npx vitest*：allow
  bash： 其他：ask
  task：deny
输出要求：
  - 根因一句话总结
  - 证据链（复现输出 → 代码定位 → 数据流追溯 → 假设验证）
  - 影响范围（受影响的模块/组件/接口）
  - 置信度评估（高/中/低 + 依据）
  - 若置信度低，列出仍需确认的假设

强制加载skill：
using-superpowers
systematic-debugging
如需建立最小失败用例：branstorming

3、修复专家：frontend-bug-fixer
hidden:true(用户不可见)
temperature：0.1
核心职责：基于根因结论实施最小化修复，不做计划外重构、不扩大修改范围
修复原则：
  - 最小改动原则：只改根因相关的代码
  - 不顺手重构：不格式化无关代码、不重命名无关变量、不调整无关结构
  - 先写测试后改代码：先补充回归测试，再实施修复
  - 自验证：改完后立即运行 lint + typecheck + 相关测试
强制约束：
  - 3次修复失败自动熔断，回传 orchestrator 请求人工介入
  - 修改文件前必须先列清单并获 orchestrator 确认（通过 task 回传）
权限：
  edit/write：ask
  bash：git status*、git diff*、pnpm lint*、pnpm typecheck*、pnpm test*、pnpm vitest*、npx vitest*、npm run lint*、npm run test*：allow
  bash： 其他：ask
  task：deny
输出要求：
  - 修改文件清单（含行号范围）
  - 修改说明（改了什么 + 为什么这样改）
  - 新增/修改的测试
  - lint + typecheck + 测试运行结果
  - 自评风险

强制加载skill：
using-superpowers
systematic-debugging
修复完成后：verification-before-completion

4、审查专家：frontend-bug-reviewer
hidden:true(用户不可见)
temperature：0
核心职责：只读审查修复 diff，验证修复正确性、回归风险、代码质量
禁止行为：修改任何代码、直接提修复建议而不说明理由、跳过审查维度、通过仍有风险的修复
权限：
  edit/write：deny
  bash：git status*、git diff*、git log*、git show*：allow
  bash：rg、grep、cat：allow
  bash：pnpm test*、npm test*、pnpm vitest*、npx vitest*：allow
  bash： 其他：ask
  task：deny
审查维度：
  - 修复是否真正解决了根因（对照 rootcasuse 结论）
  - 是否引入回归（对照已有测试 + 新增边界 case）
  - 是否越权修改（对照 fixer 声明的修改范围）
  - 代码风格/类型安全/空值处理
  - 测试是否充分覆盖修复路径
输出格式：
  - 审查结论：通过 / 有条件通过 / 不通过
  - 必须修复的问题
  - 建议优化项
  - 可接受风险

强制加载skill：
using-superpowers
systematic-debugging
如果主agent声称修好了：verification-before-completion


# 状态机与阶段门控

1、正向路径：intake - preproduce - root_cause - minimal_fix - verify - review - done

2、允许的回退路径：
   reproduce - blocked 终止
   root_cause - reproduce 根因不明 补充复现
   minimal_fix - root_cause 修复范围扩大，回到根因
   verify - minimal_fix 验证失败，重新修复
   review - minimal_fix 审查不通过，重新修复

3、明确禁止的跳转
   reproduce - minimal_fix
   reproduce - review
   root_cause - verify
   root_cause(根因不明) - minimal_fix
   verify  = fail - done

4、并发约束
同一时刻只允许一个active stage

5、todo固定清单：reproduce、root-cause、minimal-fix、verify、review

6、允许的状态：pending、in_progress、done、blocked、skipped

7、更新要求：每次阶段切换了或者收到子agent结果后，都必须更新todo状态


# 阶段门控详解

每个阶段由 orchestrator 驱动，门控逻辑 = 上游产物质检 → 当前阶段执行 → 下游准入判断。

## 通用门控规则（所有阶段共用）

### orchestrator 在每个阶段切换时必须检查：
- upstream_output_quality：上游产物是否满足下游最低所需
- token_exhaustion：本轮上下文是否已不足以执行下一阶段
- circuit_breaker：同一阶段是否已连续失败 3 次（触发熔断，全局终止，todo = blocked）
- user_interrupt：是否收到用户中断指令

### 门控判定函数伪代码（orchestrator 执行）：
````
function gate(prev, next):
    if prev.exit_code != "PASS":
        if prev.retry_count < 3:
            return GOTO prev (retry)
        else:
            return GOTO blocked (circuit breaker)
    if next.entry_conditions_met(prev.output):
        return GOTO next
    else:
        return GOTO fallback(prev, next)
````

### 阶段模板

每个阶段必须由 orchestrator 在当前阶段开始前声明：
- stage_name
- input（来自哪个上游阶段产物）
- exit_criteria（具体可验证的 checklist）
- fallback_on_fail（回退到哪个阶段）
- timeout（最长等待时间，超时视为失败）


## Stage 0：intake（输入，orchestrator 直接执行）

### 入口条件
- 用户提供 DTS 单号 或 自然语言 bug 描述

### orchestrator 动作
1. 若为 DTS 单号：调用 MCP getDTSDetail 拉取工单标题/描述/附件
2. 若为自然语言：提取疑似组件名、错误消息、复现步骤关键字
3. 初始化 todo 清单（reproduce / root-cause / minimal-fix / verify / review），全部 = pending

### 出口条件
- 已获取到可传递给 reproducer 的最小问题描述（≥ 1 条复现线索）
- todo 清单已初始化

### 门控失败处理
- 若 DTS 拉取失败 或 自然语言描述过于模糊无法提取线索 → 向用户提问补充信息，intake 保持 in_progress


## Stage 1：reproduce（复现，dispatch → frontend-bug-reproducer）

### 入口条件（orchestrator 准入检查）
- intake 已完成 → todo[reproduce] = in_progress
- 问题描述至少包含：疑似组件名/文件 + 预期行为 vs 实际行为

### reproducer 执行流程
1. 加载 using-superpowers + systematic-debugging
2. 使用 grep/glob 定位问题涉及的代码文件
3. 搜索已有测试中是否存在相关用例
4. 尝试运行相关测试，确认失败是否可复现
5. 如现有测试无法覆盖，构造最小复现用例（使用 TDD skill）
6. 运行复现用例，截取失败输出

### 出口条件（orchestrator 必须逐条验证，缺一不可）
- [ ] 提供了可独立运行的复现步骤（命令 + 参数）
- [ ] 提供了实际输出 vs 预期输出的对比
- [ ] 复现环境信息（Node 版本、浏览器版本等，如适用）
- [ ] 复现步骤可被 rootcasuse 直接使用（无需额外猜测）

### 门控失败 → 回退路径
- 无法复现 → 重试 1 次（拓宽搜索范围）
- 2 次仍无法复现 → todo[reproduce] = blocked，orchestrator 向用户汇报并请求更多信息，流程暂停
- 禁止 → 直接跳到 minimal-fix（无复现不可修复）


## Stage 2：root_cause（根因分析，dispatch → frontend-bug-rootcasuse）

### 入口条件（orchestrator 准入检查）
- reproduce 已完成（todo[reproduce] = done）
- reproduce 输出中包含可执行复现步骤 + 失败输出

### rootcasuse 执行流程
1. 加载 using-superpowers + systematic-debugging
2. phase1 根因调查：从复现输出中的报错点出发，用 grep/glob 定位相关源码
3. phase1 产出：报错代码位置（文件:行号）、相关调用链入口
4. phase2 模式分析：在代码库中搜索相似模式的代码（对比正确/错误的处理方式）
5. phase2 产出：差异对比、潜在根因假设列表
6. phase3 假设验证：对每个假设做代码级验证（git log 查变更历史、git diff 查最近改动、追溯数据来源）
7. phase3 产出：已验证/已排除的假设 + 置信度
8. 汇总输出根因结论

### 出口条件（orchestrator 必须逐条验证）
- [ ] 根因一句话总结（格式："问题根因是 X，因为 Y"）
- [ ] 完整证据链可追溯：复现输出 → 报错行 → 调用链 → 数据来源 → 根因
- [ ] 每个证据节点都标注文件:行号
- [ ] 置信度评估不为空，且当置信度 = "低" 时，必须列出仍需确认的假设
- [ ] 影响范围已标注（受影响模块/组件/接口清单）

### 门控失败 → 回退路径
- 置信度 = 低 且无更多代码线索 → 回退到 reproduce，要求补充复现信息
- 置信度 = 中/高 但证据链不完整 → 重新执行 root_cause（重试 1 次）
- 2 次仍不达标 → todo[root_cause] = blocked，orchestrator 向用户汇报根因分析结果并要求人工判断
- 禁止 → 根因不明直接跳 minimal-fix


## Stage 3：minimal_fix（实施修复，dispatch → frontend-bug-fixer）

### 入口条件（orchestrator 准入检查）
- root_cause 已完成（todo[root_cause] = done）
- 根因结论置信度 ≥ 中
- 根因结论中有明确的代码定位（文件:行号）

### fixer 执行流程
1. 加载 using-superpowers + systematic-debugging
2. 列修改文件清单 + 行号范围 → 通过 task 回传 orchestrator 确认
3. orchestrator 审查修改范围是否与根因一致 → 确认后方可继续
4. 先写回归测试（补充覆盖根因路径的测试用例）
5. 运行新测试 → 确认新测试 FAIL（证明测试能捕获 bug）
6. 实施最小修复代码
7. 运行新测试 → 确认新测试 PASS
8. 运行全量 lint + typecheck + 相关测试套件
9. 加载 verification-before-completion → 验证所有检查通过

### 出口条件（orchestrator 必须逐条验证）
- [ ] 修改文件与 orchestrator 确认的清单一致（无越权修改）
- [ ] 新增测试覆盖了根因路径
- [ ] lint 通过（无新增警告）
- [ ] typecheck 通过
- [ ] 所有相关测试 PASS（含已有 + 新增）
- [ ] 修改说明包含：改了什么 + 为什么这样改

### 门控失败 → 回退路径
- 修改范围超出根因范围 → 要求 fixer 缩减范围，重新来
- 测试失败 → 检查是否修复代码有问题，重试
- lint/typecheck 失败 → 要求 fixer 修复
- 3 次失败 → 自动熔断，todo[minimal_fix] = blocked，orchestrator 向用户汇报

### 熔断机制详解
- orchestrator 维护一个 per-stage retry counter
- retry_count ≥ 3 时 → 当前 stage = blocked → 全局流程 blocked
- blocked 后 orchestrator 只能等待用户决策：继续 / 放弃 / 手动接管


## Stage 4：verify（自验证，fixer 内已完成，orchestrator 复核）

### 说明
verify 阶段在 Stage 3 中已由 fixer 执行（lint + typecheck + 测试），不另设独立子 agent。orchestrator 在此阶段做复核。

### 入口条件
- minimal_fix 已完成（todo[minimal_fix] = done）

### orchestrator 复核动作
- [ ] 检查 fixer 输出的 lint/typecheck/测试结果是否完整
- [ ] 抽查关键测试是否确实 PASS（至少抽查 1-2 条）
- [ ] 检查修改是否越权（diff 文件清单 vs 确认清单）

### 出口条件
- [ ] 所有复核项通过

### 门控失败 → 回退路径
- 复核不通过 → 回退到 minimal_fix，附带具体问题说明
- 2 次复核仍不通过 → todo[verify] = blocked，进入人工介入


## Stage 5：review（审查，dispatch → frontend-bug-reviewer）

### 入口条件（orchestrator 准入检查）
- verify 已完成（todo[verify] = done）
- fixer 的 diff 产物完整可读（git diff 非空）

### reviewer 执行流程
1. 加载 using-superpowers + systematic-debugging
2. 获取 fixer 的修改 diff
3. 对照 root_cause 的根因结论 → 判断修复是否真正解决根因
4. 检查测试覆盖 → 运行测试确认全部 PASS
5. 审查代码质量（风格/类型安全/空值处理）
6. 检查是否越权修改
7. 输出分级结论

### 出口条件（orchestrator 必须逐条验证）
- [ ] 审查结论已输出（通过 / 有条件通过 / 不通过）
- [ ] 每个结论都附带具体理由（哪好/哪不好/为什么）

### 门控失败 → 回退路径
- 不通过 → 回退到 minimal_fix（附带具体问题清单）
- 有条件通过 → 回退到 minimal_fix（仅处理"必须修复"项）
- 2 次仍不通过 → todo[review] = blocked，orchestrator 向用户汇报并附审查结论
- 禁止 → 审查不通过仍标记 done


## Stage 6：done / blocked（终态）

### done 的准入条件
- 全部 5 个 todo 状态 = done
- reviewer 结论 = 通过
- orchestrator 确认无遗漏检查项

### done 后 orchestrator 输出
- 问题摘要 + 根因一句话
- 修改文件清单
- 测试证明（新增/修改的测试 + 运行结果）
- reviewer 审查结论

### blocked 的触发条件
- 任一 stage 连续失败 3 次（自动熔断）
- reproduce 无法复现且用户无更多信息
- root_cause 置信度持续为低且无更多代码线索
- 用户主动中断

### blocked 后 orchestrator 输出
- 当前卡在哪个阶段
- 已完成阶段的产物
- 失败原因 + 重试次数
- 请求用户决策选项：继续 / 放弃 / 手动接管


# 周期检测与循环防护

orchestrator 必须在内存中维护 transition_history 列表，每次阶段切换追加一条记录：
格式：{from, to, timestamp, reason}

检测规则：
- 同一 from→→to 连续出现 3 次 → 判定为死循环 → 强制 blocked
- 例：minimal_fix → review → minimal_fix → review → minimal_fix → review → blocked


# Agent 间通信回执契约

所有 subagent 与 orchestrator 之间的通信必须遵守本契约。契约由 orchestrator 在每次收到 subagent 回执后强制校验，校验不通过则直接打回（REJECT），不计入重试次数。

## 一、通用响应信封（Universal Response Envelope）

所有 subagent 返回给 orchestrator 的最终消息，必须包含以下 JSON envelope（置于消息末尾或以 fenced code block 包裹）：

```json
{
  "header": {
    "agent": "frontend-bug-reproducer",
    "stage": "reproduce",
    "status": "PASS | FAIL | PARTIAL",
    "retry_count": 0,
    "timestamp": "ISO 8601"
  },
  "ref": {
    "upstream_stage": "intake",
    "upstream_status": "PASS"
  },
  "payload": { ... },
  "meta": {
    "warnings": [],
    "assumptions": [],
    "needs_user_input": false
  }
}
```

### 字段约束

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| header.agent | string | 是 | 必须精确匹配当前 subagent 名称 |
| header.stage | string | 是 | 必须精确匹配当前阶段名（reproduce / root_cause / minimal_fix / review） |
| header.status | enum | 是 | 仅允许 PASS / FAIL / PARTIAL |
| header.retry_count | int | 是 | 从 0 开始，每次同阶段重试 +1，上限 2 |
| header.timestamp | string | 是 | ISO 8601 格式 |
| ref.upstream_stage | string | 是 | 上一阶段名，必须与 orch 记录一致 |
| ref.upstream_status | string | 是 | 上游阶段出口状态，必须为 PASS |
| payload | object | 是 | 阶段特定载荷，schema 见下文 |
| meta.warnings | []string | 否 | 执行过程中的非致命警告 |
| meta.assumptions | []string | 否 | 本阶段做出的合理默认假设 |
| meta.needs_user_input | bool | 否 | 是否需要用户补充信息才能继续 |

### 信封校验规则（orchestrator 收到回执后立即执行）

1. **JSON 可解析** — 不是合法 JSON → REJECT（"回执格式错误：无法解析 JSON"）
2. **header 完整** — 缺少 header 或 header 内必填字段 → REJECT
3. **header.agent 一致** — 与 orch 记录的 dispatch target 不一致 → REJECT（"agent 身份不匹配"）
4. **header.stage 一致** — 与当前 todo in_progress 阶段不一致 → REJECT
5. **header.status 合法** — 不在 PASS/FAIL/PARTIAL 枚举内 → REJECT
6. **ref.upstream_stage 正确** — 与 orch 记录的上游阶段不一致 → REJECT
7. **payload 存在** — 为 null 或缺失 → REJECT


## 二、状态码语义

| 状态码 | 语义 | orchestrator 动作 |
|--------|------|-------------------|
| PASS | 阶段完成，产物齐全 | 进入门控判定，准备下一阶段 |
| FAIL | 阶段执行失败，无法继续 | retry_count +1，若 < 3 则重试本阶段；≥ 3 则熔断 blocked |
| PARTIAL | 阶段部分完成，但缺少某些产出 | 检查 meta.assumptions + needs_user_input，决定补充信息还是回退上游 |

### PARTIAL 特殊处理规则

当 status = PARTIAL 时，orchestrator 必须检查：
- 若 `needs_user_input == true` → 暂停当前 todo，向用户展示问题，等待回复
- 若 `needs_user_input == false` 且 `assumptions` 非空 → 评估假设合理性，合理则按 PASS 继续，不合理则按 FAIL 处理
- PARTIAL 不计入熔断计数器

### 禁止的状态码
- 禁止使用 OK / ERROR / WARNING / SUCCESS 等非标准状态码
- 禁止返回空 header 或 header.status = null
- 禁止在 status = PASS 时 payload 关键字段为空


## 三、各阶段 Payload Schema

### Stage 1：reproduce → orchestrator

```json
{
  "repro_steps": {
    "command": "npx vitest run path/to/test.test.ts -t 'test name'",
    "description": "如何运行复现"
  },
  "output": {
    "actual": "实际输出（截取关键部分）",
    "expected": "预期输出",
    "diff": "差异点描述"
  },
  "env": {
    "node": "v20.x",
    "browser": "Chrome 120（如适用）",
    "os": "macOS 14"
  },
  "code_locations": [
    { "file": "src/xxx.ts", "line": 42, "relevance": "报错行" }
  ]
}
```

orchestrator 校验 — 以下任一项为空或缺失 → REJECT：
- `repro_steps.command`
- `output.actual`
- `output.expected`
- `code_locations` 数组为空

### Stage 2：root_cause → orchestrator

```json
{
  "root_cause": {
    "summary": "问题根因是 X，因为 Y",
    "confidence": "high | medium | low"
  },
  "evidence_chain": [
    { "node": "复现输出", "file": "test/xxx.test.ts", "line": 15, "finding": "测试断言失败，期望 A 实际 B" },
    { "node": "报错行", "file": "src/xxx.ts", "line": 42, "finding": "函数返回 null 而非预期对象" },
    { "node": "调用链追溯", "file": "src/yyy.ts", "line": 88, "finding": "上游传入空数组未做防御" },
    { "node": "根因", "file": "src/yyy.ts", "line": 88, "finding": "缺少空值守卫，导致下游崩溃" }
  ],
  "impact_scope": {
    "modules": ["src/xxx.ts", "src/yyy.ts"],
    "components": ["PaymentForm"],
    "apis": ["POST /api/checkout"]
  },
  "pending_hypotheses": []
}
```

orchestrator 校验：
- `root_cause.summary` 必须包含 "根因" 或 "root cause" 字样（或等价中文表述）
- `root_cause.confidence` 在 [high, medium, low] 枚举内
- `evidence_chain` 数组至少 2 个节点
- 每个 evidence 节点必须包含 file + line + finding
- 若 `confidence == low`，必须同时有 `pending_hypotheses` 非空

### Stage 3：minimal_fix → orchestrator（两次通信）

#### 第一次通信：修改确认请求（fixer → orchestrator，确认修改范围）

fixer 发送确认请求，orchestrator 审查后回复 approve/deny：

```json
{
  "type": "fix_confirmation_request",
  "planned_changes": [
    { "file": "src/xxx.ts", "lines": "40-45", "reason": "添加空值守卫", "change_type": "modify" },
    { "file": "src/xxx.test.ts", "lines": "80-95", "reason": "补充回归测试", "change_type": "add" }
  ],
  "impact_summary": "在 src/xxx.ts:42 添加空值检查，新增 1 个回归测试"
}
```

orchestrator 校验：
- 修改范围是否与 root_cause 的 impact_scope 匹配（不能越权）
- 若 planned_changes 中出现了 impact_scope 之外的文件 → REJECT（"修改范围超出根因影响范围"）

orchestrator 回复格式：
```json
{
  "type": "fix_confirmation_response",
  "decision": "approved | denied",
  "reason": "原因说明（deny 时必须）",
  "allowed_files": ["src/xxx.ts", "src/xxx.test.ts"]
}
```

#### 第二次通信：修复完成回执

```json
{
  "changes": [
    { "file": "src/xxx.ts", "lines": "40-44", "description": "添加空数组守卫", "type": "modify" },
    { "file": "src/xxx.test.ts", "lines": "80-95", "description": "空数组边界测试", "type": "add" }
  ],
  "verification": {
    "lint": { "status": "PASS", "output": "0 errors, 0 warnings" },
    "typecheck": { "status": "PASS", "output": "no type errors" },
    "tests_added": [
      { "file": "src/xxx.test.ts", "test_name": "returns empty array when input is empty", "result": "PASS" }
    ],
    "tests_existing": "All 42 existing tests PASS"
  },
  "self_risk_assessment": "低风险：仅添加空值守卫，不影响正常路径"
}
```

orchestrator 校验：
- `changes` 文件清单必须与 `fix_confirmation_response.allowed_files` 一致
- `verification.lint.status` 必须为 PASS
- `verification.typecheck.status` 必须为 PASS
- `verification.tests_added` 至少 1 条

### Stage 5：review → orchestrator

```json
{
  "verdict": "approved | conditional_approved | rejected",
  "checklist": {
    "root_cause_addressed": { "result": true, "detail": "..." },
    "no_regression": { "result": true, "detail": "..." },
    "no_scope_creep": { "result": true, "detail": "..." },
    "code_quality": { "result": true, "detail": "..." },
    "test_coverage": { "result": true, "detail": "..." }
  },
  "must_fix": [],
  "suggestions": [],
  "acceptable_risks": []
}
```

orchestrator 校验：
- `verdict` 必须在 [approved, conditional_approved, rejected] 枚举内
- `checklist` 5 个维度必须全部存在
- 若 `verdict == rejected`，`must_fix` 必须非空
- 若 `verdict == conditional_approved`，`must_fix` 必须非空且 `suggestions` 非空


## 四、Contract 非法处理流程

当 orchestrator 校验不通过时，执行标准打回流程：

```
orchestrator RECEIVE response from subagent
  ↓
VALIDATE envelope → INVALID → REJECT(response, reason)
  ↓ VALID
VALIDATE payload schema → INVALID → REJECT(response, reason)
  ↓ VALID
ACCEPT → 进入门控判定
```

### REJECT 回复格式（orchestrator → subagent）

```json
{
  "type": "contract_rejection",
  "reject_reason": "具体违反哪条规则，期望格式是什么",
  "violated_field": "header.status 或 payload.root_cause.summary 等",
  "received_value": "实际收到的值（截取关键部分）",
  "action_required": "重新组织回执，遵守契约格式"
}
```

### 打回规则

| 违规次数 | 动作 |
|---------|------|
| 第 1 次 | REJECT + 明确告知违反哪条规则，要求重新输出 |
| 第 2 次 | REJECT + 提供正确格式示例 |
| 第 3 次 | REJECT + 该 subagent 此轮 dispatch 记 FAIL，retry_count + 1 |

注意：contract 违规不计入阶段熔断（retry_count 是针对阶段执行质量的计数，contract 违规属于格式问题）。

### 常见违规示例

| 违规 | 示例 | 正确格式 |
|------|------|---------|
| status 非法 | "status": "OK" | "status": "PASS" |
| agent 不匹配 | "agent": "frontend-bug-fixer" | stage=reproduce 时代理应为 reproducer |
| 缺 payload | payload: null | 必须填入对应 stage 的 schema 数据 |
| 证据链不完整 | evidence_chain 只有 1 个节点 | 至少 2 个节点 |
| confidence 非法 | "confidence": "不确定" | "confidence": "low" |
| envelope 位置错误 | 埋在大段自然语言中无法定位 | 必须为独立 fenced code block 或消息末尾 JSON |

