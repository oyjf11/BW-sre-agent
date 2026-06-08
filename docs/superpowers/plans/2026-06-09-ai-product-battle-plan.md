# AI Product Battle Plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the AI product manager interview battle plan into a two-layer document set: a 15-25 page memorization-oriented main plan plus one long-form extension document.

**Architecture:** Keep the main document concise and interview-ready, with short answers, role-specific project narratives, and high-risk anti-puncture scripts. Move long reasoning, metric detail, follow-up chains, and methodology补课 into a separate extension document so the main plan stays usable before interviews.

**Tech Stack:** Markdown documents, existing `.interview/battle-plan/` materials, `rg`, `sed`, `wc`, `git diff`, `git status`.

---

## Scope Check

This is one document-rewrite task, not multiple independent software subsystems. It touches only interview preparation Markdown files and does not change backend code, frontend code, dependencies, database migrations, runtime configuration, or project execution behavior.

## File Structure

- Modify: `.interview/battle-plan/作战计划-ai产品.md`
  - Responsibility: 15-25 page interview battle plan for fast review and direct interview answers.
  - Style: short, firm, memorization-oriented; use "要害一句 -> 三点 -> 套项目" for core answers.

- Create: `.interview/battle-plan/作战计划-ai产品-扩展材料.md`
  - Responsibility: long-form追问底稿, metric details, anti-puncture chains, methodology补课, and expanded questions.
  - Style: detailed but structured; each high-risk topic should include interviewer intent, answer strategy, and fallback wording.

- Already created: `docs/superpowers/specs/2026-06-09-ai-product-battle-plan-design.md`
  - Responsibility: approved design source for this plan.

- Create this plan: `docs/superpowers/plans/2026-06-09-ai-product-battle-plan.md`
  - Responsibility: executable implementation plan for the document rewrite.

## Task 1: Preflight And Baseline

**Files:**
- Read: `.interview/battle-plan/作战计划-ai产品.md`
- Read: `.interview/battle-plan/temp.md`
- Read: `.interview/核心诉求.md`
- Read: `.interview/ai产品面试-精炼版.md`
- Read: `.interview/battle-plan/母题骨架-一页纸.md`
- Read: `docs/superpowers/specs/2026-06-09-ai-product-battle-plan-design.md`

- [ ] **Step 1: Confirm target files are not already modified**

Run:

```bash
git status --short -- '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: either no output, or only the extension document is untracked if a previous partial run created it. If the main document is already modified, inspect the diff before editing:

```bash
git diff -- '.interview/battle-plan/作战计划-ai产品.md'
```

- [ ] **Step 2: Capture baseline size and opening structure**

Run:

```bash
wc -l '.interview/battle-plan/作战计划-ai产品.md'
sed -n '1,120p' '.interview/battle-plan/作战计划-ai产品.md'
```

Expected: the current main document opens with `# AI 产品经理面试作战计划` and contains the older sections for岗位区别、开场定位、问题穷举、标准答案、弱点补强、执行计划.

- [ ] **Step 3: Re-read approved design anchors**

Run:

```bash
rg -n "主文档重构为 10 个章节|扩展文档包含 7 个模块|2\\.2天->4小时|向上汇报|Axure|XMind|ROI" docs/superpowers/specs/2026-06-09-ai-product-battle-plan-design.md
```

Expected: matches for the approved 10 main sections, 7 extension modules, `2.2天->4小时`, 向上汇报, Axure, XMind, and ROI.

## Task 2: Rewrite Main Document Structure And Positioning

**Files:**
- Modify: `.interview/battle-plan/作战计划-ai产品.md`

- [ ] **Step 1: Replace the main document title and strategic opening**

Use `apply_patch` to replace the current main document with a new document that begins with this exact top-level structure:

