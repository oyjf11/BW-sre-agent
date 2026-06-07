# Vibe Dev Toolkit（hoo-desk 全流程研发 Harness 简版）设计

> 本文是「AI 辅助研发提效工具包」的**可演示简版**设计稿。
> 真实工具包运行在企业内网（OpenCode 载体，80+ skills，主链路+贯穿面均在跑），
> 是 `.interview/harness-engineering-体系认知.md` 那套产研 harness 的 v1 落地。
> 本简版在真实的 Vue2 项目 **hoo-desk** 上复刻其全流程骨架，**测试域做到最深**，
> 并补全真实工具包偏薄的 **Bad Case 闭环**。
>
> **双目标**：(1) 面试可讲、可 demo 的真实产物；(2) 验证我对 harness 设计内核的动手能力。

---

## 0. 定位与边界

### 0.1 这是什么

一个**做进 hoo-desk 项目**的 OpenCode 配置包 + 配套 TS/Node 执行脚本，把"需求→设计→拆分→开发→审查→测试→交付"全流程在结构上复刻一遍，骑在一个统一的**确定性脊柱**（编排器+状态机+契约+恢复）上。

### 0.2 深度分配（核心取舍）

全流程**结构上都复刻**（证明懂团队级基础设施），但**深度按面试价值分配**——不是每个节点都做生产级，否则会稀释王牌、陷入老项目构建泥潭。

| 阶段 | 内容 | 深度 | 面试价值 | 本期 |
|---|---|---|---|---|
| **A 脊柱** | 编排器 / 状态机(task.json) / 契约信封 / 事件日志 / 中断恢复 / 任务选择算法 | 真实 | 中（控制权·状态） | ✅ 本期 |
| **B 测试域 + Bad Case** ★ | AC→生成→真跑 Playwright→三防线校验 + compound/research | **最深** | **最高** | ✅ 本期 |
| C 前半段 | 需求→设计(AC) + 人机门控四选项 + 任务拆分 DAG | 中 | 高（门控·DAG） | ⏳ 后续 spec |
| D 开发循环+审查 | 自愈循环 + 分级修复（受控小改动） | 薄/受控 | 中 | ⏳ 后续 spec |

**本期 spec 范围 = A + B**。AC 先用**手写 JSON 输入**（C 阶段再补"需求→AC"的上游生成）。

### 0.3 第一性约束：工具链零业务耦合，适配任何工程

**这是凌驾于一切之上的架构约束**：本工具包的目标是适配任意前端工程，不是"测 hoo-desk"。
因此 `tools/vibe` 工具链内核**绝不能内嵌任何项目专属知识**——不知道 hoo-desk、不知道 login、
不知道 isForget、不知道 element-ui。所有项目专属信息从外部"项目档案（project profile）"喂入。

```
┌────────────────────────────────────────────────────────────┐
│  工具链内核 tools/vibe  （通用 · 零业务知识）                  │
│  orchestrator / contracts / coverage-checker / badcase       │
│  只认两样东西: ① AC schema  ② Playwright 结构化结果           │
└──────────────────────────┬─────────────────────────────────┘
                           │ 靠"框架探测 + 适配矩阵"对接任意工程
              ┌────────────┴────────────┐
              │ 探测器 detect() → framework 枚举 (vue2/vue3/react16±) │
              │   → 预置 profile + 选择器适配器 (见 §2.5)             │
              └─────────────────────────┘
```

**判定准则**：`tools/vibe/src/**` 里出现任何 `hoo-desk` / `login` / `isForget` 字样，即为架构违规
（`element-ui`/`antd` 等**框架级**词可出现在适配器内，因其是有限枚举的通用插件）。
靶子 login.vue 只是**本期验证工具链的第一个真实样本**，不是工具链的一部分。
换工程 = 探测器自动出 profile；换框架 = 命中矩阵另一适配器，工具链脊柱一行不改。

### 0.4 可全量补全：脊柱先行的承诺

本期只做局部（A+B），但设计保证后期能平滑补全 C/D/贯穿面。三条保证：

1. **脊柱先行**：A 阶段建好确定性脊柱（编排器/状态机/契约/恢复）。C/D 是往同一条脊柱
   **挂新节点**，非另起炉灶。`task.json` 的 `type` 字段本期只有 `test`，后期加
   `design`/`develop`/`review` 即可。
