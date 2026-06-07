# 中国大陆 Agent 应用开发工程师面试技术考察角度

> 整理时间：2026-06-06
> 适用岗位：AI Agent 工程师 / LLM 应用开发 / 智能体开发 / MAS 工程师

---

## 一、大模型基础（必考）

### 1.1 模型能力边界

- Prompt Engineering：CoT（Chain of Thought）、少样本学习、指令微调 vs 提示词工程的选择
- Token 计算与上下文窗口：长上下文管理、截断策略、Sliding Window
- Temperature / Top-p 参数对输出多样性的影响
- 模型幻觉（Hallucination）产���原因及缓解手段
- Function Calling / Tool Use 的底层机制（JSON Schema → 模型输出解析）

### 1.2 常见考题

- GPT-4 / Claude / Qwen 等模型的核心差异，如何选型？
- 如何评估一个模型对任务的适用性？
- 输出格式不稳定时如何处理？（Retry + 结构化 prompt + JSON Mode）

---

## 二、RAG（检索增强生成）

### 2.1 核心链路

```
文档 → 切分（Chunking）→ Embedding → 向量库 → 检索（相似度/BM25/混合）→ Rerank → 注入 Context → LLM
```

### 2.2 考察重点

| 模块 | 考察点 |
|------|--------|
| Chunking 策略 | 固定长度 vs 语义切分，overlap 设置，父子块检索 |
| Embedding 选型 | text-embedding-3 / BGE / M3E，向量维度 vs 效果 |
| 向量库选型 | Milvus / Weaviate / Qdrant / pgvector 差异，生产规模考量 |
| 检索策略 | 稠密检索 vs 稀疏检索（BM25）vs 混合检索（RRF 融合） |
| Rerank | Cross-encoder vs bi-encoder，延迟代价 |
| 评估指标 | Recall@K、MRR、NDCG、faithfulness、answer relevance |

### 2.3 常见陷阱题

- 向量相似度高但答案质量低——为什么？（语义漂移、切块破坏上下文）
- RAG vs Fine-tune 如何选择？（知识更新频率、数据量、推理成本）
- 多跳问答（Multi-hop QA）如何处理？（子问题分解 + 多轮检索）

---

## 三、Agent 框架与编排

### 3.1 主流框架对比

| 框架 | 适用场景 | 核心特性 |
|------|----------|----------|
| LangChain | 快速原型，工具链组合 | Chain / Agent / Tool 抽象 |
| LangGraph | 复杂状态机，多节点图 | StateGraph + 条件路由 + checkpoint |
| AutoGen | 多智能体对话 | 角色对话 + 代码执行 |
| CrewAI | 团队协作场景 | 角色分工 + 任务流转 |
| Dify / Coze | 低代码 Agent | 可视化编排 |

### 3.2 LangGraph 深度考察（当前热点，已经过多源验证）

**Checkpoint / Persistence（高频考点）**
- `thread_id` 是 checkpoint 主键，调用图时必须在 `config["configurable"]["thread_id"]` 中指定
- CheckpointTuple 四个核心字段：`channel_values`（全量状态快照）、`channel_versions`（各 channel 版本向量）、`versions_seen`（节点已见版本追踪）、`pending_writes`（未提交写操作列表）
- 生产级：`InMemorySaver` 替换为 `RedisSaver`（langgraph-checkpoint-redis 包），通过 `from_conn_string` 上下文管理器接入

**条件路由与并发（高频考点）**
- `add_conditional_edges` 的 `path` 参数支持同步/异步 callable 和 Runnable；`path_map` 可选，不提供时 path 函数直接返回节点名称
- `Send` 实现 Map-Reduce 并发：`return [Send('generate_joke', {'subject': s}) for s in state['subjects']]`
- **关键**：Send 的局部状态与主图状态可以不同（状态隔离），面试必知
- `Send(node, arg)` 是图框架里的写法；SDK 客户端版本用 `input` 参数，需区分语境

**Human-in-the-Loop（高频考点）**
- `interrupt()` 强依赖 checkpointer，无 checkpointer 则无法暂停
- payload 暴露方式：stream API 用 `stream.interrupts`，invoke v1 用 `result['__interrupt__']`，v2 推荐 `result.interrupts`
- 恢复：`Command(resume=<人工输入>)`
- 工具层面三种审批类型：`accept`（直接执行原始 tool_input）、`edit`（修改 args 后执行）、`response`（作为用户反馈返回 LLM）

**State 序列化（高频坑）**
- Pydantic model 从 checkpoint 反序列化后变成 dict，访问属性需兼容：`ticket.service if hasattr(ticket, 'service') else ticket.get('service')`

**Streaming**：事件流 token-level vs node-level 输出的区别与选择

### 3.3 Agent 模式（已验证）

- **ReAct**（arXiv:2210.03629）：交替生成 reasoning traces 和 task-specific actions，使 LLM 动态调整规划并与外部工具交互。LangGraph 实现：`llm_call` → `tool_node` → 条件判断（有 tool_calls 则循环，否则 END），可用 `create_react_agent` 预构建。**注意**：ReAct 并非在所有基准上全面超越 CoT-only，Fever 部分子集上两者可持平，面试应表述为"在多数基准任务上超越纯推理或纯行动基线"
- **HuggingGPT**（arXiv:2303.11366）：以 ChatGPT 作 controller，四阶段流水线（任务规划→模型选择→任务执行→响应生成），从 HuggingFace 按描述匹配专家模型——LLM 作 planner 的多模型编排经典范例
- **Plan-and-Execute**：先生成计划再逐步执行，避免短视
- **Reflexion**：自我反思与迭代改进
- **Tree of Thoughts（ToT）**：搜索树展开，适合复杂推理
- **Multi-Agent**：子 Agent 作为 tool 被 orchestrator 调用（工具模式）vs 子 Agent 作为独立子图被 invoke（子图模式），两者状态隔离和 checkpointer 继承规则不同