```markdown
# AI 产品经理面试作战计划

> 目标岗位：AI 策略产品经理 / AI 平台产品经理，月 base 30k+
> 核心定位：有工程纵深、能把复杂 AI 能力产品化落地的候选人
> 作战原则：不装全能传统 PM，把工程纵深翻译成业务价值、可控流程和可验证结果

---

## 0. 作战理念

一句话：我不主打“通用型全能 PM”，我主打“懂工程、懂 Agent、能把 AI 从 Demo 推到可控试点的 AI 产品候选人”。

主动打的优势区：

- 复杂 AI 工作流拆解：Router / Planner、13 节点 SRE 流程、前端测试三防线。
- 可控与可信：证据链、质量门禁、Human-in-the-loop、risk_gate、审批与审计。
- 评估与迭代：Bad Case 闭环、离线评测、证据完整率、缺陷归因。
- 企业内部 AI 落地：从 PoC 到试点，从个人提效到团队流程。

只求不露怯的弱项区：

- C 端增长、商业化定价、大规模运营。
- 长期 Axure / 墨刀原型经验。
- 严格 A/B 实验和成熟数据分析平台实战。

统一话术：

> “我的背景不是传统 C 端 PM，而是从研发和 AI 工程化落地切入。我能把复杂业务拆成可执行流程，把不稳定的 AI 能力放进有边界、有证据、有评估、有审批的产品体系里。这是我相对纯业务 PM 的差异化。”
```

- [ ] **Step 2: Add role split and opening scripts**

Continue the main document with these sections and keep each opening script between 120 and 180 Chinese characters:

```markdown
## 1. 两类岗位怎么打

### AI 策略 PM

考察重点：场景判断、业务价值、ROI、推广阻力、从 1 到 100。

打法：少讲底层代码，多讲“为什么这个场景值得上 AI、怎么灰度试点、怎么度量价值、怎么复制到更多团队”。

### AI 平台 PM

考察重点：能力抽象、平台治理、权限模型、评测体系、安全边界、开发者采用率。

打法：把开发套件、应用生成平台和 OpsPilot 都讲成“平台能力分层 + 流程治理 + 质量门禁”的案例。

## 2. 开场定位

### 策略 PM 版

> 我有 7 年研发和企业内部平台经验，近一年重点参与 AI 研发提效、应用生成和运维 Agent 方向。我对 AI 产品的判断是：难点不是模型能不能生成，而是能不能把 AI 能力变成可控、可验证、可推广的业务流程。所以我更适合做企业内部 AI 策略和落地型产品。

### 平台 PM 版

> 我有前端和全栈研发背景，参与过内部 AI 工具链和应用生成平台建设。我比较熟悉 Agent Workflow、RAG 意图识别、质量门禁、证据采集和 Human-in-the-loop。我做平台 PM 的优势是能理解业务团队要的灵活性，也能理解平台必须守住的安全、评测和治理边界。
```

- [ ] **Step 3: Add three projects with two narratives each**

Add `## 3. 三个项目，两种讲法` with these six subsections:

```markdown
### 3.1 开发套件：策略 PM 讲法
### 3.2 开发套件：平台 PM 讲法
### 3.3 应用生成平台：策略 PM 讲法
### 3.4 应用生成平台：平台 PM 讲法
### 3.5 OpsPilot：策略 PM 讲法
### 3.6 OpsPilot：平台 PM 讲法
```

Each subsection must contain exactly these four bullets:

```markdown
- 用户 / 场景：
- 核心痛点：
- 产品方案：
- 价值表达：
```

Use these project anchors:

- 开发套件：前端自动化测试、Playwright 真跑、截图取证、五分类失败归因、质量门禁、Bad Case 闭环。
- 应用生成平台：企业轻应用生成、Router / Planner、场景化 RAG 意图增强、Schema 中间产物、Sandpack 预览、增量修改。
- OpsPilot：SRE 故障处置、intake 到 rca 工作流、evidence_fanout、risk_gate、approval_interrupt、verify、RCA。

- [ ] **Step 4: Validate first-half structure**

