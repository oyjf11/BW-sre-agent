下面不是逐句直译，而是**按原文章节完整覆盖的中文意译与精读**。我会区分：

- **原文在说什么**
- **这句话真正意味着什么**
- **落实到 Coding Agent 应该怎么做**

---

# 《Harness Engineering for Coding Agent Users》中文结构化精读

## 一、文章信息

**英文标题：** Harness engineering for coding agent users
**作者：** Birgitta Böckeler，Thoughtworks 杰出工程师
**发布日期：** 2026 年 4 月 2 日

这篇文章试图建立一套心智模型，用来回答：

> 怎样让 Coding Agent 在更少人工监督的情况下，仍然产出值得信任的软件？

作者认为，不能只依赖模型能力，也不能只写一个更长的 Prompt。真正需要建设的是模型外部的一整套控制系统，即 **Harness**。([martinfowler.com][1])

---

# 二、文章的核心论点

传统 AI Coding 的思路通常是：

```text
选择更强模型
    ↓
编写更详细 Prompt
    ↓
让 Agent 生成代码
    ↓
人工检查
```

Harness Engineering 的思路则是：

```text
明确目标和规则
    ↓
为 Agent 提供合适的上下文、工具和环境
    ↓
Agent 执行
    ↓
自动检测结果
    ↓
错误反馈给 Agent
    ↓
Agent 自我修正
    ↓
只有高风险问题才交给人
```

因此，Harness 的目标不是保证 Agent 永远不犯错，而是：

1. 提高 Agent 第一次做对的概率。
2. 让 Agent 能看见自己的错误。
3. 让 Agent 在交付给人之前自动修正。
4. 把人工注意力留给机器难以判断的问题。

可以概括为：

> **可靠性不只来自模型，而来自模型、环境、约束和反馈闭环的共同作用。**

LangChain 使用了一个更宽泛的定义：

```text
Agent = Model + Harness
```

模型提供推理能力；Harness 提供状态、工具执行、文件系统、沙箱、编排、约束和验证机制。Birgitta 的文章进一步把讨论范围缩小到“Coding Agent 用户如何建设项目外层 Harness”。([LangChain Blog][2])

---

# 三、Harness 有内外两层

文章认为，“Harness”这个词在不同语境下含义不同。

## 1. Coding Agent 厂商提供的内部 Harness

例如 Claude Code、Codex、OpenCode 自带的：

- System Prompt
- 文件读取和代码搜索
- 工具调用机制
- Bash 执行
- 上下文压缩
- 子 Agent 调度
- 模型路由
- 权限控制
- 会话状态管理

这些决定了 Agent 本身如何运行。

## 2. 使用者建设的外部 Harness

这是文章真正关注的部分，包括：

- `AGENTS.md`、`CLAUDE.md`
- Skills
- 架构文档
- API 规范
- 项目脚手架
- 自定义命令
- Linter
- 类型检查
- 测试体系
- 架构约束
- Review Agent
- CI/CD
- 日志、指标和运行时监控

外层 Harness 不改变模型本身，而是改变模型工作的环境。

你可以把它理解为：

```text
模型能力 = 员工个人能力
Coding Agent = 员工使用的电脑和工具
外层 Harness = 企业研发制度、工程平台、质量门禁和反馈体系
```

仅仅拥有聪明的工程师，并不意味着企业能稳定交付软件；同理，仅仅拥有强模型，也不意味着 Agent 能稳定完成工程任务。

---

# 四、核心框架：Guides 与 Sensors

这是整篇文章最关键的一组概念。

```text
Harness
├── Guides：行动前引导
└── Sensors：行动后检测
```

---

## 4.1 Guides：前馈控制

Guides 是在 Agent 开始行动之前，为它提供方向。

作者借用了控制论中的 **Feedforward Control，前馈控制**。

它回答的是：

> 在 Agent 写代码之前，我们能提供哪些信息，降低它走错路的概率？