2. **契约隔离**：节点间靠契约信封交接（内核③），新增节点只要产出符合契约，脊柱即可调度，
   不影响存量节点。
3. **路线图锁定**：§6 的 Phase 1→4 即施工图，每阶段独立 spec→plan，互不阻塞。

> 诚实前提：平滑补全的代价取决于**脊柱这一期是否设计稳**。故本期把脊柱（A）当作最该认真做的
> 地基——它虽非面试王牌（测试域才是），却是"后期能否全量补全"的承重墙，因此标注为「真实深度」。

### 0.3 不做什么（YAGNI）

- ❌ 不对接 DevOps 需求平台（C 阶段用手写需求替代）
- ❌ 不做任务拆分 DAG / 开发循环 / 代码审查（C/D 阶段）
- ❌ 不碰 hoo-desk 老构建链（webpack3）去生成业务代码——开发域是泥潭，ROI 最低
- ❌ 不做交付 MR / 自动更新
- ❌ 不引入数据库——状态用文件（task.json / events.jsonl），贴合真实工具包的"本地沉淀"形态

---

## 1. 背景：要复刻的真实链路（已澄清事实）

以下是经访谈确认的真实工具包形态，简版据此复刻。**【真跑】/【愿景】标注是面试诚实线，不得混淆。**

```
0  需求接入：对接 DevOps 需求平台，/it-design <需求单号> 拉取        【真跑·我主导】
1  需求分析：理解→歧义→澄清(agent 反问,参考 brainstorm 模式)        【真跑·我主导】
   └─ 人机确认门控①：确认 / 修改 / 重新设计 / 查看详细文档（四选项）
2  方案设计：结晶出 AC（JSON，带优先级，喂给任务拆分）              【真跑·我主导】
   └─ 人机确认门控②：同上四选项
   └─ 反证 Agent 挑刺方案                                          【愿景·未上线】
3  任务拆分：DAG 依赖编排（前/后端分流，定向知识库），优先级定序     【真跑·我主导】
   └─ 状态机 pending→doing→passing/failing
   └─ 任务选择算法：恢复选 doing 中优先级最高；多 doing 按优先级+顺序；
      无 doing 按优先级选 pending 第一
4  开发循环：/it-sub-developer，5s 轮询 task.json，30min 超时熔断     【真跑·我了解】
   └─ 单测 + 构建校验（非 AC 验收）；构建失败→/it-build-fix；
      测试失败→自动修（有熔断 + 禁改测试）
5  代码审查：分级修复 critical/high 自动修，med/low 不阻塞，5 次熔断  【真跑·我了解】
   └─ 平时自动放行，熔断才交人
6  系统测试：AC 驱动 E2E + 三道防线 ★（主战场）                      【真跑·我主导】
7  交付：执行报告 + workflow_report.md；人工提交 MR→CR→合入          【真跑·我主导】
   └─ /learning-compound（YAML 沉淀本地）+ /learning-researcher（检索） 【真跑】

贯穿面：
A  中断恢复（内建在任务选择算法 + task.json 持久化）
B  质量门禁（每节点准入/出口 + 分级 + 熔断）
C  知识沉淀（有数据上报 + 本地 compound/research；中心化回流  【偏愿景】）
```

### 1.1 测试域三防线（面试��牌的理论内核）

源于一个真实面试失败问题的系统化回答：「断言怎么写 / 怎么避免 happy path / 大模型没测却说测了」。

**核心命题**：真执行+机器证据只能消灭"执行层幻觉"，"断言层"和"覆盖层"幻觉必须另设两道结构来堵，**三道都不依赖 LLM 自我报告**。

| 幻觉层 | 面试官问法 | 防线 | 机制 |
|---|---|---|---|
| 执行层：没跑却说跑了 | "没测却说测了" | ① 真执行+机器证据 | trace.zip / 退出码 / 截图，LLM 伪造不了 |
| 断言层：跑了但断言空洞 | "断言怎么写" | ② AC 驱动断言 | 每条断言溯源到结构化 AC 的 expected |
| 覆盖层：声称覆盖实则没生成 | "怎么避免 happy path" | ③ AC↔断言双向映射 | 有 AC 无断言=缺口；有断言未执行=造假 |

---

## 2. 第一阶段（A+B）总体架构

### 2.1 数据流