Run:

```bash
rg -n "## 0\\. 作战理念|## 1\\. 两类岗位怎么打|## 2\\. 开场定位|## 3\\. 三个项目，两种讲法|3\\.6 OpsPilot：平台 PM 讲法" '.interview/battle-plan/作战计划-ai产品.md'
```

Expected: one match for each required heading.

## Task 3: Add Main Document Core Answers, Anti-Puncture Scripts, And Execution Plan

**Files:**
- Modify: `.interview/battle-plan/作战计划-ai产品.md`

- [ ] **Step 1: Add JD hard-gate section**

Append `## 4. JD 三条硬门槛怎么接` with exactly these subsections:

```markdown
### 4.1 Axure / XMind / 墨刀
### 4.2 数据分析意识、产品思维、运营方法论
### 4.3 复杂业务结构化、模型化、可执行方案
```

Required wording for `4.1`:

```markdown
> “XMind 这类结构化工具我会用于流程拆解和方案表达；Axure / 墨刀不是我过去最高频的工具，但我能快速补低保真原型。我的优势是前端背景，很多交互我可以直接做成高保真可运行原型。对 AI 产品来说，我更关注原型背后的流程、边界、异常状态和验收口径。”
```

Required wording for `4.2`:

```markdown
> “我没有大规模 C 端增长经验，但企业内部 AI 产品也需要数据驱动。我会看试点漏斗、有效任务完成率、人工返工率、Bad Case 类型分布、团队复用率和能力采用率。我的经验更接近内部试点运营：选种子团队、形成标杆案例、模板化复制、周度复盘，再反推产品规则和评测集。”
```

Required wording for `4.3`:

```markdown
> “复杂业务结构化是我的强项。比如 OpsPilot 我把 SRE 故障处置拆成 intake、triage、planner、evidence、diagnose、risk_gate、approval、executor、verify、rca 等节点；应用生成平台把自然语言生成拆成 Router、Planner、Schema、SQL、预览、增量修改；开发套件把前端测试拆成证据采集、脚本执行、失败归因、缺陷流转和质量门禁。”
```

- [ ] **Step 2: Add core mother questions**

Append `## 5. 核心母题标准答案` with these ten question blocks:

```markdown
### Q1. 什么场景适合上 AI？
### Q2. AI 产品为什么 Demo 惊艳，落地困难？
### Q3. AI 产品北极星指标怎么设计？
### Q4. 怎么向 CTO / VP 汇报 ROI？
### Q5. 怎么定义一个 AI 功能好不好用？
### Q6. 企业 AI 治理怎么设计？
### Q7. 试点成功后怎么从 1 到 100？
### Q8. Prompt 工程怎么产品化？
### Q9. 平台统一治理和团队个性化怎么平衡？
### Q10. 怎么设计 Human-in-the-loop？
```

Each block must use this format:

```markdown
**要害一句**：

**三点**：
- 
- 
- 

**套项目**：
```

Concrete required content:

- Q4 must include `年度收益 = 节省工时价值 + 质量收益 + 复用收益 - AI 运行成本 - 维护成本`.
- Q5 must include `从业务工作流反推指标，不从模型指标出发`.
- Q6 must include `权限、数据隔离、高风险审批、审计、输出可追溯`.
- Q7 must include `种子团队、标杆案例、模板化复制、能力准入、周度复盘`.
- Q10 must include `高风险决策、语义不确定、责任归属`.

- [ ] **Step 3: Add highest-risk anti-puncture section**

Append `## 6. 防戳穿专章` with six scripts. Use this exact four-part structure for each script:

```markdown
### 6.x [风险点标题]

**先承认**：

**再区分**：

**再转化**：

**拉回证据**：
```

Required six titles:

```markdown
### 6.1 “2.2 天到 4 小时”是不是人工预估？
### 6.2 OpsPilot 到底是不是企业级项目？
### 6.3 你真的懂后端和生产级 Agent 服务吗？
### 6.4 “10+ 团队试点”具体是什么口径？
### 6.5 你没有系统写过 PRD / 用户调研，怎么做 PM？
### 6.6 你的 AI 产品指标是不是不够严谨？
```

Required wording for `6.1`:

```markdown
**先承认**：这个数字最初确实来自试点团队的工时反馈和人工估算，不是严格对照实验，我不会把它包装成严格 A/B 结论。

**再区分**：效率提升的单点数字不够严谨，但质量度量不是拍脑袋。开发套件真正系统化的是测试质量：Playwright 真跑、截图取证、失败归因、证据完整率和 Bad Case 回流。

**再转化**：如果现在重做，我会用对照组和实验组统一采集任务完成工时、人工返工次数、缺陷逃逸率、回归覆盖率，再看置信区间，而不是只报一个亮眼数字。

**拉回证据**：这次教训反而让我形成了现在的评估观：AI 产品不要只报省时，要同时度量质量、返工和风险。
```

- [ ] **Step 4: Add behavior interview and safe steering sections**

Append these sections:

```markdown
## 7. 行为面试软杀招

### 7.1 平时向上汇报多不多，会不会写汇报材料？

## 8. 面试中主动引导的话题

## 9. 7 天执行计划
```

Required wording for `7.1`:

```markdown
> “高频正式 PPT 汇报不算多，我们团队更多用可运行产物、数据和复盘文档同步。但结构化材料我做得不少，比如方案设计、能力拆解、架构决策、试点结果复盘。我的理解是，向上汇报的核心不是 PPT 本身，而是把复杂技术问题翻译成价值、风险和决策项，让决策者快速判断要不要投入、风险在哪里、下一步怎么推进。”
```

`## 8` must list these five safe topics:

```markdown
- AI 落地路径：从 Demo 到可控试点，再到模板化复制。
- 证据驱动评估：答案不重要，证据链、验证和返工率更重要。
- 复杂工作流拆解：把不确定任务拆成可恢复、可审计的节点。
- Human-in-the-loop：不是泛泛审批，而是在高风险决策、语义不确定和责任归属处介入。
- Bad Case 闭环：用户修正和失败案例要回流规则、Prompt、评测集和流程。
```

`## 9` must contain a 7-day table with rows `第 1 天` through `第 7 天`.

- [ ] **Step 5: Validate main document required content**

Run:

```bash
rg -n "JD 三条硬门槛|年度收益 = 节省工时价值|2\\.2 天到 4 小时|高频正式 PPT 汇报|第 7 天|Human-in-the-loop" '.interview/battle-plan/作战计划-ai产品.md'
wc -l '.interview/battle-plan/作战计划-ai产品.md'
```

Expected: matches for every required phrase. Line count should be between 260 and 650 lines, which corresponds to a concise 15-25 page Markdown battle plan depending on rendered density.

## Task 4: Create Extension Document With Long-Form Details

**Files:**
- Create: `.interview/battle-plan/作战计划-ai产品-扩展材料.md`

- [ ] **Step 1: Create extension document header and module list**

Use `apply_patch` to create the extension document beginning with:

```markdown
# AI 产品经理面试作战计划：扩展材料

> 用途：主文档负责背诵和现场作答；本文件负责追问底稿、长解释、指标口径和方法论补课。
> 使用方式：面试前优先背主文档；被某个问题反复戳穿时，再回到本文件补追问链。

---

## 1. 防戳穿长版话术库
## 2. ROI 与价值量化框架
## 3. 评估产品化：从业务工作流反推指标
## 4. 数据分析与运营方法论最小骨架
## 5. 工具能力补强：Axure / XMind / 墨刀
## 6. 向上汇报与材料写作
## 7. 扩展题库
```

- [ ] **Step 2: Expand anti-puncture scripts**

Under `## 1. 防戳穿长版话术库`, add six subsections matching the main document risk titles:

```markdown
### 1.1 “2.2 天到 4 小时”是不是人工预估？
### 1.2 OpsPilot 到底是不是企业级项目？
### 1.3 你真的懂后端和生产级 Agent 服务吗？
### 1.4 “10+ 团队试点”具体是什么口径？
### 1.5 你没有系统写过 PRD / 用户调研，怎么做 PM？
### 1.6 你的 AI 产品指标是不是不够严谨？
```

Each subsection must include:

```markdown
**面试官真实意图**：

**错误答法**：

**推荐答法**：

**如果继续追问**：
```

`1.1` must explicitly include:

```markdown
我接受这个质疑：`2.2 天到 4 小时` 最初不是严格实验，而是试点反馈估算。我的修正不是否认这个数字，而是把它降级为“试点反馈”，再补上更严谨的度量口径：对照组、实验组、任务完成工时、人工返工次数、缺陷逃逸率、回归覆盖率和置信区间。
```

- [ ] **Step 3: Add ROI framework and metric formulas**

Under `## 2. ROI 与价值量化框架`, add:

```markdown
### 2.1 汇报 ROI 的一句话框架
### 2.2 成本侧
### 2.3 收益侧
### 2.4 年度收益公式
### 2.5 三个项目分别怎么套
```

Required formula:

```markdown
年度收益 = 节省工时价值 + 质量收益 + 复用收益 - AI 运行成本 - 维护成本
```

Required caveat:

```markdown
`2.2 天到 4 小时` 只能作为试点反馈估算，不作为严格 A/B 实验证据。正式汇报时要把它放在“试点信号”里，而不是放在“最终 ROI 结论”里。
```

- [ ] **Step 4: Add evaluation productization module**

Under `## 3. 评估产品化：从业务工作流反推指标`, add:

```markdown
### 3.1 总原则
### 3.2 开发套件指标
### 3.3 应用生成平台指标
### 3.4 OpsPilot 指标
### 3.5 怎么回答“你怎么定义好用”
```

Required metrics:

- 开发套件：有效测试任务完成率、证据完整率、缺陷分流准确率、人工返工率。
- 应用生成平台：意图识别准确率、一次可预览成功率、增量修改命中率、人工修正轮次。
- OpsPilot：根因候选命中率、证据覆盖率、高风险操作拦截率、审批后执行成功率、RCA 可复用率。

Required sentence:

```markdown
我不从“模型准确率多少”开始定义好用，而是从用户工作流开始：用户要完成什么任务、哪里最容易返工、哪些错误最贵、哪些结果必须可验证。
```

## Task 5: Complete Extension Methodology, Tools, Reporting, And Expanded Questions

**Files:**
- Modify: `.interview/battle-plan/作战计划-ai产品-扩展材料.md`

- [ ] **Step 1: Add data analysis and internal operation module**

Under `## 4. 数据分析与运营方法论最小骨架`, add five subsections:

```markdown
### 4.1 漏斗
### 4.2 A/B
### 4.3 用户分层
### 4.4 留存 / 复用
### 4.5 Bad Case 闭环
```

Required positioning:

```markdown
我不把自己包装成做过大规模 C 端增长的人。我的经验更适合企业内部 AI 产品试点运营：先找种子团队，跑出标杆案例，再把流程、模板、评测集和准入规则沉淀下来复制到更多团队。
```

- [ ] **Step 2: Add product tool补强 module**

Under `## 5. 工具能力补强：Axure / XMind / 墨刀`, add:

```markdown
### 5.1 面试官为什么问工具
### 5.2 XMind 怎么补
### 5.3 Axure / 墨刀怎么补
### 5.4 前端背景怎么转化为优势
```

Required answer:

```markdown
我会把工具问题拆开看：XMind 是结构化表达，Axure / 墨刀是低保真交互表达。我的短板是过去没有长期以这些工具交付产品原型；我的优势是能用前端直接做高保真、可运行、可验证的交互原型。
```