典型 Guides 包括：

- 项目规则
- 架构原则
- 编码规范
- 业务规格
- API 文档
- 测试说明
- Skills
- 脚手架
- CLI
- Codemod
- 语言服务器
- 示例代码

例如：

```markdown
## Bug 修复规则

1. 修改前必须稳定复现问题。
2. 必须保留复现证据。
3. 不得修改无关模块。
4. 修复后必须运行受影响测试。
5. 验证失败时不得宣布完成。
```

这属于推理型 Guide。

而下面这种属于程序型 Guide：

```bash
pnpm create internal-service
```

这个脚手架直接生成符合组织规范的目录、配置和测试结构，从结构上减少 Agent 自由发挥的空间。

### 精读理解

很多人把 Harness Engineering 理解成“写更多规则文件”，这是不完整的。

最有效的 Guide 不一定是自然语言，而可能是：

- 一个项目模板
- 一个代码生成器
- 一个强类型接口
- 一个固定目录结构
- 一个只能按正确方式调用的内部 SDK

因为程序结构比文字要求更难被忽略。

---

## 4.2 Sensors：反馈控制

Sensors 在 Agent 行动后观察结果，并把问题反馈回来。

作者称之为 **Feedback Control，反馈控制**。

典型 Sensors 包括：

- ESLint
- TypeScript 类型检查
- 单元测试
- 集成测试
- Playwright
- Semgrep
- 覆盖率检查
- 架构依赖检查
- 浏览器截图
- 控制台日志
- AI Code Review
- 运行时监控

执行过程是：

```text
Agent 修改代码
    ↓
运行 Sensor
    ↓
发现失败
    ↓
把失败信息返回 Agent
    ↓
Agent 分析并修改
    ↓
再次执行 Sensor
```

好的 Sensor 不只是输出：

```text
Error: rule violation
```

而应尽可能输出可操作信息：

```text
Controller 不允许直接依赖 Repository。

请通过 Service 层访问数据：
Controller → Service → Repository

违规位置：
src/order/controller.ts:42
```

这种错误信息本身就是下一轮 Agent 的修复上下文。

OpenAI 的实践也强调了这一点：他们通过自定义 Linter 和结构测试执行架构约束，并在错误信息中加入修复指引，使检测结果可以直接进入 Agent 的自修复过程。([OpenAI][3])

---

## 4.3 为什么 Guides 和 Sensors 必须同时存在

只有 Guides：

```text
告诉 Agent 应该怎么做
但不知道它实际有没有做到
```

只有 Sensors：

```text
Agent 不断犯错
工具不断报错
Agent 再不断返工
```

二者结合才构成闭环：

```text
Guide 降低错误发生概率
Sensor 捕获剩余错误
反馈让 Agent 修正
错误经验再反哺 Guide
```

这也是 Harness Engineering 与普通 Prompt Engineering 的本质区别。

Prompt Engineering 常常只考虑输入；Harness Engineering 同时设计输入、执行、观察、修正和升级。

---

# 五、Computational 与 Inferential

文章又从执行方式上，把 Guides 和 Sensors 分成两类。

| 类型          | 中文理解               | 特点                           |
| ------------- | ---------------------- | ------------------------------ |
| Computational | 程序计算型、确定性     | 快、便宜、可重复               |
| Inferential   | 模型推理型、语义判断型 | 理解力强，但更贵、更慢、不稳定 |

---

## 5.1 Computational：确定性控制

典型工具：

- TypeScript
- ESLint
- 单元测试
- 架构测试
- 静态分析
- 正则检查
- 依赖分析
- 脚本
- Codemod
- CI 门禁

