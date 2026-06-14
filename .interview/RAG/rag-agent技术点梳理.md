# 这个 RAG 项目用到了哪些技术点（面试沉淀）

代码位置：`.interview/RAG/server/src/modules/`，是个 NestJS + React 的 AI 聊天项目，自带知识库。整体特点：**RAG 的基本链路是齐的，但都是朴素实现，没有上前沿优化**。面试时可以拿它讲"从 0 到 1 怎么搭一个 RAG"，也可以用来回答"如果让你优化会怎么改"。

---

## 一、RAG 链路，一步一步过

### 1. 文档怎么切（chunking）
文件：`knowledge/chunker.service.ts`

策略是"先按段落分，段落太长再用滑动窗口切"：
- CHUNK_SIZE = 600
- OVERLAP = 80
- MIN_CHUNK_LENGTH = 20（太短的碎片直接扔）

这是最常见的 chunking 思路，没有按语义边界（比如用模型判断句子是否相关）去切，纯粹按字数。

### 2. 怎么生成向量（embedding）
文件：`knowledge/embedding.service.ts`

调的是 SiliconFlow 的 API，模型是 BAAI/bge-m3。批量请求，每批 25 条，每批之间隔 200ms，主要是怕触发 API 限流。

### 3. 向量存哪（向量存储）
文件：`database.service.ts`

没用专门的向量数据库（faiss、pgvector、milvus 这些都没用），就是 SQLite 一张表 `kb_chunks`，embedding 列直接存成 JSON 字符串。

这点面试官如果问"为什么不用向量数据库"，可以答：数据量小的场景用 SQLite 完全够，向量数据库的优势（近似最近邻索引、海量数据下的检索速度）在小规模下体现不出来，反而增加部署复杂度。

### 4. 怎么检索

**向量检索**（`retrieval.service.ts`）：把 query 也 embedding 一下，然后跟每条 chunk 的向量算余弦相似度（dot product / 两个向量的模长乘积），设了个阈值 VEC_THRESHOLD=0.3，低于这个就不要。

**关键词检索**：用 SQLite 的 FTS5 全文索引，MATCH 语法，多个关键词用 OR 拼起来。

**两路融合**：用的是 RRF（Reciprocal Rank Fusion，倒数排名融合），K=60。具体做法是向量检索和关键词检索各自先取 topK*3 的结果（怕漏掉），然后按照"1/(K+排名)"算融合分数，重新排序后取最终的 topK=5。

这就是**混合检索（hybrid search）**，向量检索负责语义相似，关键词检索负责精确匹配（比如查个具体的函数名、报错码，向量检索经常找不准，关键词检索一查就到）。

### 5. Prompt 怎么拼
文件：`chat.controller.ts`

把检索到的 chunk 按 `[N] (来源: 文件名)\n 内容` 的格式拼起来，塞进 system message。带来源标注是为了让模型在回答时能说"这个信息来自哪个文档"，也方便排查是不是检索错了。

---

## 二、这个项目里没有的 RAG 技术点（面试查漏补缺）

这几个是常见 RAG 优化项，这个项目都**没做**，但都是高频考点，得自己能讲清楚"是什么、解决什么问题、怎么实现"：

- **Query 改写/扩展**：用户的原始 query 直接拿去检索了，没有让模型先把 query 改写成更适合检索的形式（比如把口语化的问题改写成关键词，或者生成多个角度的 query 分别检索再合并）。问题场景：用户问得很模糊或者带错别字，原始 query 检索效果差。
- **Cross-encoder rerank（精排）**：项目里的"融合排序"（RRF）只是把两路检索结果按排名重新排了一下，不是真正意义上的 rerank。真正的 rerank 是用一个专门的模型（比如 bge-reranker）对 query 和每个候选 chunk 一对一打分，这个打分比向量相似度更准，但更慢，所以一般放在粗筛之后。
- **上下文压缩/摘要**：多轮对话历史是直接截断最近 20 条（`chat.controller.ts`），没有做摘要压缩。长对话场景下，前面的重要信息可能被截断丢掉。
- **向量微调**：用的是通用的 bge-m3，没有针对自己的领域数据做微调，检索效果天花板受限于通用模型对这个领域词汇的理解。

---

## 三、Agent 相关技术点

### 1. Streaming（流式输出）
文件：`chat.controller.ts`

用 SSE（Server-Sent Events），把模型输出的内容按 chunk 推给前端，还专门区分了"思考过程"（reasoning_content，针对 deepseek-reasoner 这种带推理链的模型）和"正式回答"两种 chunk 类型分别推送。

### 2. 多轮对话管理
历史记录直接 `slice(-20)`，只保留最近 20 条发给模型，硬截断，防止 token 超限。没有摘要、没有重要性筛选。

### 3. 意图识别 + 两阶段生成
文件：`multimodal/multimodal.service.ts`

多模态场景下分两步：第一步让模型分析用户意图，输出一个结构化的 IntentPlan（包含要写的摘要、要生成的图片 prompt、要画的图表 spec）；第二步根据这个 plan 去生成实际内容（带 [IMAGE_N] 占位符的 markdown + mermaid 图表）。

这其实就是一个简化版的"规划-执行"两阶段 agent，但没有 function calling，规划结果就是一段结构化文本，靠模型自己按格式输出。

### 4. 多模型适配器
文件：`ai/ai.service.ts`

支持 DeepSeek、豆包、Kimi、千问、MiniMax 等多个厂商，每个厂商有自己的 buildRequestBody（怎么构造请求）和 parseChunk（怎么解析流式返回）。还有 fast/think/expert 三档参数预设（temperature 和 max_tokens 不同）。

### 5. 没有的 Agent 技术点
- **Function calling / tool use**：完全没有，模型只负责生成文本，不会调用外部工具。
- **真正的 ReAct 式多步推理**：上面说的"两阶段生成"是固定两步，不是模型自己决定要不要调用工具、调用几次。

---

## 四、几个工程上的小细节（加分项）

- RAG 检索如果报错，用 try-catch 接住，不影响正常聊天流程（降级处理）。
- SQLite 开了 WAL 模式 + 事务写入，支持并发读写不冲突。
- API Key 的查找顺序是：用户自己配置的 > 数据库里存的 > 环境变量里的，给了用户自带 key 的灵活性。
- 检测到负面情绪自动生成工单——这是一个"agent 触发业务动作"的小例子，虽然简单，但可以用来回答"agent 怎么和业务系统联动"这类问题。

---

## 五、面试自测

被问到这个项目，应该能顺着讲出来的几条线：

1. **检索链路**：chunking → embedding → 向量检索 + FTS5 关键词检索 → RRF 融合 → 拼 prompt。每一步用了什么参数（600/80、topK*3、RRF K=60、topK=5）要记住。
2. **混合检索为什么有用**：向量检索强在语义，关键词检索强在精确匹配专有名词/代码片段，两者互补。
3. **如果让你优化，你会加什么**：query 改写、cross-encoder rerank、上下文摘要压缩、领域微调——每个都要能说出"现在缺了它会有什么具体问题"。
4. **RRF 和 rerank 的区别**：RRF 是对已有排名做融合，不需要额外模型；rerank 是用模型对 query-doc 对重新打分，更准但更贵。这两个容易被面试官拿来对比问。