```
                       ┌──────────────────────── 脊柱（确定性）─────────────────────────┐
[手写 AC.json] ──┐     │  orchestrator → 读 task.json → 任务选择算法 → 派发 → 收契约信封  │
                 │     │           ↑                                    ↓                │
                 └────►│      events.jsonl ◄──── 每步事件 ────────  契约校验/门控        │
                       └────────────────────────────┬──────────────────────────────────┘
                                                     │ 派发测试域任务
                       ┌─────────────────────────────▼─────────────────────────────────┐
                       │ test-generator: AC → Playwright 用例(.spec.ts, 每条带 ac_id)    │
                       │       ↓                                                         │
                       │ [真执行] npx playwright test → trace.zip / 退出码 / 截图        │ 防线①
                       │       ↓                                                         │
                       │ coverage-checker(确定性脚本): AC ↔ 断言 双向映射                │ 防线②③
                       │       ↓                                                         │
                       │ 失败/造假/缺口 → test-analyst 归因 → Bad Case(yaml)             │
                       └─────────────────────────────┬─────────────────────────────────┘
                                                     │
            /learning-compound 写入 .vibe/badcases/*.yaml ──► 下次 /learning-researcher 检索注入
```

### 2.2 第一个验证样本：`hoo-desk/src/views/public/login.vue`

> ⚠️ 它是**本期用来验证工具链通用能力的第一个真实样本**，不是工具链的内置目标。
> 工具链通过 §2.5 的 project profile 认识它，profile 之外工具链对它一无所知（见 §0.3）。

**选它当首个样本的理由**（天然含 happy-path 陷阱与覆盖盲区，无需埋 bug）：

- **三态表单**：`isForget` ∈ {1 登录, 2 忘记密码, 3 设置密码}，`rulesList` computed 随状态切换 formRules1/2/3。LLM 极易只测 `isForget==1` 的正常登录，漏掉状态 2/3 → **happy path 活靶**。
- **多条可断言的客户端校验**：
  - `check()`：空手机号 / 空密码 → toast 报错（login.vue:545-557）
  - `toFindPsw()`：两次新密码不一致 → "两次密码输入不一致"（login.vue:521-523）
  - `toGetCode()`：未填手机号点获取验证码 → 报错（login.vue:493-498）
- **覆盖盲区天然存在**：异常路径（如两次密码不一致）LLM 默认不生成 → 防线③双向映射可现场抓出缺口。

> 样本在本机 `npm run dev` 可起（已确认），Playwright 打真实页面 → 防线①拿真证据，不降级。
> **通用性验收**：profile 里把 page/route/选择器策略换成另一个 hoo-desk 页面（如 `course/creat_class.vue`），
> 工具链不改一行即可生成并校验——本期验收标准 §8 含此项。

### 2.3 技术栈

| 部分 | 技术 |
|---|---|
| 工具链（orchestrator / generator / checker / analyst 脚本） | **TypeScript + Node** |
| 契约校验 | **zod**（hoo-desk/.opencode 已用 zod，复用） |
| E2E 执行 | **Playwright（TS）** |
| 被测样本 hoo-desk | Vue2 + JS（原样，不改） |
| 状态/沉淀 | 文件：`task.json` / `events.jsonl` / `badcases/*.yaml` |

### 2.5 项目适配层：框架自动探测 + 有限适配矩阵（通用性的关键）

通用性不靠"应对任意未知工程"，而靠**有限框架矩阵的确定性探测**——这贴合真实约束（公司框架固定）。
工具链对工程的认识 = 自动探测出的 `framework` 枚举 + 对应预置策略，**不读业务源码结构假设**。

**探测器（确定性，不靠 LLM）**：读 `package.json` 依赖版本，落入四枚举之一：

```
detect(project_root) → framework
├── vue2       vue ^2.x                     → 适配器: element-ui / vux 选择器策略
├── vue3       vue ^3.x                     → 适配器: element-plus / antd-vue
├── react16-   react <16.8 (class 组件为主)  → 适配器: 类组件 / enzyme 式
└── react16+   react >=16.8 (hooks)         → 适配器: antd / testing-library 式
```

> react 以 16.8（hooks 分水岭）为界分两类：16- 以 class 组件 + 生命周期为主，选择器/断言偏组件实例；
> 16+ 以函数组件 + hooks 为主，走 testing-library「按用户可见行为查询」思路。两者测试策略不同，故分列。