例如：

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
pnpm architecture:check
```

它们的优势是结果明确：

```text
通过 / 不通过
允许 / 不允许
覆盖率 82% / 低于阈值
存在循环依赖 / 不存在
```

这类 Sensor 应尽量靠近 Agent，甚至每次修改后执行，因为成本低、反馈快。

### 核心原则

> 能通过确定性规则判断的问题，不要优先交给另一个 LLM 判断。

例如“Controller 是否直接依赖 Repository”，用 AST 或依赖图检测通常比让 Review Agent 阅读代码更便宜、更稳定。

---

## 5.2 Inferential：推理型控制

有些问题无法用简单规则判断：

- 是否误解了业务需求
- 是否过度设计
- 根因分析是否合理
- 测试是否只是在迎合实现
- 是否产生语义重复代码
- 修复是否掩盖了真实问题
- 架构方案是否符合当前业务阶段

这些需要 LLM 或人进行语义判断。

例如：

```text
设计 Agent
    ↓
评审方案是否合理

实现 Agent
    ↓
Review Agent 检查是否过度修改

测试 Agent
    ↓
检查测试是否真正覆盖需求
```

推理型 Sensor 很重要，但不能把它当作绝对真理。

它更适合作为：

- 风险提示器
- 第二意见
- 语义补充
- 人工 Review 前置过滤器

而不是唯一质量门禁。

---

# 六、Harness Engineering 与 Context Engineering 的关系

文章认为：

> Harness Engineering 是 Coding Agent 场景下，一种更具体、更系统化的 Context Engineering。

Context Engineering 关注的是：

```text
模型在当前时刻应该看到什么？
```

Harness Engineering 进一步关注：

```text
模型应该看到什么？
它能做什么？
做完以后怎么验证？
失败后如何修复？
什么时候停止？
什么时候交给人？
```

Context Engineering 提供信息传递机制，例如：

- `AGENTS.md`
- Rules
- Skills
- MCP
- 文件搜索
- 项目文档
- 会话历史

Harness Engineering 则把这些机制组织成一个控制系统。

Birgitta 在另一篇文章中把 Coding Agent 的上下文分为可复用提示、规则、工具、MCP、Skills 和工作区文件，并强调上下文不能无限堆积，应该按任务逐步加载。([martinfowler.com][4])

因此：

```text
Context Engineering
解决“给 Agent 看什么”

Harness Engineering
解决“如何让 Agent 稳定完成工作”
```

---

# 七、Steering Loop：人类不是逐行纠错，而是调系统

文章提出了一个非常重要的循环：

```text
Agent 犯错
    ↓
人分析为什么现有 Harness 没拦住
    ↓
调整 Guide 或 Sensor
    ↓