---

## 四、工具调用（Tool Use）

### 4.1 设计原则

- 工具描述的 prompt 写法：名称、参数、返回值、使用时机
- 工具失败处理：重试、fallback、错误信息反馈给 LLM
- 工具安全性：参数校验（JSON Schema）、权限控制、审计日志

### 4.2 常见考题

- 如何防止 Agent 调用危险工具？（Tool Gateway + 白名单 + human approval）
- 工具返回结果过长时如何处理？（摘要压缩、分页、结构化截取）
- 工具调用幂等性如何保证？（唯一 call_id + 状态机去重）

---

## 五、记忆与上下文管理

### 5.1 记忆类型

| 类型 | 实现 | 适用场景 |
|------|------|----------|
| 短期记忆 | 对话历史 in context | 单轮/多轮对话 |
| 长期记忆 | 向量库存储 + 检索 | 用户偏好、历史事件 |
| Episodic Memory | 总结压缩后存储 | 长会话摘要 |
| 工作记忆 | Graph State / Agent Scratchpad | 复杂任务推进中间状态 |

### 5.2 考察重点

- 上下文超限时的压缩策略（summarize、滑动窗口、重要信息提取）
- 多轮对话中记忆的选择性遗忘机制
- 用户级 vs 会话级记忆的隔离

---

## 六、多智能体系统（MAS）

### 6.1 设计模式

- **Orchestrator-Worker**：中央调度，适合任务明确的并行场景
- **Peer-to-Peer**：智能体相互协作，适合探索型任务
- **Supervisor + Specialist Pool**：主管分配，专家执行
- **Debate / Critic**：多 Agent 对同一问题辩论，提升答案质量

### 6.2 工程挑战

- Agent 间通信协议设计（消息格式标准化）
- 任务分配策略（能力标签 + 负载均衡）
- 死锁/循环调用检测
- 结果聚合与冲突解决

---

## 七、评估与测试

### 7.1 LLM-as-Judge

- 使用强模型（GPT-4）评估弱模型输出
- 评估维度：faithfulness（忠实度）、relevance（相关性）、correctness（正确性）
- 偏差控制：position bias、verbosity bias、自一致性验证

### 7.2 离线评测

- 构建评测数据集：Golden QA pairs、人工标注
- 指标体系：BLEU/ROUGE（文本相似）、精确匹配、语义相似度
- A/B 对比评测框架

### 7.3 在线监控

- 异常输出检测（长度异常、拒答、幻觉）
- 延迟/Token 消耗监控
- 用户反馈闭环

---

## 八、工程化与生产落地

### 8.1 性能优化

- **Prompt Cache**：前缀缓存减少重复 Token 计算（Anthropic/OpenAI 均支持）
- **并行调用**：多工具/多 Agent 并发，避免串行等待
- **Streaming**：首 Token 时间（TTFT）vs 整体延迟权衡
- **模型路由**：复杂任务用大模型，简单任务用小模型

### 8.2 可观测性

- **Tracing**：LangSmith / Langfuse / Phoenix 的 span 追踪
- **日志结构化**：每个节点的 input/output 记录
- **成本追踪**：Token 消耗按节点统计

### 8.3 安全��

- Prompt Injection 防御（输入过滤、越权检测）
- 输出审核（内容安全、敏感信息脱敏）
- Human-in-the-loop 关键操作审批

---

## 九、系统设计题（高频）

### 题型示例

1. **设计一个客服 Agent 系统**：如何处理多轮对话、意图识别、知识库检索、人工接管？
2. **设计 SRE 故障处置 Agent**：如何编排证据收集→诊断→修复→验证流程？
3. **设计代码审查 Agent**：如何拆解任务、调用工具、处理大文件？
4. **设计 RAG 知识库系统**：如何保证检索质量、处理文档更新、支持多语言？

### 考察维度

- 需求拆解能力（业务理解 → 技术映射）
- 容错与降级设计
- 扩展性（增加新工具/新节点的成本）
- 成本控制意识（Token 消耗、API 调用次数）

---

## 十、行为面试 / 项目深挖

### 常见追问方向

- "你的 Agent 卡住时怎么定位？" → 考察可观测性与调试能力
- "LLM 输出不稳定时你怎么办？" → 考察鲁棒性设计
- "上线后 Token 消耗超预期怎么处理？" → 考察成本优化能力
- "多 Agent 结果冲突时如何决策？" → 考察架构设计
- "你们的 RAG 召回率低怎么改进？" → 考察 RAG 调优经验

---

## 十一、加分项（2025-2026 热点）

| 方向 | 关键词 |
|------|--------|
| MCP（Model Context Protocol） | Anthropic 标准，工具/资源/提示标准化接入 |
| Agent2Agent 协议 | Google 推进的跨 Agent 通信标准 |
| 计算机使用（Computer Use） | 屏幕操作、GUI Agent |
| 长上下文模型 | Gemini 1M / Claude 1M，对 RAG 的冲击与互补 |
| 小模型 On-device Agent | Phi-3 / Qwen2.5-0.5B 端侧推理 |
| Agentic RAG | Agent 主动决策检索时机和策略 |

---

## 参考资料

- LangGraph 官方文档：https://langchain-ai.github.io/langgraph/
- LangChain 中文社区：https://python.langchain.com.cn/
- Anthropic MCP 规范：https://modelcontextprotocol.io/
- AutoGen 论文：https://arxiv.org/abs/2308.08155
- ReAct 论文：https://arxiv.org/abs/2210.03629
- LLM-as-Judge：https://arxiv.org/abs/2306.05685
