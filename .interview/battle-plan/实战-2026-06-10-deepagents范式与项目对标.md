# 实战沉淀 · deepagents / DeepAgent 是什么 + deep vs shallow agent 范式

> 🎯 一句话 kernel（背这句）：Shallow agent 是「工具循环」，Deep agent 在循环外加了规划+文件系统(卸上下文)+子代理(隔离上下文)+HITL——OpsPilot 就是手搓的 deep agent。

## 母题速记
| 触发（面试官会问） | kernel（背这句） | 项目锚点（这次具体对标了什么） | 可能追问 |
|---|---|---|---|
| 了解 deepagents / DeepAgent 吗？干嘛的？ | 先分清三个东西：**deepagents**=LangChain 开源框架（建在 LangGraph 上，灵感来自 Claude Code）；**DeepAgent**=Abacus.AI 商业产品；**DeepMind**=Google 实验室 | 面试官 99% 问的是框架 deepagents，落点在「deep vs shallow」范式 | 那你项目算 deep 还是 shallow？ |
| deep agent 和普通 agent 差在哪 | Shallow=`while: 调工具`(ReAct 循环)；Deep=循环外加四件基础设施：**规划 / 文件系统当上下文 / 子代理 / 长期记忆+HITL** | OpsPilot 把这四件用 LangGraph 13 节点手工实现了 | 文件系统为什么能解决上下文？子代理隔离的是什么？ |
| deepagents / LangGraph / LangChain 怎么选 | 要**快速起步**→LangChain；要**底层可控状态机**→LangGraph；要**自主跑复杂长任务**→deepagents | OpsPilot 选 LangGraph 是因为要确定性编排 + 自建 checkpoint/HITL，不要框架替我做主 | 那你为什么不直接用 deepagents？ |
| 这俩适用什么场景 | deepagents=长链、多步、非确定性（调研/写代码/数据流水线）；不适用简单单步问答或强确定工作流 | OpsPilot 是长链多步 SRE 诊断，正好是 deep agent 的典型场景 | shallow 够用的场景举例？ |

<details>
<summary>📖 详细复盘 + 面试问答底稿（点开）</summary>

## 详细复盘

**问题背景**：面试官问「了解 deepmind、deepsgent 吗，干嘛的，适用什么场景」——拼写含混，先要判断指代对象，答错对象比答不全更糟。

**澄清三个易混对象**：
1. **deepagents**（小写、复数）= LangChain 2025 出的**开源 Agent 框架**，`pip install deepagents`。建在 LangGraph runtime 之上，灵感**直接来自 Claude Code**，目标是把 Claude Code / Manus / OpenAI Deep Research 那套「能干长任务」的核心架构抽成**模型无关、可定制**的 harness。提供 `create_deep_agent()` 开箱即用。Terminal Bench 2.0 用 Sonnet 4.5 约 42.65%，与 Claude Code 同档持平。
2. **DeepAgent**（Abacus.AI）= **商业通用智能体产品**，ChatLLM Teams 套件里，$10/月。卖点「不止聊天、直接执行」：完整 Linux 环境、浏览器自动化、多模态生成、多模型路由。对标 Manus 但便宜得多。
3. **DeepMind** = Google AI 研究实验室（AlphaGo/AlphaFold/Gemini）。若真问这个是考行业格局，不是 Agent 工程题。

**核心范式（面试真正考点）—— deep vs shallow agent**：
- **Shallow agent**：本质 `while True: 调工具`，一个 ReAct 循环。任务一长、步骤一多就崩——上下文塞满、跑偏、无法回头。
- **Deep agent**：同一个工具循环外面，加四件「基础设施」：
  1. **Planning**——内置 `write_todos`，先拆解再执行
  2. **File system 当上下文**——把大结果卸载到虚拟文件系统，绕开上下文窗口限制
  3. **Sub-agents**——子任务派给独立上下文的子 agent，隔离上下文污染
  4. **Long-term memory / skills + HITL**——长期记忆、技能注入、关键步骤人工审批

**OpsPilot ↔ deepagents 概念逐条对标**（这是接项目的钩子）：

| deepagents 概念 | OpsPilot 对应物 |
|---|---|
| Planning / write_todos | `planner` 节点 |
| Sub-agents 隔离上下文 | `evidence_fanout`（扇出取证） |
| File system 卸载上下文 | evidence 持久化到 DB / OSS 归档 |
| HITL 人工审批 | `risk_gate` + `approval_interrupt` |
| Long-term memory | `retrieve_memory` + RAG |
| 自我纠错（deep 的隐含项） | `critic` 节点回边（= M16 Reflection） |

**关键取舍（为什么不直接用 deepagents）**：deepagents 是「opinionated harness」，框架替你把规划/子代理/上下文管理做主了；OpsPilot 要的是**确定性编排 + 可控的自建 checkpoint/HITL**（0.0.55 没原生 interrupt，见 A6/A9），所以选更底层的 LangGraph 自己编排，把「框架替我做主」换成「我逐节点掌控」。

## 面试问答底稿

**Q：** 了解 deepagents 吗？干嘛的，适用什么场景？

**A（分两层）：**
- **第一层（通用/范式）**：deepagents 是 LangChain 建在 LangGraph 上的开源框架，灵感来自 Claude Code。它的核心价值是把「deep agent」范式做成开箱即用——相对 shallow agent（纯工具循环）多了四件事：规划、文件系统卸上下文、子代理隔离上下文、长期记忆+HITL。适用长链/多步/非确定性任务（深度调研、写代码、数据流水线），不适用简单单步问答。
- **第二层（但我项目实际上…）**：我的 OpsPilot 就是一个手搓的 deep agent——这四件我都用 LangGraph 13 节点实现了：planner 对应规划、evidence_fanout 对应子代理隔离、evidence 落 DB/OSS 对应文件系统卸上下文、risk_gate+approval 对应 HITL。我没用 deepagents 这个库，是因为我要确定性编排 + 自建 checkpoint/HITL 的可控性，不想让 opinionated 框架替我做主。所以我对 deep agent 范式不是看文档知道的，是逐个节点踩出来的。

**诚实边界：** 我没有用 deepagents 这个库本身做过项目，对它的 API 细节（`create_deep_agent` 的参数、middleware 机制）只停在读文档层面。我能讲清楚的是**它抽象的那套范式**，以及**用更底层的 LangGraph 把同一套范式自己实现的取舍**——这是我的一手经验，库的使用经验不是。

**反问加分**：你们 Agent 落地是直接用 deepagents 这类高层 harness，还是 LangGraph 自己编排？质量门禁/HITL 怎么做的？

## 关键文件速查
| 关注点 | file:line |
|---|---|
| 13 节点编排 | `backend/app/graph/builder.py` |
| planner / evidence_fanout / critic / risk_gate 实现 | `backend/app/graph/nodes/__init__.py` |
| 自建 checkpoint + evidence 持久化 | `backend/app/services/graph_runner.py` |
| HITL 审批续跑 | `dispatcher-resume机制.md`（面试库） |

## 参考来源
- LangChain Deep Agents 官方：https://www.langchain.com/deep-agents
- LangChain Docs（overview + 选型口诀）：https://docs.langchain.com/oss/python/deepagents/overview
- DeepWiki langchain-ai/deepagents：https://deepwiki.com/langchain-ai/deepagents
- Abacus.AI DeepAgent：https://deepagent.abacus.ai/

</details>