以后同类错误更少发生
```

例如 Agent 第一次忘记加测试，可以直接提醒。

但如果同类问题反复出现，就不应该继续依赖临时提醒，而应该把经验固化为：

- Definition of Done
- Skill
- PR 检查项
- 覆盖率规则
- 测试目录扫描器
- CI 门禁
- Review Agent 规则

这意味着人的角色从：

```text
每次告诉 Agent：你这里又错了
```

转变为：

```text
为什么系统允许这种错误重复发生？
```

这与平台工程、质量工程和 SRE 的思想非常接近：

> 不只修复单次故障，还要修复产生故障的系统条件。

---

# 八、质量左移：越早发现越便宜

文章沿用了持续集成和测试左移的原则。

检查不应该全部堆在 PR 合并前，而应按成本和速度分层。

## 第一层：Agent 本地执行阶段

适合运行：

- LSP
- 格式化
- 类型检查
- ESLint
- 快速单测
- 基础架构检查
- 轻量 Review Agent

目标是几十秒内发现明显问题。

## 第二层：提交或 PR 阶段

适合运行：

- 完整单测
- 集成测试
- E2E
- 安全扫描
- 依赖检查
- 覆盖率
- 变更范围 Review

## 第三层：CI 或合并后

适合运行：

- Mutation Testing
- 大范围架构 Review
- 性能测试
- 完整回归
- 跨模块语义检查

## 第四层：持续运行

适合监控：

- 死代码
- 依赖老化
- 架构漂移
- 覆盖率质量
- 错误率
- 延迟
- SLO
- 日志异常
- AI 输出质量

文章的重点不是“检查越多越好”，而是：

> 根据检查的速度、成本和风险，把它放到最合适的位置。([martinfowler.com][1])

---

# 九、三种 Harness

文章按“系统希望维持什么状态”，区分了三种 Harness。

---

## 9.1 Maintainability Harness：可维护性 Harness

它关注代码内部质量。

检测对象包括：

- 重复代码
- 圈复杂度
- 超大文件
- 风格违规
- 缺少测试
- 循环依赖
- 死代码
- 架构漂移
- 不合理依赖
- 语义重复

这是当前最容易建设的一类，因为传统软件工程已经积累了大量工具。

例如：

```text
ESLint
SonarQube
Semgrep
dependency-cruiser
ArchUnit
TypeScript
覆盖率工具
```

但文章也指出，确定性工具主要擅长发现结构问题。

下面这些仍然很难可靠判断：

- 需求是否理解错误
- 功能是否多做了
- 根因是否诊断错误
- 方案是否不必要地复杂
- 实现是否符合组织真实意图

因此，可维护性 Harness 很重要，但不能证明软件“做对了”。

---

## 9.2 Architecture Fitness Harness：架构适应性 Harness

这类 Harness 用于持续保持架构特征。

例如：

```text
UI 层不能访问数据库
Domain 层不能依赖 Infrastructure 层
跨业务模块只能通过公开接口通信
所有外部输入必须在边界解析
日志必须包含 traceId
核心接口延迟不能超过阈值
```

它不只检查代码结构，还可以检查：

- 性能
- 安全
- 弹性
- 可观测性
- 可部署性
- 模块化
- 数据隔离

这种思想来自 **Architecture Fitness Function**：把“好的架构”转化成可以持续自动执行的验证条件。([Thoughtworks][5])

例如：

```ts
expect(controllerDependencies).not.toContain("repository");
```

或者：

```bash
pnpm test:architecture
pnpm test:performance
pnpm test:tenant-isolation
```

精髓是：

> 架构不能只存在于 PPT 和架构师脑中，而应尽量变成可执行规则。

---

## 9.3 Behaviour Harness：行为 Harness

这是作者认为最难的一部分。

它回答：

> 软件最终是否真的按业务需要运行？

例如：

- 用户是否真的能完成登录
- 退款金额是否正确
- 租户数据是否隔离
- 订单状态是否符合业务规则
- 故障告警是否真正触发
- 页面交互是否符合用户预期

当前常见做法是：

```text
给 Agent 一份需求
    ↓
Agent 写代码
    ↓
Agent 同时写测试
    ↓
测试通过
    ↓