**适配矩阵**：每个 framework 枚举映射一个**选择器策略适配器**（输入 AC 的语义锚点，输出该框架/UI 库的
Playwright 选择器与断言风格），适配器是工具链内的通用插件，**不含具体页面知识**。

**profile 的新定位**：从"必填手写"降级为"**探测结果 + 可选覆盖**"。探测器产出 `.vibe/profile.json`，
用户通常零配置；仅当探测不准或需覆盖个别字段（如自定义 toast 选择器、非标启动命令）时手改。

```jsonc
// .vibe/profile.json （hoo-desk: 探测器自动生成,用户未改动）
{
  "project": "hoo-desk",
  "framework": "vue2",                  // ← 探测器从 package.json vue ^2.5.2 推出
  "dev": { "command": "npm run dev", "ready_log": "Compiled successfully",
           "base_url": "http://localhost:8080", "timeout_ms": 180000 },
  "ui": {
    "adapter": "vue2",                  // ← 默认随 framework; 可手动覆盖为 vux 等
    "toast_selector": ".el-message",     // ← 适配器默认值,可覆盖
    "input_strategy": "placeholder"
  },
  "acceptance_dir": ".vibe/specs/acceptance",
  "e2e_out_dir": "e2e"
}
```

**判定准则不变**：`tools/vibe/src/**` 出现 `hoo-desk`/`login`/`isForget` 即违规。
但适配器内可以有 `element-ui`/`antd` 这类**框架级**知识（因为它们是有限枚举的通用插件，非项目专属）。
换工程 = 探测器自动出 profile；换框架 = 命中矩阵里另一个适配器；**login/isForget 永不进工具链。**

**本期落地**：探测器实现四枚举的识别逻辑 + **vue2 适配器做扎实**（因为靶子 hoo-desk 是 vue2）；
vue3 / react16± 适配器**留接口 + 骨架**（枚举能识别、策略可注册），本期不填实现——
这是"对扩展开放"的典型，后期补其他框架只加适配器，不动探测器与脊柱。

### 2.4 目录结构（做进 hoo-desk）

```
hoo-desk/
├── .opencode/                          # 已存在,复用,不破坏
│   ├── command/                        # 新增命令入口（目录单复数以 hoo-desk/.opencode 既有约定为准,
│   │   ├── vibe-test.md                #   实现首步先确认: 已知其用 skill/ 单数,command/agent 同步对齐）
│   │   ├── learning-compound.md        # Bad Case 沉淀
│   │   └── learning-researcher.md      # Bad Case 检索
│   ├── agent/                          # 新增 agent 定义
│   │   ├── test-orchestrator.md        # 编排器(确定性,不写代码)
│   │   ├── test-generator.md           # AC → Playwright 用例
│   │   └── test-analyst.md             # 失败归因 → Bad Case
│   └── skill/
│       └── task-management/            # 已存在,本期复用其状态机思想
├── .vibe/                              # 新增: 简版运行时数据
│   ├── specs/acceptance/*.ac.json      # 手写 AC 输入
│   ├── runtime/task.json               # 任务状态机
│   ├── runtime/events.jsonl            # 事件日志
│   ├── reports/<run>/                  # trace/截图/双向映射报告
│   └── badcases/*.yaml                 # Bad Case 库
├── tools/vibe/                         # 新增: TS/Node 工具链
│   ├── src/orchestrator.ts             # 脊柱: 状态机+选择算法+恢复
│   ├── src/contracts.ts                # zod schema (信封/AC/用例/报告/profile)
│   ├── src/detect.ts                   # 框架探测器 → vue2/vue3/react16± 枚举
│   ├── src/adapters/                   # 选择器策略适配器(可含框架级知识,如 element-ui)
│   │   ├── vue2.ts                     #   本期做扎实
│   │   ├── vue3.ts                     #   本期留骨架+接口
│   │   ├── react16-minus.ts            #   本期留骨架+接口
│   │   └── react16-plus.ts             #   本期留骨架+接口
│   ├── src/coverage-checker.ts         # 防线②③: AC↔断言双向映射
│   ├── src/badcase.ts                  # compound/research 实现
│   ├── tests/                          # 工具链自身的单元测试(Vitest)
│   └── package.json                    # 独立于 hoo-desk 的依赖
└── e2e/                                # 新增: 生成的 Playwright 用例落地处
    └── login/*.spec.ts
```