- [ ] **Step 3: Add upward reporting module**

Under `## 6. 向上汇报与材料写作`, add:

```markdown
### 6.1 面试官为什么问
### 6.2 不能怎么答
### 6.3 推荐答法
### 6.4 如果追问“你写过什么材料”
```

Required answer:

```markdown
高频正式 PPT 汇报不算多，但我做过很多结构化成果输出：方案设计、能力拆解、架构决策、试点结果复盘、问题归因和改进建议。向上汇报的核心是把复杂技术问题翻译成业务价值、风险边界和决策选项。
```

- [ ] **Step 4: Add expanded question bank**

Under `## 7. 扩展题库`, add these question groups:

```markdown
### 7.1 伦理合规
### 7.2 多模态产品设计
### 7.3 Prompt 版本管理和效果对比
### 7.4 平台定价
### 7.5 竞品拆解
### 7.6 1 到 100 推广细节
```

Each group must include three bullets:

```markdown
- 可能问法：
- 答题抓手：
- 项目锚点：
```

- [ ] **Step 5: Validate extension document required content**

Run:

```bash
rg -n "追问底稿|试点反馈估算|年度收益 = 节省工时价值|从用户工作流开始|企业内部 AI 产品试点运营|高保真、可运行、可验证|向上汇报的核心|Prompt 版本管理" '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
wc -l '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: matches for every required phrase. Line count should be between 220 and 750 lines.

## Task 6: Final Verification, Diff Review, And Commit

**Files:**
- Verify: `.interview/battle-plan/作战计划-ai产品.md`
- Verify: `.interview/battle-plan/作战计划-ai产品-扩展材料.md`

- [ ] **Step 1: Check modified file scope**

Run:

```bash
git status --short -- '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: exactly these target files are shown for this task: main document modified, extension document untracked or added.

- [ ] **Step 2: Scan for weak unfinished language**

Run:

```bash
rg -n "需要完善|稍后|以后写|未完成|先空着" '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md' || true
```

Expected: no matches.

- [ ] **Step 3: Verify required section coverage**

Run:

```bash
rg -n "## 0\\. 作战理念|## 9\\. 7 天执行计划|## 7\\. 扩展题库|6\\.1 “2\\.2 天到 4 小时”是不是人工预估|7\\.1 伦理合规" '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: matches for the main document opening and closing sections, extension expanded question bank, the `2.2 天到 4 小时` anti-puncture script, and ethics expansion.

- [ ] **Step 4: Review diff manually**

Run:

```bash
git diff -- '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: diff only changes the AI product battle plan main document and adds the extension document. No backend, frontend, dependency, config, or unrelated interview files are included.

- [ ] **Step 5: Commit target documents only**

Run:

```bash
git add -- '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
git commit -m "docs: rebuild ai product interview battle plan" -- '.interview/battle-plan/作战计划-ai产品.md' '.interview/battle-plan/作战计划-ai产品-扩展材料.md'
```

Expected: commit succeeds and includes exactly the two target interview documents.

## Task 7: Final Knowledge Capture In Response

**Files:**
- No file changes.

- [ ] **Step 1: Summarize key design decisions**

Final response must include:

```markdown
关键设计决策：采用双层文档；主文档背诵，扩展文档追问；不包装全能 PM，主打工程纵深 AI 落地。
```

- [ ] **Step 2: Summarize verification results**

Final response must include the actual commands run and whether they passed:

```markdown
验证：已运行 rg 关键话术检查、wc 文档体量检查、git diff 范围检查。
```

- [ ] **Step 3: Summarize risk and next reuse checklist**

Final response must include:

```markdown
风险：文档重构不能替代真实面试演练；`2.2 天到 4 小时` 已降级为试点反馈估算，面试时不能再当严格实验结论讲。

下次复用清单：先确认岗位类型；再确认真实项目口径；再把高危数字区分为严格指标、试点信号、个人估算三类。
```