认为功能正确
```

问题是：

> 代码和测试可能同时误解了需求。

例如需求是“普通用户不能删除已发布应用”，Agent 误解成“普通用户不能删除任何应用”。

它写出的实现和测试完全一致，所有测试都通过，但业务仍然是错的。

所以 Behaviour Harness 通常还需要：

- 人工批准的验收案例
- 独立于实现者的测试设计
- 固定 Fixture
- 真实浏览器验证
- 黄金数据集
- 人工验收
- 生产反馈

文章提到的 Approved Fixtures 思路，就是由人预先批准关键输入和预期输出，避免实现 Agent 同时控制代码与测试判定标准。

---

# 十、Harnessability：代码库是否容易被 Harness 管理

不同项目并不具备相同的 Harness 建设条件。

更容易 Harness 化的项目通常具有：

- 强类型语言
- 清晰模块边界
- 统一目录结构
- 稳定框架
- 完整测试
- 明确接口
- 可自动启动的环境
- 结构化日志
- 可重复构建
- 规范化脚手架

例如 TypeScript 项目天然拥有类型检查 Sensor。

分层明确的项目可以自动检查：

```text
Controller → Service → Repository
```

而历史项目可能存在：

- 隐式全局变量
- 动态依赖
- 模块循环引用
- 无测试
- 文档过期
- 启动依赖人工操作
- 大量知识只在人脑中

这种项目最需要 Harness，却也最难建设 Harness。

文章将有利于 Agent 理解和操作环境的结构属性称为 **Ambient Affordances**。简单理解就是：

> 不用每次告诉 Agent，项目结构本身就在引导它走正确路线。([martinfowler.com][1])

---

# 十一、Harness Templates：未来的项目模板不只是代码模板

传统项目模板通常提供：

```text
目录结构
依赖
基础配置
示例代码
```

未来的 Harness Template 可能同时提供：

```text
项目结构
技术栈
AGENTS.md
Skills
架构规则
自定义 Linter
测试策略
CI Pipeline
Review 流程
运行时监控
```

例如：

```text
React 管理后台 Harness
Node.js 数据服务 Harness
Java CRUD 服务 Harness
Go 事件处理 Harness
Agent 服务 Harness
```

每个模板都预先限制解决方案空间。

这背后对应 Ashby 的必要多样性定律：控制系统要管理复杂系统，必须能够覆盖其可能状态。若 Agent 什么架构都能生成，Harness 很难穷尽所有情况；如果组织先固定少量标准拓扑，控制难度会显著下降。([martinfowler.com][1])

也就是说：

```text
允许 Agent 任意设计
→ 灵活，但难以治理

限制为几种标准架构
→ 自由度下降，但更容易自动验证
```

这与企业内部脚手架、应用平台和“黄金路径”高度一致。

---

# 十二、人类的角色不会消失

人类工程师天然携带一套隐性的 Harness：

- 知道团队为什么这么设计
- 知道哪些技术债暂时可以接受
- 知道某些规范是强约束还是历史习惯
- 能感受到代码复杂度正在失控
- 知道业务当前最重要的目标
- 对代码提交承担社会和组织责任

Agent 没有这些天然背景。

它不会因为写出一个 300 行函数而产生“不舒服”的感觉，也不知道一个技术上正确的方案是否适合当前组织。

Harness Engineering 的本质，是尝试把人的隐性经验外部化：

```text
人的经验
    ↓
