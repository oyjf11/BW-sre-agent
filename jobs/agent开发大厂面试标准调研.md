# Agent 开发领域中国大陆大厂面试标准调研

公开招聘 JD、面经文章和大厂相关岗位描述显示：中国大陆大厂现在招 Agent 开发，不是单纯考“会不会调 LangChain”，而是考“能不能把 LLM + RAG + Tool Use + Workflow + 后端工程 + 业务指标”做成可上线、可评估、可观测、可控的系统。

## 参考来源

- 腾讯大模型应用 Agent 开发工程师：强调 RAG、Agent、ChatBI、Data+AI、供应链预测、风险智能体等落地方向。来源：https://www.mianshima.com/job/1/1924747914551336960
- 字节大模型应用开发工程师：强调 Agent 任务规划、工具调用、对话管理、RAG、检索召回重排、Prompt 版本管理、评测集、后端架构、缓存与监控。来源：https://www.nowcoder.com/jobs/detail/428910
- 美团商业分析智能体 BA Agent：强调商业数据理解、数据仓库、BI、NL2SQL、多 Agent、复杂推理、工具使用、量化实验。来源：https://www.mianshima.com/job/7/3690292460
- 京东 AI Agent 开发工程师：强调 Tool Use、多轮对话管理、记忆/上下文管理、任务计划与执行、RAG、向量索引、数据治理、安全审计。来源：https://www.mianshima.com/job/9/154863
- 快手大模型 AI Agent 开发工程师：强调任务规划、工具调用、记忆管理、多智能体协同、可观测、评测、稳定性、部署体系。来源：https://www.nowcoder.com/jobs/detail/441964
- 小红书 AI 应用架构工程师：强调通用 Agent 层、多模型调用、动态 Workflow、自动路由、Function Call、ReAct、Tool 编排、可配置可调试平台。来源：https://jobs.niuqizp.com/job-vk85555aN.html
- 百度开发者中心面经：系统梳理 RAG、Agent、架构设计、优化策略等高频考点。来源：https://developer.baidu.com/article/detail.html?id=5573507

## 一、候选人分层标准

### 初级合格线

- 会 Python / Java / Go 至少一门后端语言。
- 理解 LLM 基本调用、Prompt、上下文窗口、temperature、token 成本。
- 会用 LangChain / LangGraph / LlamaIndex / Dify / Coze 之一做 Demo。
- 做过基础 RAG：文档切分、embedding、向量库、检索、拼接 prompt。
- 能解释 Function Calling / Tool Use 的基本流程。
- 有一个能跑通的 side project 或内部工具。

### 中级合格线

- 能独立设计 Agent 工作流，而不是只写 prompt。
- 理解 Agent Loop、Planning、ReAct、Reflection、Multi-Agent 的适用边界。
- 能设计 Tool Registry、参数 schema、工具超时、重试、错误处理。
- 能做 RAG 优化：hybrid search、rerank、query rewrite、召回评估。
- 有后端工程能力：API 设计、异步任务、缓存、日志、监控、数据库、消息队列。
- 能把 Agent 放进真实业务流程，比如客服、数据分析、内容审核、运营自动化、供应链预测。
- 知道如何评估 Agent：任务成功率、人工接管率、工具失败率、成本、延迟、满意度。

### 高级 / 专家标准

- 能设计生产级 Agent 平台或通用 Agent Runtime。
- 能抽象多模型调用、动态 Workflow、自动路由、Tool 编排、记忆管理、权限体系。
- 熟悉 LLMOps / AIOps：Prompt 版本管理、评测集、回放、灰度、监控、成本治理。
- 能处理复杂业务问题：NL2SQL、ChatBI、供应链预测、智能客服、广告投放、智能选品。
- 能推动跨团队落地，和产品、算法、数据、业务团队一起定义指标。
- 对模型后训练、SFT、RLHF、AgentRL、RAG 评测、推理优化有理解或实践更加分。

## 二、技术考察模块

### 1. Agent 架构

大厂会重点问：

