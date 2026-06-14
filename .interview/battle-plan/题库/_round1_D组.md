# Round 1 · D 组 — 模型内部基础（不露怯，能扯两句即可）

> 策略：2-3 层展开，展示对基础原理的理解，不强套项目经验。
> 每个母题控制在 150–250 字。

---

## M28 · Transformer 架构

**Kernel**：Encoder(双向理解)+Decoder(单向生成)。GPT 选 Decoder-only 因为自回归生成天然适合语言建模。

**展开**：

### Layer 1 — 为什么 / 背景
在 Transformer 之前，RNN/LSTM 是序列建模主流，但致命伤是**串行计算**（第 n 步必须等前 n-1 步跑完），训练无法并行；长序列时梯度消失/爆炸让远距离依赖抓不住。Transformer 用 Self-Attention 一次性算所有 token 之间的关系，把序列建模从 O(n) 步串行变成 O(1) 步并行。

### Layer 2 — 怎么做 / 机制
每个 token 的输入 → Self-Attention(看整句所有 token 的关系) → FFN(逐位置非线性变换) → 残差连接 + LayerNorm → 输出。BERT 系用双向 Encoder 做理解任务；GPT 系只用 Decoder，去掉 Cross-Attention，纯自回归预测下一个 token。训练时用 Masked Self-Attention(上三角 mask 为负无穷，防偷看未来)。

### Layer 3 — 坑 / 边界 / 追问预判
**为什么 Decoder-only 一统天下？** ①训练效率：所有 token 统一因果注意力，一次前向并行训全句（teacher forcing）；Encoder-Decoder 需要 Encoder 先跑完。②扩展性更好：架构更简洁。③预训练和推理范式统一（都是「预测下一个 token」），无需切换。代价是纯 Decoder 做理解任务不如双向 Encoder。

**项目印证**：OpsPilot 调用的 LLM（OpenAI/MiniMax/DeepSeek）皆为 Decoder-only 架构。未直接修改 Transformer，但理解该架构有助于 debug——比如「为什么提示词要放开头」（token 只能 attend 前面的）、「为什么长上下文烧钱」（KV-Cache 随长度线性增长）

> 📎 素材：深度学习.md
> 🏷️ 覆盖题号：Transformer 架构基础题

---

## M29 · Self-Attention 机制

**Kernel**：每个 token 生成 Q(我查什么)、K(我的标签)、V(我的内容)。注意力权重 = softmax(Q·Kᵀ/√dₖ)，加权求和 V 得到上下文表示。√dₖ 防点积过大导致梯度饱和。

**展开**：

### Layer 1 — 为什么 / 背景
CNN 看局部窗口，RNN 逐步传递信息——用户问「苹果股价多少」，CNN/RNN 很难一步到位把「苹果」和「股价」直接关联。Self-Attention 让每个 token **直接和所有 token 算一遍关联度**，一步完成全局信息聚合，不再依赖邻近 token 逐跳传递。

### Layer 2 — 怎么做 / 机制（五步走，这是核心，多写两句）
**① QKV 生成**：输入 X 通过 Wq、Wk、Wv 三个线性变换得到 Q/K/V，每个 token 都有自己的一套。
**② 算分数**：Score = Q·Kᵀ，得到 N×N 矩阵，Score[i][j] = token i 和 token j 的关联度。
**③ 缩放 √dₖ**：Q 和 K 的每个维度独立，点积方差正比于 dₖ。不缩放的后果：点积值很大 → softmax 输出接近 one-hot（极端分布）→ 梯度接近 0 → **训不动**。除以 √dₖ 把方差拉回 1，保持 softmax 在温和区域。
**④ softmax 归一化**：Weight = softmax(Score/√dₖ)，每行和为 1，表示「关注度分布」。
**⑤ 加权求和**：Output = Weight × V，每个 token 的输出 = 所有 token 的 V 的加权和，注意力权重决定谁影响谁。

**⑥ 多头**：把 d_model 切成 h 份（如 768→12×64），每份独立做一遍上述过程，最后拼接。不同头自然捕捉不同子空间（有的头负责语法关系，有的负责语义相关，有的看位置）。

### Layer 3 — 坑 / 边界 / 追问预判
复杂度 O(n²)：序列 4096，attention 矩阵 = 4096² ≈ 16M，显存爆炸 → FlashAttention 分块+IO 优化解决。Masked Self-Attention 训练时注意上三角 mask 正确（设为负无穷），否则信息泄露。头数不是越多越好，8-16 头是常见平衡。

**项目印证**：理解 QKV 有助于理解 LLM 行为。比如 prompt 中间的关键指令容易被忽略——原因：中间 token 的注意力被前后大量 token 稀释，首尾位置的注意力分布通常更高 → 「重要信息放开头或结尾」。

> 📎 素材：深度学习.md
> 🏷️ 覆盖题号：Self-Attention/QKV 相关题

---

## M30 · LayerNorm vs RMSNorm

**Kernel**：LayerNorm = 减均值除标准差 + 仿射变换 γ/β。RMSNorm = 只除 RMS，省均值计算 + 一个参数 β，同效果下更快更省显存。LLaMA 系主力。

**展开**：

### Layer 1 — 为什么不用 BatchNorm
BatchNorm 在 batch 维度做归一化，依赖 batch 内其他样本统计量 → 对小 batch 和**变长序列**不稳定。Transformer 处理变长句子，batch 内各句长度不一，BatchNorm 的统计量不可靠。LayerNorm 在**单样本特征维度**归一化，不依赖 batch size，天然适合 NLP 变长输入。