> **隔离原则**：简版所有新增物集中在 `.vibe/`、`tools/vibe/`、`e2e/`、`.opencode/{command,agent}` 下，**不修改 hoo-desk 任何业务源码与构建配置**，保证靶子可独立运行、简版可整体移除。

---

## 3. 脊柱（A）详细设计

### 3.1 task.json 状态机

```jsonc
{
  "run_id": "run-20260607-login-001",
  "created_at": "<注入,非脚本生成>",
  "tasks": [
    {
      "id": "T1",
      "type": "test",                    // 本期只有 test 类型;C/D 阶段扩展
      "ac_refs": ["AC-LOGIN-01", "AC-LOGIN-02"],
      "priority": 1,                      // 数字越小越优先
      "seq": 1,                           // 同优先级内的顺序
      "status": "pending",                // pending→doing→passing/failing
      "attempts": 0,
      "max_attempts": 3
    }
  ]
}
```

**状态枚举**：`pending → doing → passing | failing`（与真实工具包一致）。

### 3.2 任务选择算法（确定性，复刻真实逻辑）

```
selectNext(tasks):
  doing = tasks.filter(status == "doing")
  if doing.nonEmpty:                       # —— 中断恢复路径
      return doing.sortBy(priority, seq).first   # 选 doing 中优先级最高
  pending = tasks.filter(status == "pending")
  if pending.nonEmpty:
      return pending.sortBy(priority, seq).first  # 无 doing → pending 第一
  return null                              # 全部终态 → 结束
```

**这是内核①（控制权归确定性系统）+ ⑥（状态外置可恢复）的落点**：下一步干什么由此算法算出，**不问 LLM**；崩溃重启后读 task.json 即可从 `doing` 精确续跑。

### 3.3 契约信封（zod 强制校验）

所有 agent 回执必须以 JSON 信封结尾，orchestrator 用 zod 校验，不合规打回（不计入任务重试）：

```jsonc
{
  "header": { "agent": "test-generator", "stage": "generate",
              "status": "PASS|FAIL|PARTIAL", "attempt": 0 },
  "payload": { /* stage-specific, 见 §4 */ },
  "meta": { "warnings": [], "needs_user_input": false }
}
```

### 3.4 事件日志 events.jsonl

每个状态转换、每次派发、每次校验结果 append 一行 `{ts, type, task_id, from, to, detail}`。
**用途**：可观测（内核⑦）+ 中断恢复时重建上下文。`ts` 由调用方注入（脚本内禁用 Date.now 以保证可重放测试）。

---

## 4. 测试域 + 三防线（B）详细设计

### 4.1 AC 输入格式（`.vibe/specs/acceptance/login.ac.json`）

```jsonc
{
  "feature": "login",
  "target": { "page": "src/views/public/login.vue", "route": "/login" },
  "criteria": [
    {
      "id": "AC-LOGIN-01",
      "priority": 1,
      "desc": "空手机号点击登录时,提示'请输入账号'",
      "given": "isForget=1 登录态, 手机号为空",
      "when": "点击登录按钮",
      "then": { "observable": "toast", "expect_text": "请输入账号" }
    },
    {
      "id": "AC-LOGIN-04",
      "priority": 2,
      "desc": "设置密码态,两次密码不一致时提示",
      "given": "isForget=3 设置密码态, 两次密码不同",
      "when": "点击确定",
      "then": { "observable": "toast", "expect_text": "两次密码输入不一致" }
    }
    // ...covering isForget 1/2/3 三态,刻意包含异常路径
  ]
}
```

**关键**：`then.observable` + `expect_text` 是**机器可断言的预期**，断言由此而来——不是 LLM 拍脑袋。这是防线②的地基。

> **通用性注意**：AC 只描述**语义**（"toast 显示某文案"），不写具体选择器（`.el-message`）。
> 选择器由 §2.5 profile 的 UI 适配器在生成时注入。这样同一份 AC 语义可跨 UI 框架复用，
> 工具链不被 element-ui 绑死。`target.page/route` 也以 profile 的 base_url 为前缀拼接。

### 4.2 防线①：真执行 + 机器证据

- test-generator 产出 `e2e/login/*.spec.ts`（真 Playwright 用例）。
- orchestrator **只认** `npx playwright test --reporter=json` 的退出码 + `trace.zip` + 截图。
- agent 回执里口头说"PASS"**不被采信**；以 Playwright JSON reporter 的结构化结果为准。
- 短路点：测试结果解析独立于 agent 自述，写入 `.vibe/reports/<run>/result.json`。

