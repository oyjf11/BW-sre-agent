# RAG 评测中的对比方案与评分尺度

## 问题背景

本评测脚本跑了 **5 路检索方案 + 2 路拆分方案**，但它们输出的分数来自**完全不同**的数学世界，直接比大小毫无意义。因此需引入**尺度无关的排序质量指标**来公平对比。

---

## Part 1：对比方案总览

| 方案 | 检索方式 | 分数来源 | 尺度性质 |
|------|----------|----------|----------|
| A 裸向量 | 原始口语 → embedding → cosine | cosine 相似度 | 内积归一化，0~1 |
| B +改写 | 规则改写 → embedding → cosine | cosine 相似度 | 同上 |
| C +rerank | B 改写 → 向量粗排 → gte-rerank 精排 | gte-rerank relevance_score | cross-encoder 输出，无固定范围 |
| D 关键词 | 改写 → 倒排索引 IDF 加权命中 | token overlap 归一化 | 0~1，受 IDF 分布影响 |
| E Hybrid | 向量 cosine × 0.6 + 关键词 IDF × 0.4 | 加权融合 | 0~1（α=0.6 可调） |
| F 规则拆分 | 规则拆分 → 各自规则改写 → embedding → cosine 检索 → 合并去重 | cosine 相似度（聚合取 max） | 内积归一化，0~1 |
| G LLM拆分 | LLM 拆分 → 各自规则改写 → embedding → cosine 检索 → 合并去重 | cosine 相似度（聚合取 max） | 内积归一化，0~1 |

---

## Part 2：7 种评分尺度

### 1. Cosine 相似度（A、B 路使用）

#### 数学定义

$$\text{cosine}(a, b) = \frac{a \cdot b}{\|a\| \cdot \|b\|}$$

#### 工作原理
1. 把 query 和 document 分别用 embedding 模型（`text-embedding-v4`）映射到高维向量空间
2. 计算两个向量的夹角余弦值
3. 值越接近 1 表示语义越相近

#### 性质
- **范围固定**：$[0, 1]$（对归一化向量）
- **对称性**：$\text{cosine}(a, b) = \text{cosine}(b, a)$
- **语义空间依赖**：分数受 embedding 模型训练数据分布影响，不同模型不可直接比较

#### 适用场景
- 向量检索的粗排/初排阶段
- 同一 embedding 模型下的相对排序

#### 局限
- 分数绝对值在不同模型间不可比
- 多意图场景下整句 embedding 会模糊次要意图

---

### 2. Rerank Relevance Score（C 路使用）

#### 工作原理
rerank 模型（`gte-rerank-v2`）是 **cross-encoder**：
1. 将 query 和每个候选 document **拼接**成一对输入
2. 经过 Transformer 完整编码，直接输出一个相关性分数
3. 每一层都有 query-document 交互，比 bi-encoder 精准得多

#### 与 Cosine 的关键区别

| 维度 | Cosine（bi-encoder） | Rerank（cross-encoder） |
|------|---------------------|------------------------|
| 编码方式 | query 和 doc 独立编码 | query + doc 联合编码 |
| 交互深度 | 仅在内积时交汇 | 每层 Transformer 都交互 |
| 速度 | 快（可预计算 doc 向量） | 慢（每个 query 要重新算） |
| 精度 | 较低 | 更高 |
| 分数范围 | [0, 1] 固定 | 不固定，由分类头决定 |

#### 性质
- **范围不固定**：可能 >1 或 <0，不同模型尺度不同
- **只可同模型内比较**：和 cosine 分数横比无意义
- **margin 天然更大**：cross-encoder 更敢拉大 top1 和 top2 的差距

#### 适用场景
- 向量粗排后的精排/重排序
- 需要高置信度门控的生产场景

---

### 3. IDF 加权关键词分数（D 路使用）

#### 工作原理
1. 对知识库所有子块做 tokenize（中文单字+二元组+英文词）
2. 构建倒排索引：token → 子块列表
3. 对 query 同样 tokenize，计算每个 token 的 IDF 权重：$\text{idf}(t) = \log\frac{N+1}{df(t)+1} + 1$
4. 对每个子块累加命中 token 的 IDF 值，归一化到 [0,1]
5. small-to-big 聚合到父块

#### 性质
- **范围**：[0, 1]（IDF 和归一化后）
- **与语义无关**：纯字面匹配，对同义词/口语表达不敏感
- **对精确词极敏感**：单字 query "看板" 命中率极高，因为子块恰好包含该词

#### 适用场景
- 用户 query 包含精确领域术语时
- 与向量检索互补（向量管语义，关键词管精确匹配）

#### 局限
- 口语绕圈表达全面失能（例："别发邮件了" → 关键词全跑偏到 CRM）
- medium 难度档下 D 路命中率仅 67%，对比 B 路 100%

---

### 4. Hybrid 融合分数（E 路使用）

#### 数学定义

$$\text{hybrid}_i = \alpha \cdot \text{cosine}_i + (1-\alpha) \cdot \text{kw}_i$$

其中 $\alpha = 0.6$，cosine 和 keyword 分数各自归一化到 [0,1]。

#### 性质
- **范围**：[0, 1]
- **融合策略**：向量权重更高（0.6），关键词做辅助纠偏
- **门控特性优于单独方案**：E 路在阈值 0.072 即达 F1=1.0，仅拒答 5.9%

#### 适用场景
- 希望同时覆盖语义相似和精确匹配的场景
- 需要更宽门控阈值范围的生产系统