- Agent 和 Chatbot 的区别是什么？
- Agent Loop 怎么设计？
- ReAct、Plan-and-Execute、Reflection、Multi-Agent 分别适合什么场景？
- 为什么生产 Agent 更适合用 Workflow / Graph，而不是完全自由推理？
- 怎么防止 Agent 无限循环？
- 怎么处理中断、恢复、重试、人工审批？

判断标准：

- 只会说“Agent 会调用工具”是不够的。
- 合格回答要讲出：状态机、工具链、任务规划、观察反馈、终止条件、错误处理、可观测性。
- 高级回答要能讲：Workflow Agent 比自由 Agent 更适合高风险生产业务。

### 2. LangGraph / Workflow 编排

常考点：

- LangGraph 的 node、edge、state 是什么？
- conditional edge 怎么用？
- 如何实现 human-in-the-loop？
- 如何从失败节点恢复？
- 如何设计多 Agent 协作？
- LangGraph 和 LangChain 的区别？

大厂看重：

- 你是否理解“图”是为了控制复杂流程。
- 是否能解释分支、循环、重试、审批、中断、恢复。
- 是否能把 Agent 设计成可调试、可观测、可上线的系统。

### 3. Tool Use / Function Calling

常考点：

- Function Calling 的完整链路是什么？
- 工具参数 schema 怎么设计？
- 工具调用失败怎么办？
- 工具调用如何做幂等？
- 如何防止模型调用危险工具？
- 工具结果是否应该原样返回给模型？

判断标准：

- 初级：知道模型生成函数参数，后端执行。
- 中级：知道 schema、权限、超时、重试、审计。
- 高级：知道风险分级、审批、人机协同、工具调用可靠性、幂等执行。

### 4. RAG

常考点：

- RAG 的完整流程是什么？
- chunk 怎么切？
- 向量检索和关键词检索区别？
- hybrid search 为什么重要？
- rerank 解决什么问题？
- RAG 召回率怎么评估？
- RAG 幻觉怎么处理？
- GraphRAG 适合什么场景？

大厂标准：

- 不能只说“把文档放进向量库”。
- 要能讲清楚：数据清洗、切分、embedding、索引、召回、重排、上下文构造、引用、评测。
- 如果岗位偏数据分析 / BI，还会问 NL2SQL、Text-to-SQL、数据权限、血缘、口径一致性。

### 5. Prompt Engineering

常考点：

- System Prompt 应该写什么？
- few-shot 有什么作用？
- temperature 怎么影响输出？
- 如何保证 JSON 输出稳定？
- Prompt 注入怎么防？
- Prompt 如何版本管理？

大厂标准：

- Prompt 只是软约束，不能当安全边界。
- 合格回答必须提到 schema 校验、工具权限、后处理、评测集、版本管理。

### 6. 评测体系

现在大厂非常重视这个。

常考点：

- Agent 怎么评估？
- RAG 怎么评估？
- Prompt 改了怎么判断变好还是变坏？
- 如何构造评测集？
- 线上效果和离线效果不一致怎么办？

常见指标：

- 任务完成率
- 工具调用成功率
- 首次解决率
- 人工接管率
- 幻觉率
- 平均耗时
- token 成本
- 用户满意度
- RAG 召回率 / 命中率 / 上下文相关性
- 业务指标，比如 GMV、转化率、库存周转、客服解决率

### 7. 后端工程能力

公开 JD 中反复出现的能力：

- API 设计
- 服务拆分
- 缓存
- 监控
- 日志
- 消息队列
- 并发
- 数据库
- 服务稳定性
- 部署运维
- Docker / Kubernetes

面试常问：

- 长任务 API 怎么设计？
- SSE / WebSocket / 轮询怎么选？
- 如何做任务队列和失败重试？
- 如何防止重复执行？
- 如何做 trace_id？
- 如何监控 Agent 线上质量？
- 如何控制 LLM 调用成本？

### 8. 业务理解

这个岗位不是纯算法岗，也不是纯后端岗。

大厂会问：

- 智能客服 Agent 怎么落地？
- 选品 Agent 需要哪些数据？
- 补货预测怎么评估？
- 广告 Agent 怎么优化 ROI？
- 商业分析 Agent 如何处理指标口径？
- 跨境电商有什么特殊复杂性？