### 4.3 防线②：AC 驱动断言（每条用例带 ac_id）

- generator 生成的每个 test 必须在标题或元数据里标注 `ac_id`，例：
  ```ts
  test('[AC-LOGIN-04] 两次密码不一致提示', async ({ page }) => { ... })
  ```
- 断言必须命中 AC 的 `then.expect_text`（如 `await expect(toast).toHaveText('两次密码输入不一致')`）。
- **空断言检测**：由 §4.4 的 coverage-checker 统一负责（静态扫描 spec 文件，识别 `expect(true)` / 无 `expect` / 断言文本不匹配任何 AC expect_text 的用例 → 标记 `HOLLOW`）。本节只规定 generator 的产出义务（每条用例必须带 ac_id 且断言命中 expect_text），检测与判定收敛在 checker 一处，避免职责重复。

### 4.4 防线③：AC↔断言双向映射（确定性脚本，反作弊核心）

`coverage-checker.ts` 产出双向映射报告 `.vibe/reports/<run>/coverage.json`：

```
正向 (AC → 测试):   每条 AC 是否有 ≥1 个 ac_id 匹配的用例,且该用例真执行过(在 result.json 里)
反向 (测试 → AC):   每个用例的 ac_id 是否存在于 AC 集合; 是否有断言

判定:
  AC 有,但无匹配用例            → MISSING (覆盖缺口)
  AC 有,有用例,但用例未执行     → CLAIMED_NOT_RUN (造假: 声称覆盖未真跑)
  用例有 ac_id,但无有效断言      → HOLLOW (断言空洞)
  用例 ac_id 不在 AC 集合        → ORPHAN (野生用例)
  AC 有,用例执行,断言命中 expect → COVERED ✅
```

**门控**：任何 MISSING / CLAIMED_NOT_RUN / HOLLOW → 该 run 不通过，进 Bad Case。
**这是把"没测却说测了"摁死的确定性闸门——不依赖任何 LLM 判断。**

### 4.5 Bad Case 闭环（补全真实工具包薄弱点）

**沉淀**（`/learning-compound` → `badcase.ts`）：失败/造假/缺口结构化为 YAML：

```yaml
---
id: BC-20260607-001
feature: login
type: coverage_gap            # coverage_gap | hollow_assertion | exec_fail | claimed_not_run
ac_id: AC-LOGIN-04
symptom: "两次密码不一致路径无测试,生成器默认只覆盖 happy path"
root_cause: "generator 未覆盖 isForget=3 异常分支"
fix_hint: "在生成 prompt 中强制要求覆盖每个 AC 的 then,包括异常 observable"
created_at: "<注入>"
---
（可选自由文本补充）
```

**检索**（`/learning-researcher` → `badcase.ts`）：下次跑 vibe-test 前，按 `feature` + AC 关键词检索相似 Bad Case，注入 generator 上下文（"历史上这些路径漏过，务必覆盖"），形成**用得越多越不犯同类错**的复利雏形。

> 形态对齐真实工具包的 `/learning-compound`（YAML frontmatter + 结构化字段 + 本地存储）。

---

## 5. 测试策略（简版自身怎么被测）

简版工具链自己也要可测，否则是"测试工具不可信"的笑话。分两层（呼应 OpsPilot Phase 8 的分层思想）：

| 层 | 测什么 | 怎么测 | 进 CI |
|---|---|---|---|
| **L1 工具链单元** | orchestrator 选择算法、coverage-checker 五种判定、契约 zod 校验、badcase 读写 | Vitest + 固定 fixture（mock AC + mock result.json），**确定性** | ✅ |
| **L2 端到端真跑** | AC → 真生成 → 真打 hoo-desk → 三防线报告 | 手动/按需，依赖 dev server + LLM，**非确定性** | ❌ 标注非 CI |

**L1 关键用例**（必须覆盖）：
- 选择算法：有 doing 选 doing 最高优先级；无 doing 选 pending 第一；全终态返回 null。
- coverage-checker：构造 MISSING / CLAIMED_NOT_RUN / HOLLOW / ORPHAN / COVERED 五种输入，断言判定正确。
- 契约：合法信封通过；缺字段/非法 status 被 zod 拒绝。

---

## 6. 分阶段路线图（全流程复刻的全局位置）