#### 局限
- $\alpha$ 需要针对数据集调参（当前硬编码 0.6）
- 继承了关键词的弱点：口语绕圈场景下仍不如纯向量

---

### 5. MRR（Mean Reciprocal Rank）

#### 数学定义

$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$

其中 $\text{rank}_i$ 是第 $i$ 个查询中**第一个**正确回答的排名（1-indexed），未命中为 0。

#### 示例

| 查询 | 正确答案排名 | 倒数排名贡献 |
|------|-------------|-------------|
| Q1：正确答案在 Top-1 | rank=1 | 1/1 = 1.0 |
| Q2：正确答案在 Top-3 | rank=3 | 1/3 = 0.333 |
| Q3：正确答案在 Top-2 | rank=2 | 1/2 = 0.5 |
| Q4：未命中 | rank=0 | 0 |

MRR = (1.0 + 0.333 + 0.5 + 0) / 4 = 0.458

#### 性质
- **范围**：$[0, 1]$，1 = 全部查询正确答案都在 Top-1
- **尺度无关**：只看排名不看分数 → A/B/C/D/E 五路可直接比较
- **关注单点**：只关心「第一个正确答案在哪」

#### 解读
- MRR = 0.8：平均正确答案大约在第 1.25 位
- MRR = 0.5：平均正确答案大约在第 2 位
- MRR < 0.5：超过一半的正确答案不在 Top-2

---

### 6. NDCG@k（Normalized Discounted Cumulative Gain）

#### 数学定义

$$\text{DCG@k} = \sum_{i=1}^{k} \frac{\text{rel}_i}{\log_2(i + 1)}, \quad \text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}$$

其中 $\text{rel}_i$ 为排名第 $i$ 位的相关性（二元：命中=1，未命中=0），$\text{IDCG@k}$ 为理想排序下的 DCG。

#### 二元相关性的 NDCG

每个查询只有一份正确文档时：

$$\text{NDCG@k} = \begin{cases} \frac{1}{\log_2(\text{rank} + 1)} & \text{答案排名 rank} \leq k \\ 0 & \text{答案不在 Top-k} \end{cases}$$

| 正确答案排名 | NDCG@1 | NDCG@3 | NDCG@5 |
|-------------|--------|--------|--------|
| 1 | 1.000 | 1.000 | 1.000 |
| 2 | 0 | 0.631 | 0.631 |
| 3 | 0 | 0.500 | 0.500 |
| 4 | 0 | 0 | 0.431 |
| 5 | 0 | 0 | 0.387 |

#### 性质
- **范围**：$[0, 1]$，1 = 完美排序
- **尺度无关**：只看排名
- **位置敏感**：排第 1 得满分，排第 k 也有分但折扣递减
- **NDCG@1 = Hit@1**：数学上等价

---

### 7. Coverage@k / Precision@k / F1@k（多意图专用）

> 当用户一句话包含多个意图时（如 "搞个聊天+看板"），以上 6 种单答案指标不够用。

#### Coverage@k（覆盖度）

$$\text{Coverage@k} = \frac{|\text{Top-}k \cap \text{answers}|}{|\text{answers}|}$$

衡量：用户的 N 个意图里，Top-K 检索覆盖了几个。100% = 全找到。

#### Precision@k（精度）

$$\text{Precision@k} = \frac{|\text{Top-}k \cap \text{answers}|}{k}$$

衡量：Top-K 返回的结果里，几成是用户真正要的。

#### F1@k

$$\text{F1@k} = \frac{2 \times \text{Coverage@k} \times \text{Precision@k}}{\text{Coverage@k} + \text{Precision@k}}$$

覆盖度与精度的调和平均，综合衡量多意图检索质量。

#### 性质
- **互补关系**：放宽 Top-K → Coverage↑ 但 Precision↓
- **单意图退化为 Hit@k**：N=1 时 Coverage@1 = Hit@1
- **Top-1 天花板**：N 意图场景下 Coverage@1 ≤ 1/N（每个正确答案只能占一个位置）

#### 实际数据（8 条多意图 case）

```
指标           B 不拆分    F 规则拆分   G LLM拆分
Coverage@1    43.8%       43.8%       43.8%
Coverage@3    100.0%      100.0%      100.0%
Precision@3   66.7%       66.7%       66.7%
F1@3          0.800       0.800       0.800
```

- **Coverage@1 永远 ≤50%**（2 个意图只能排 1 个在 Top-1）
- **Top-3 全覆盖**但 Precision 降到 67%（引入 33% 噪音）
- **打破 Top-1 天花板**需要语义拆分（F/G 路）

---

## 指标选用指南

```
评测目标                          推荐指标          备注
───────────────────────────────────────────────────────────
"检索结果准不准？"                 MRR               行业通用，一条数说清
"排第一的对了没有？"               NDCG@1            = hit1 率
"前三里有正确答案吗？"             NDCG@3            比 hit3 更精细（区分排位）
"系统敢不敢直接给用户？"           margin            配合阈值做门控
"A/B/C/D/E 五路谁更好？"          MRR + NDCG        排名指标跨方案可比
"多意图覆盖了几个？"               Coverage@3        用户意图命中率
"多意图检索质量？"                 F1@3              Coverage 与 Precision 的调和
"拆分方案有没有用？"               Coverage@1        能否打破 1/N 天花板
```

**核心原则**：跨方案对比用排名指标（MRR/NDCG），同方案内评估置信度用 margin，多意图评估用 Coverage@k + F1@k。