优秀回答要包含：

- 业务目标
- 数据来源
- 决策流程
- 工具接口
- 风险边界
- 人工审核
- 评估指标
- 灰度上线

## 三、典型面试轮次

### 1. 一面：基础工程 + LLM 应用基础

重点考：

- Python / Java / Go 基础
- API 设计
- 数据库
- 并发
- RAG 基础
- Function Calling
- 项目细节

常见判断：你是不是只调过 API，还是独立做过完整模块。

### 2. 二面：Agent 架构 + 系统设计

重点考：

- Agent Runtime 设计
- Workflow / LangGraph
- Tool Registry
- 记忆管理
- 多 Agent
- 评测体系
- 容错与恢复

常见题：设计一个智能客服 Agent / 智能选品 Agent / BI Agent。

### 3. 三面：业务落地 + 稳定性 + Owner 意识

重点考：

- 如何从 0 到 1 落地
- 如何定义业务指标
- 如何灰度上线
- 如何监控效果
- 如何处理线上事故
- 如何推动产品、算法、数据协作

### 4. 加面 / 专家面：前沿与深度

可能问：

- AgentRL
- SFT / RLHF / DPO
- long context
- GraphRAG
- 多模态 Agent
- NL2SQL
- 推理成本优化
- 模型路由
- 可验证奖励
- LLMOps 平台化

## 四、面试评分 Rubric

### 1 分：概念型

- 知道 RAG、Agent、LangChain 名词。
- 做过简单 Demo。
- 不能解释生产问题。

### 2 分：工具型

- 会接 LLM API。
- 会搭基础 RAG。
- 会 Function Calling。
- 但缺少评测、监控、可靠性设计。

### 3 分：工程型

- 能独立做一个可用 Agent 服务。
- 有 API、日志、错误处理、工具 schema、数据库和任务状态。
- 能解释失败重试、超时、幂等。

### 4 分：生产型

- 做过真实业务上线。
- 有评测集、灰度、监控、成本治理。
- 能处理权限、审批、人工接管、回滚。
- 能用业务指标证明效果。

### 5 分：平台 / 专家型

- 能设计通用 Agent 平台。
- 能抽象 Workflow、Tool、Memory、Eval、Model Router。
- 能支持多个业务线快速接入。
- 对模型训练、RAG、Agent 推理模式、LLMOps 有系统理解。

## 五、和当前项目的匹配度

当前 SRE Agent 项目和这个 JD 的匹配点比较明确：

- LangGraph 工作流：匹配 Graph-based Agents / Workflow Agents。
- 13 节点流程：匹配任务规划、证据收集、诊断、修复、验证、RCA。
- Tool Gateway：匹配 Tool Use / Function Calling / 工具可靠性。
- Risk Gate + Approval：匹配生产 Agent 可控、可靠、人机协同。
- Checkpoint / Resume：匹配长任务恢复和 human-in-the-loop。
- EventBus / SSE：匹配 Agent 日志监控和可观测性。
- LLM fallback：匹配模型调用可靠性。
- Mock / Real Adapter：匹配从 Demo 到生产工具接入。

短板也明显：

- 不是电商 / 跨境 / 供应链业务场景。
- RAG 能力如果只是 retrieve_memory，还需要补充完整知识库链路。
- 缺少向量数据库、hybrid search、rerank、评测集。
- 缺少推荐 / 预测 / NLP 算法模块。
- 缺少消息队列、缓存、分布式任务调度等大规模生产能力展示。

## 六、建议面试时的项目表述

不要说：

> 我做了一个 LangGraph Agent。

要说：

> 我做的是一个生产化思路的 SRE Workflow Agent。它不是简单调用 LLM，而是把故障处置拆成 intake、triage、planning、evidence、diagnosis、critic、remediation、risk gate、approval、execution、verification、RCA 等节点。系统有状态机、checkpoint、工具网关、风险审批、事件流、失败恢复和 LLM fallback。虽然业务是 SRE，但架构可以迁移到电商客服、补货、选品、广告优化等场景。

这样更贴合大陆大厂 Agent 岗位的判断标准：能落地、能控制风险、能解释业务价值。