### Layer 2 — 怎么做 / 机制
**LayerNorm**：对每个 token 的 d 维向量 x → 算 μ = mean(x)、σ² = variance(x) → 归一化 ŷ = (x - μ) / √(σ² + ε) → 仿射 y = γ·ŷ + β。γ(scale) 和 β(shift) 是可学习参数，恢复归一化后网络的表达能力。
**RMSNorm**：只算 RMS = √(mean(x²))，归一化 y = x/RMS · γ。省了均值计算（少一次规约）和一个参数 β。LLaMA 在千亿参数量级实测：去掉均值**数值几乎无损**，但计算量和显存都更省——积少成多。

### Layer 3 — 坑 / 边界 / 追问预判
归一化放哪里也讲究：原始 Transformer 是 Post-LN（子层输出之后归一化，梯度路径长，深层难训）。现在主流 Pre-LN（子层输入之前归一化），梯度更稳定。你的答案可以顺带提这一点。

**项目印证**：类比——OpsPilot 每个节点输出需做 schema 校验，保证数据格式一致，这和归一化把每层数据「拉回同一尺度」是同一种思想：防止数值/格式在多层传递中爆炸或漂移。

> 📎 素材：深度学习.md
> 🏷️ 覆盖题号：归一化相关题

---

## M31 · 位置编码

**Kernel**：Transformer 本身无位置感知 → 需注入位置信息。绝对位置(正弦/可学习) → 相对位置 → RoPE(旋转矩阵，LLaMA 主力) → ALiBi(加偏置到 attention score，外推强)。

**展开**：

### Layer 1 — 为什么
Self-Attention 是**排列等变**的——输入序列打乱，输出对应打乱但值不变。「猫追狗」和「狗追猫」对 Attention 没区别。必须注入位置信息。

### Layer 2 — 怎么做 / 机制
**绝对位置**：原始 Transformer 用正弦编码 `PE(pos,2i)=sin(pos/10000^(2i/d))`，固定不训。可学习位置编码让模型自己学 embedding，简单但泛化长度受限（训 512，推 513 就崩）。
**RoPE（旋转位置编码，当前主流）**：核心——不是把位置编码加输入上，而是**把 Q、K 按位置旋转**：qₘ=Rₘ·q，kₙ=Rₙ·k，点积后 qₘ·kₙ = q·(Rₙ₋ₘ·k)，注意力分数只依赖**相对位置**。好处：①数学优雅（旋转矩阵 = 复数乘法）；②**外推能力强**——训 2k 长度，推 4k 不崩（相对关系是连续的）；③LLaMA/Qwen/ChatGLM 全用 RoPE。
**ALiBi**：最简——直接在 attention score 上加与距离成正比的负偏置，远距扣分多。外推能力极强（训 512 推 1M），但表达力不如 RoPE。

### Layer 3 — 坑 / 边界 / 追问预判
RoPE 外推不是无限的，超长文本高频位置会失真，需 NTK-aware 插值修正。不同模型 RoPE 基频不同（LLaMA=10000, Qwen=1000000），不可混用。

**项目印证**：OpsPilot 处理长证据摘要时，若超出模型最大训练长度，RoPE 可帮助外推，但超出太多仍需 truncate 或 chunk。

> 📎 素材：深度学习.md
> 🏷️ 覆盖题号：位置编码相关题

---

## M32 · LoRA 微调

**Kernel**：冻结原模型，旁路加低秩矩阵 A×B(r≪d) 只训这小部分。效果接近全量微调，参数减 100–1000x。多任务可换 LoRA 权重。推理零延迟（可合并回原权重）。

**展开**：

### Layer 1 — 为什么
全量微调 175B GPT-3 需几百 GB 显存，预算不可行。LoRA 基于关键发现：**微调时的权重更新 ΔW 是低秩的**，可用两个小矩阵乘积近似：ΔW = A·B（A∈R^(d×r)，B∈R^(r×k)，r≪d）。如 d=4096, r=8，参数量从 4096²≈16M → 4096×8×2≈65K。

### Layer 2 — 怎么做 / 机制
① 对目标层 W（Q/K/V 投影矩阵），**冻结**不训练
② 旁路加 A(r×d) 和 B(d×r)：A 高斯初始化，**B 初始化为 0**（保证训练初期 h=Wx+0=Wx，不破坏原模型）
③ 前向：h = Wx + (α/r)·BAx，α 是缩放因子（常用 α=16, r=8）
④ 反向：只更新 A、B 的梯度
⑤ **推理合并**：W' = W + (α/r)·BA，融合后无额外计算，零延迟
⑥ **多任务切换**：每任务训一组 LoRA 矩阵，换任务换矩阵即可，base model 不动

### Layer 3 — 坑 / 边界 / 追问预判
r 不是越大越好，r=8/16 通常足够，过大过拟合。LoRA 加在哪些层有讲究：一般为 Attention 的 Q/K/V/O + FFN 的 gate/up_proj 效果最好。**base model 升级后 LoRA 权重不可直接迁移**（如 LLaMA→LLaMA2）。合并时注意 FP16 精度溢出。

**项目印证**：当前调 API，未用 LoRA。但若未来想做 SRE 领域私有化部署，LoRA 是性价比最优方案——几万条历史工单 + 几百块算力，即可让开源模型更懂运维诊断。

> 📎 素材：深度学习.md
> 🏷️ 覆盖题号：LoRA/PEFT 微调相关题