规则
文档
测试
架构约束
检查器
反馈闭环
```

但不可能完全外部化。

因此，正确目标不是：

```text
彻底取消人类参与
```

而是：

```text
减少机械性检查
把人投入需求判断、架构取舍和风险决策
```

---

# 十三、文章留下的开放问题

作者没有把 Harness Engineering 描述成已经成熟的方法论，而是提出了一系列尚未解决的问题：

## 1. Harness 自身如何保持一致

随着规则增多，可能出现：

```text
AGENTS.md 要求 A
Skill 要求 B
Linter 强制 C
测试隐含要求 D
```

这些要求可能互相冲突。

因此 Harness 本身也需要：

- 版本管理
- 测试
- 一致性检查
- 生命周期管理
- 废弃机制

## 2. 如何评价 Harness 的质量

如果某个 Sensor 从来不报错，可能有两种解释：

```text
代码质量非常好
或
Sensor 根本没有检测能力
```

测试可以用覆盖率和 Mutation Testing 评价，但 Harness 目前还缺少类似成熟指标。

未来可能需要：

- Harness 覆盖率
- 错误拦截率
- 误报率
- 漏报率
- 自修复成功率
- 人工升级率
- 单任务验证成本

## 3. 如何处理冲突信号

例如：

```text
性能 Sensor 要求减少抽象
维护性 Sensor 要求拆分模块
安全规则要求增加边界校验
交付目标要求尽快上线
```

Agent 是否能做出合理权衡，目前仍不稳定。

## 4. Behaviour Harness 如何成熟

可维护性和架构规则相对容易自动化，但“业务是否真正正确”仍然依赖大量人工判断。

这是目前最关键的缺口。([martinfowler.com][1])

---

# 十四、结合 OpenAI 实践理解这篇文章

OpenAI 的 Harness Engineering 实践可以看作这篇文章的一个案例。

OpenAI 团队让 Codex 生成产品代码、测试、CI、文档、可观测性和内部工具；人的主要工作变成设计环境、明确意图和建设反馈机制。([OpenAI][3])

其关键做法包括：

```text
仓库作为知识源
严格分层架构
自定义 Linter
结构测试
可执行计划
自动文档维护
Agent 自动复现 Bug
自动验证和录屏
自动处理 CI 失败
持续扫描架构漂移
定期生成重构 PR
```

他们还发现，Agent 会复制代码库中已有的不良模式，因此需要周期性“垃圾回收”：持续扫描偏差、小步偿还技术债，而不是积累到最后集中治理。([OpenAI][3])

这印证了 Birgitta 的核心观点：

> Agent 自治不是一次授权，而是不断编码测试、验证、反馈和恢复能力之后形成的结果。

---

# 十五、映射到你的 Hermes → Claude → Codex → OpenCode 方案

你当前设想更接近：

```text
Hermes：流程编排
Claude Code：方案设计
Codex：代码实现
OpenCode / DeepSeek：测试与检查
人：最终验收
```

这已经具备多 Agent 编排，但按照文章标准，还不能仅凭“多 Agent”就称为完整 Harness。

## 还应补齐四层

### 1. Guides

```text
AGENTS.md
架构规范
SDD / Spec
任务阶段约束
工具使用说明
Definition of Done
Skill
接口契约
```

### 2. Computational Sensors

```text
TypeScript
ESLint
单元测试
Playwright
依赖边界检查
覆盖率
安全扫描
构建检查
```

### 3. Inferential Sensors

```text
方案 Review Agent
根因 Review Agent
代码 Review Agent
测试质量 Review Agent
需求符合度 Review Agent
```

### 4. Control Loop

```text
失败分类
自动重试
最大重试次数
重新验证
阻断条件
人工升级条件
经验沉淀
Harness 规则更新
```

完整形态应该是：

```text
用户需求
    ↓
Hermes 任务分类
    ↓
Claude 生成 Spec
    ↓
Spec Review
    ↓
Codex 实现
    ↓
确定性检查
    ↓
推理型 Review
    ↓
失败则回流实现 Agent
    ↓
通过后人工验收
    ↓
重复问题沉淀到 Harness
```

---

# 十六、最终结论

这篇文章真正提出的不是一个新工具，而是一种新的软件工程重心：

```text
过去：
工程师主要生产代码

现在：
工程师和 Agent 共同生产代码

未来：
工程师主要设计让 Agent 稳定生产代码的系统
```

Harness Engineering 的最小闭环是：

```text
Guides
告诉 Agent 怎么做

Sensors
检测 Agent 做得怎么样

Self-correction
让 Agent 根据检测结果修正

Steering loop
把重复错误沉淀为新的规则和检测器

Human judgment
负责需求、取舍、风险与最终责任
```

最值得记住的一句话是：

> **Agent 的自治上限，不只取决于模型有多聪明，更取决于它能否获得明确引导、可观察反馈、自动验证和可控的失败路径。**

[1]: https://martinfowler.com/articles/harness-engineering.html "Harness engineering for coding agent users"
[2]: https://blog.langchain.com/the-anatomy-of-an-agent-harness/ "The Anatomy of an Agent Harness"
[3]: https://openai.com/index/harness-engineering/ "Harness engineering: leveraging Codex in an agent-first world | OpenAI"
[4]: https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html "Context Engineering for Coding Agents"
[5]: https://www.thoughtworks.com/en-de/radar/techniques/architectural-fitness-function " Architectural fitness function | Technology Radar | Thoughtworks Germany"