```
本期 Phase 1 (本 spec):  A 脊柱 + B 测试域三防线 + Bad Case 闭环   [手写 AC 输入]
   ↓ 独立 spec
Phase 2:  C 前半段 — 需求→方案设计(产出 AC) + 人机门控四选项 + 任务拆分 DAG
   ↓ 独立 spec                                （AC 从手写升级为门控生成,接上 B 的输入）
Phase 3:  D 开发循环 + 分级修复审查（受控小改动,不啃 hoo-desk 老构建）
   ↓ 独立 spec
Phase 4:  贯穿面增强 — 交付报告 / 知识回流中心化 / 反证 Agent（愿景落地）
```

每阶段 spec→plan→实现独立交付，每阶段结束都有可 demo 的增量。

---

## 7. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| hoo-desk 老依赖装不上/起不来 | 防线①拿不到真证据 | 已确认本机可跑；首个 plan task 即"验证 dev server + Playwright 连通"，不通则降级 mock 页面（保留三防线逻辑） |
| LLM 生成的 spec.ts 语法/选择器错 | E2E 跑不起来 | generator 产出后先 `tsc --noEmit` + Playwright dry-run 校验；失败计入 attempts,熔断后进 Bad Case |
| Playwright 选择器依赖 element-ui 内部结构 | 用例脆弱 | AC 的 target 提供稳定锚点(按钮文案/placeholder),generator 优先用语义选择器 |
| 简版被误当生产工具 | 面试翻车 | 文档显著标注"简版/演示";落地度光谱区分【真跑】【愿景】 |
| 工具链 Date.now/随机导致测试不可重放 | L1 不确定 | 脚本内禁用 Date.now/随机,时间戳由调用方注入(同 OpsPilot 约定) |

---

## 8. 验收标准（Phase 1 完成的定义）

- [ ] `tools/vibe` 工具链 L1 单测全绿（选择算法 + 五种覆盖判定 + 契约校验 + badcase 读写）。
- [ ] 手写 `login.ac.json`（覆盖 isForget 1/2/3 三态，含 ≥2 条异常路径 AC）。
- [ ] 跑通一次端到端：AC → 生成 spec.ts → 真打 hoo-desk 登录页 → 产出 trace + result.json + coverage.json。
- [ ] coverage.json 能**真实抓出**至少一种缺陷：故意让 generator 漏掉某条异常 AC，报告标 MISSING；或注入空断言，报告标 HOLLOW。
- [ ] 该缺陷经 `/learning-compound` 落成 badcase.yaml；再次运行时 `/learning-researcher` 能检索到并注入。
- [ ] **框架探测**：`detect()` 能从 `package.json` 正确识别 hoo-desk 为 `vue2`，并对 vue3/react16-/react16+ 的样例 package.json 各返回正确枚举（L1 单测覆盖四枚举）。
- [ ] **通用性验证**：仅新增一份 AC（指向 hoo-desk 另一个页面，如 `course/creat_class.vue`），探测器自动复用 vue2 profile，**不改 `tools/vibe/src/**` 任何一行**，即可对新页面生成并产出 coverage.json。
- [ ] **零耦合校验**：`tools/vibe/src/**`（适配器目录除外）全文搜索无 `hoo-desk`/`login`/`isForget` 硬编码（CI 加一条 grep 守卫）。框架级词（element-ui 等）仅允许出现在 `src/adapters/**`。
- [ ] 全程不修改 hoo-desk 业务源码与构建配置。

---

## 附：与面试三份文档的映射（便于讲述）

| 简版机制 | 对应 harness 内核 | 文档出处 |
|---|---|---|
| 任务选择算法、orchestrator 不问 LLM | ① 控制权归确定性系统 | 不变内核 §2① |
| 契约信封 zod 校验、AC JSON | ③ 契约优先 | 不变内核 §2③ |
| 防线①真执行机器证据 | ④ 证据高于断言 | 不变内核 §2④ |
| 三防线分层、coverage-checker | ④ + 测试域展开 | PHASE8 设计决策（同源思想） |
| task.json 持久化 + 恢复选 doing | ⑥ 状态外置可恢复 | 不变内核 §2⑥ |
| events.jsonl + Bad Case 闭环 | ⑦ 可观测与闭环 | 不变内核 §2⑦ |
| 人机门控四选项（Phase 2） | ① 特例：人在高代价处 | 体系认知 §7 |
```
