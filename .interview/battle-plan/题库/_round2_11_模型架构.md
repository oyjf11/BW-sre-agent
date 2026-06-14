# Round 2 · 模型架构基础（46 题）答案

## 模型架构基础（46 题）

### Q1 手动实现 LayerNorm 前向传播（NumPy）

**核心**：对每个 token 的 d 维向量 x 做减均值除标准差 + 仿射变换。

- μ = mean(x), σ² = var(x) → ŷ = (x - μ) / √(σ² + ε)，输出 y = γ·ŷ + β
- ε 防除零；γ/β 可学习参数恢复表达能力；数值稳定：用 np.sqrt(np.max(var, 0))

> 🏷️ M30 | ⭐

### Q2 手动实现多头注意力（QKV/缩放点积/拼接/投影）

**核心**：将 d_model 切 h 份，每头独立做 Attention(QKᵀ/√dₖ)V，拼接后投影。

- 维度变化：(b,n,d) → Q/K/V 各 (b,h,n,dₖ) → Score(n×n) → softmax → 加权 V → concat(b,n,d) → Wo 投影
- √dₖ 缩放防点积过大致梯度饱和；多头捕获不同子空间语义

> 🏷️ M29 | ⭐

### Q3 BERT+CRF 在 NER 中的工作原理

**核心**：BERT 提取上下文 token 向量，CRF 对标签序列建模转移约束。

- BERT 输出发射分数（token→label），CRF 学习 label 间转移概率（B-PER→I-PER 高分，I-PER→B-LOC 低分）
- 联合训练端到端；优势：CRF 约束标签拓扑，避免 B-PER 后接 I-LOC 这种非法序列

> 🏷️ M28 | ⭐

### Q4 Decoder-only 架构合理性（GPT 系）

**核心**：自回归预测 next token，训练推理范式统一，因果注意力可全句并行训练。

- 训练效率：一次前向 teacher forcing 并行训全句，Encoder-Decoder 需 encoder 先跑完
- 推理简洁：去掉 cross-attention，仅 Masked Self-Attn；代价是理解任务不如双向 Encoder

> 🏷️ M28 | ⭐

### Q5 GPT vs BERT 系统对比

**核心**：GPT=Decoder-only 单向生成，BERT=Encoder-only 双向理解。

| 维度 | GPT | BERT |
|------|-----|------|
| 架构 | Decoder-only | Encoder-only |
| 目标 | 预测 next token | MLM 完形填空 |
| 场景 | 生成、对话、补全 | 分类、NER、QA |
| 注意力 | 因果 mask 单向 | 双向 attention |

> 🏷️ M28 | ⭐

### Q6 MLA 原理 + KV Cache 作用

**核心**：MLA 将 KV 映射到低维 latent 再升维回多头，减少 KV Cache 显存；KV Cache 缓存已生成 token 的 K/V 避免重复计算。

- MLA：KV 从 d→latent_dim(≪d) 投影，推理时只存 latent 侧 + 上投影矩阵，显存显著下降
- KV Cache 代价 O(n²)，MLA 将每 token 存储从 2·d·h 降到 ≈2·latent_dim，长序列收益巨大

> 🏷️ M29（扩展）| ⭐

### Q7 常见标准化方法对比（LayerNorm vs RMSNorm vs BatchNorm vs GroupNorm）

**核心**：LayerNorm 特征维归一化不依赖 batch；RMSNorm 省均值计算更省显存。

- BN 跨 batch 归一化，小 batch/变长序列统计量不可靠 → 不适合 NLP
- LN：ŷ = (x-μ)/σ·γ+β；RMSNorm：ŷ = x/RMS·γ，省 μ + β 参数，LLaMA 验证数值近乎无损

> 🏷️ M30 | ⭐

### Q8 多头注意力底层实现细节

**核心**：QKV 线性变换 → 按头切分 → 独立缩放点积 → 拼接 → 输出投影。

- 内存布局：转置为 (b, h, n, dₖ) 使各头在同一 batch 连续，便于 GPU 并行
- 位置编码可加在 QK 上（RoPE 旋转）或加在输入嵌入层后；多头优于单头：不同头学不同子空间关系

> 🏷️ M29 | ⭐

### Q9 位置编码方法总览

**核心**：四种主流：绝对正弦/可学习 → 相对位置 → RoPE → ALiBi，演化方向是提升外推能力。

- 绝对正弦 PE 固定不训但长度不可外推；可学习 embedding 泛化受限
- RoPE 旋转 Q/K 使注意力仅依赖相对距离，外推好，LLaMA/Qwen 主力；ALiBi 最简加偏置，外推极强

> 🏷️ M31 | ⭐

### Q10 DDPM 随机时间步训练原理

**核心**：随机采样 t 让每个 batch 见不同噪声强度，模型同时学会各种噪声水平的去噪。

- 固定先加满再逐步 ①样本多样性差（只见过中间态分布）②训练不充分（早期 t 见过，后期 t 忘掉）
- 随机 t 等效随机噪声水平数据增强，训练稳定且覆盖完整噪声分布，生成质量更高

> 🏷️ 扩展 | ⭐

### Q11 大模型面临的主要挑战

**核心**：计算成本、推理延迟、幻觉、上下文长度是四大瓶颈。

- 训练千亿参数需千卡 GPU 数十天；推理 KV Cache 随长度线性膨胀
- 幻觉根因：最大似然目标不保证事实正确；长上下文：注意力 O(n²) 显存瓶颈，需 FlashAttention/稀疏注意力

> 🏷️ M28（扩展）| ⭐

### Q12 LayerNorm vs BatchNorm（为何选 LN）

**核心**：BN 跨 batch 依赖大 batch 统计量，LN 在特征维归一化与 batch 无关。

- NLP 变长序列各句长度不一，BN 统计量不可靠；LN 单样本归一化稳定
- LN 不依赖 batch size，训练推理一致，天然适合序列模型

> 🏷️ M30 | ⭐

### Q13 位置编码的作用与重要性

**核心**：Self-Attention 排列等变，不加位置则「猫追狗」和「狗追猫」无区别。

- 注入 token 顺序信息使模型感知序列结构；缺少位置编码，Attention 退化为词袋模型
- 绝对位置给坐标，相对位置给距离，RoPE 给旋转角——本质都是让模型知道谁在前谁在后

> 🏷️ M31 | ⭐

### Q14 LayerNorm vs RMSNorm 主要区别

**核心**：LN 减均值+除标准差+γ+β；RMSNorm 只除 RMS+γ，省均值运算和 β 参数。

- 计算效率：RMSNorm 少一次 reduce（均值），→10% 加速，显存省 β(≈d 个 float)
- LLaMA 系全部采用 RMSNorm：千亿量级数值逼近无损，边际收益巨大

> 🏷️ M30 | ⭐

### Q15 为何选 LayerNorm 而非 BatchNorm（重复变体）

**核心**：同 Q12。BN 依赖 batch 统计，LN 单样本独立。

- 变长序列 + 小 batch 下 BN 不稳定；LN 特征维归一化 batch 无关
- Transformer 训练推理一致，LN 天然适配

> 🏷️ M30 | ⭐

### Q16 DDPM 随机时间步原理（重复变体）

**核心**：同 Q10。随机 t 让模型学会全局噪声水平的去噪映射。

- 从高效训练视角：随机采样 t 每步都在学有用信号，不浪费计算
- 从分布覆盖视角：使模型见过完整噪声谱，推理时 DDPM 逐步去噪才有平滑过渡

> 🏷️ 扩展 | ⭐

### Q17 LayerNorm vs RMSNorm 差异 + LLaMA 倾向

**核心**：同 Q14。RMSNorm 省均值计算和 β，LLaMA 千亿量级验证高效等价。

- 数学：LN(y)=γ·(x-μ)/σ+β；RMSNorm(y)=γ·x/RMS
- 推理侧 LN 仍要做均值和方差，RMSNorm 快一截，对自回归解码累积收益显著

> 🏷️ M30 | ⭐

### Q18 归一化层为何引入 + 位置

**核心**：稳定数值分布、缓解梯度爆炸/消失，加速收敛。

- 机制：将每层输出拉回零均值单位方差，避免多层累积导致数值漂移
- Transformer 位置：原始 Post-LN（子层后），现主流 Pre-LN（子层前归一化），梯度更稳定

> 🏷️ M30 | ⭐

### Q19 常见神经网络结构

**核心**：CNN（空间局部）、RNN/LSTM（序列递推）、Transformer（全局并行注意力）。

- CNN 适用于图像/时间序列；RNN 适用于时序预测；Transformer 统治 NLP + 多模态
- GNN 用于图结构；扩散模型/VAE 用于生成

> 🏷️ 扩展 | ⭐

### Q20 逻辑回归基本原理

**核心**：线性模型 + sigmoid 将输出映射到 (0,1) 作为概率。

- P(y=1|x) = 1/(1+e^(-wx-b))，决策边界 = wx+b=0（线性超平面）
- 损失用交叉熵；概率解释清晰，可输出置信度

> 🏷️ 扩展 | ⭐

### Q21 主流图像/内容生成模型

**核心**：扩散模型（StableDiffusion/DDPM/DALL·E）、GAN、VAE/VQ-VAE、Flow Matching。

- GAN 对抗训练生成快但不稳定；VAE 隐变量采样多样性强但模糊
- 扩散模型逐步去噪质量最高，Flow Matching 用连续流替代离散去噪步骤，生成速度更快

> 🏷️ 扩展 | ⭐

### Q22 参数规模对模型的影响

**核心**：规模增大通常提升容量，但伴随优化难度上升、过拟合风险、梯度不稳定。

- 规模<→涌现能力：一定规模后出现新能力（数学推理、复杂指令跟随）
- 大参数量需要更多正则化/高质量数据；超大模型需混合精度/梯度累积/ZeRO 优化

> 🏷️ 扩展 | ⭐

### Q23 Encoder 与 Decoder 功能区别

**核心**：Encoder 双向理解源序列，Decoder 自回归生成目标序列。

- Encoder：无 mask 全可见，输出上下文表示；蕴含整句语义
- Decoder：Masked Self-Attn + Cross-Attn（取 Encoder 输出），逐 token 自回归生成
- 机器翻译：Encoder 读源语言全文 → Decoder 逐词生成目标语言

> 🏷️ M28 | ⭐

### Q24 LayerNorm 作用机制与对训练的影响

**核心**：将激活值归一化到稳定分布，梯度更平滑，加速收敛。

- 没有 LN：深层网络值域偏移，梯度消失或爆炸；LN 后每层输入保持正态化
- 对收敛：减少内部协变量偏移（ICS），允许更大的学习率

> 🏷️ M30 | ⭐

### Q25 MoE 提升 Agent 能力

**核心**：MoE 用门控网络将输入路由到不同专家，实现任务专业化，稀疏激活降低计算。

- 计算效率：每 token 仅激活 top-k 专家（如 8 个中 2 个），参数量大但 FLOPs 不涨
- Agent 场景：不同专家分管代码/数学/推理，router 动态调度，类似团队分工

> 🏷️ M28（扩展）| ⭐

### Q26 VQ-VAE 基本原理与结构

**核心**：编码器连续隐变量 → 离散化查码本 → 解码器重建，实现离散隐空间表示。

- 编码器：x → zₑ(x)（连续）；向量量化：将 zₑ 替换为码本 E 中最近邻 eₖ
- 损失：重建损失 + ∥sg[zₑ]-e∥² + β∥zₑ-sg[e]∥²（commitment loss）
- 优势：离散表示更适合语言/图像 tokenization；挑战：码本坍塌（部分 code 不更新）

> 🏷️ 扩展 | ⭐

### Q27 LayerNorm vs RMSNorm 差异 + 工业实践（重复变体）

**核心**：LN=减均值+除标准差+γ+β；RMSNorm=RMS+γ，LLaMA 系主力。

- 数值稳定性：RMSNorm 不计算均值，对异常值容忍性更好
- 内存：省 β 参数（d 个），千亿模型 d=8192→省 32KB/层，但层数多累积客观

> 🏷️ M30 | ⭐

### Q28 判别式转生成式的方法

**核心**：统一用生成式框架重构传统分类/匹配任务。

- 格式化输出：输出标签字符串（"positive"）而非 softmax 类别 ID
- 思维链：分类前先推理再作答；指令重构：将匹配转为"A 是否符合 B"的 yes/no 生成
- 优势：统一训练范式，可利用预训练的文本理解能力，few-shot 效果好

> 🏷️ 扩展 | ⭐

### Q29 LayerNorm vs BatchNorm（重复变体）

**核心**：同 Q12/Q15。LN 特征维归一化，BN 批维归一化。

- 序列建模中 batch 内 token 数不一，BN 统计量嘈杂；LN 独立归一化稳定
- Pre-LN 梯度传播更直接，深层模型训练不崩

> 🏷️ M30 | ⭐

### Q30 归一化方法系统对比

**核心**：LN/RMSNorm/BN/GN 四种常见归一化维度不同。

- BN(batch维)：CV主流，依赖大batch；LN(feature维)：NLP主流，序列友好
- RMSNorm(feature RMS)：LN精简版，LLaMA主力；GN(group维)：小batch图像BN替代
- 位置：原始Transformer Post-LN → 现主流 Pre-LN，梯度更短

> 🏷️ M30 | ⭐

### Q31 VQ-VAE 结构与码本机制（重复变体）

**核心**：同 Q26。核心：连续→离散→重建，码本 E∈R^(K×d)，查最近邻离散化。

- 关键：straight-through estimator 梯度传递（前向离散，反向直通编码器）
- 应用：DALL·E 用 VQ-VAE 将图像 tokenize 成离散序列再训自回归模型

> 🏷️ 扩展 | ⭐

### Q32 判别式转生成式方法（重复变体）

**核心**：同 Q28。统一范式：分类→文本生成。

- 典型：T5「text-to-text」框架，所有任务统一为 seq2seq；GPT-3 用 prompt 将分类/匹配转为补全
- 性能：生成式在 few-shot 场景优于判别式微调，但 zero-shot 分类精度仍有差距

> 🏷️ 扩展 | ⭐

### Q33 Encoder vs Decoder 结构与应用场景

**核心**：同 Q23。Encoder 双向编码，Decoder 单向生成。

- 结构：Encoder 全 Attention 可视→多层堆叠→输出上下文；Decoder 加入 Cross-Attn 接收 Encoder 输出
- 机器翻译：Encoder 用双向信息理解完整原文，Decoder 逐词生成时参考原文

> 🏷️ M28 | ⭐

### Q34 LayerNorm 作用机制与梯度缓解

**核心**：同 Q24。归一化拉回稳定分布，梯度更平滑。

- 无 LN：残差累加使数值量级膨胀 → softmax 饱和区 → 梯度≈0
- LN 将每子层输出重新正态化，避免激活和梯度量级发散

> 🏷️ M30 | ⭐

### Q35 Few-shot 推理为何提升表现

**核心**：In-Context Learning——模型从示范中捕捉任务模式，不更新参数。

- 预训练目标含大量 pattern 匹配任务，few-shot 激活了这一能力
- 示例提供分布线索：格式、答案范围、语义；本质是模型在 inference-time「条件化」

> 🏷️ 扩展 | ⭐

### Q36 自回归生成 token 选择机制

**核心**：使用采样/贪心选出的 token ID（离散），而非 softmax 概率分布（连续）。

- 理由：Decoder 训练时的输入是 ground truth token embedding，不是上一时刻的概率分布
- 训练-推理一致性：都用离散 token；如果用分布 → 训练信号是离散但推理用分布 → mismatch
- 例外：scheduled sampling 尝试混合 teacher forcing 和 self-generated token

> 🏷️ M28（扩展）| ⭐

### Q37 FFN 隐藏层维度扩展

**核心**：通常扩展 4x（d_ff = 4 × d_model），设计动机是给非线性变换足够容量。

- 理论：Transformer FFN 是两层 MLP（升维+ReLU/GELU+降维），升维让中间表示有足够空间
- 实验：4x 经验最优，过小限制表达能力，过大参数量爆炸
- 变体：LLaMA 用 SwiGLU 激活，取 8/3 × d_model 保持等量 FLOPs

> 🏷️ M28（扩展）| ⭐

### Q38 近期阅读的大模型论文

**核心**：建议准备 1-2 篇阅读过的论文，能说出核心思路和创新点。

- 示例：FlashAttention——分块+IO 感知，将注意力从显存瓶颈转为计算瓶颈
- 示例：LLaMA 系列——小模型+多数据，证明数据质量 > 模型规模；有准备的回答更显专业

> 🏷️ 扩展 | ⭐

### Q39 模型缺陷及解决方法

**核心**：幻觉→RAG/约束解码；不一致→temperature=0+重复惩罚；延迟→量化/投机解码。

- 幻觉：RAG 检索外挂知识库、约束解码限制输出空间、RLHF 对齐真实偏好
- 延迟：KV Cache + 量化 INT8/INT4 + 投机解码（小模型起草+大模型校验）

> 🏷️ 扩展 | ⭐

### Q40 VQ-VAE 与传统 VAE 的区别（重复变体）

**核心**：VAE 用连续高斯隐变量；VQ-VAE 用离散码本隐变量。

- VAE：p(z|x) 输出 μ,σ → 重参数采样 z（连续），重建 + KL 散度
- VQ-VAE：编码器连续 → 查码本离散化 → 解码重建；无 KL，用 codebook/commitment loss
- 优势：离散表示天然适合语言/图像 tokenization，自回归模型可建模离散 token 序列

> 🏷️ 扩展 | ⭐

### Q41 Self-Attention 机制（Q/K/V）

**核心**：Query 查信息，Key 提供标签，Value 提供内容；QK 点积得权重，softmax 后加权 V。

- Score = softmax(QKᵀ/√dₖ)：除以 √dₖ 防点积值过大导致 softmax 梯度饱和
- 输出：每个 token = 所有 token V 的加权和，高注意力权重的 token 贡献大

> 🏷️ M29 | ⭐

### Q42 LayerNorm vs RMSNorm 工业实践（重复变体）

**核心**：同 Q14/Q17/Q27。RMSNorm 更省算力/显存，LLaMA 全系使用。

- 性能差异：RMSNorm 在千亿级模型上效果接近 LN，但训练/推理更快
- 推理：自回归解码每步都要过 LN，RMSNorm 累积省时显著

> 🏷️ M30 | ⭐

### Q43 Transformer 整体架构

**核心**：Encoder-Decoder 结构，每层含 Self-Attn + FFN + 残差连接 + 归一化。

- Encoder：N 层，每层 Self-Attn(全可见) + FFN + 两层残差 LN
- Decoder：N 层，每层 Masked Self-Attn + Cross-Attn(取 Encoder 输出) + FFN
- 位置编码注入顺序信息；输出 softmax 得词表概率分布

> 🏷️ M28 | ⭐

### Q44 VQ-VAE 离散表示学习（重复变体）

**核心**：同 Q26/Q31。离散表示使数据可 tokenize 后用自回归模型建模。

- 编码器 x→zₑ(连续) → 量化 q(z)=eₖ → 解码器重建
- 离散瓶颈迫使学习有意义的 structured representation；DALL·E/VQGAN 的 foundation

> 🏷️ 扩展 | ⭐

### Q45 DDPM vs Flow Matching 对比

**核心**：DDPM 逐步加噪→逐步去噪（随机微分方程离散化）；Flow Matching 学连续速度场直接在数据-噪声间插值。

- DDPM：p(xₜ|x₀) 高斯→多步马尔可夫链；生成慢（1000 步），质量高
- Flow Matching：dx/dt = vᵩ(x,t)，ODE 路径直线插值，采样步数可大幅减少（10-100 步），速度与质量的平衡更好
- 数学：DDPM 模拟扩散 SDE 的逆向过程；FM 模拟概率流 ODE，路径更直接

> 🏷️ 扩展 | ⭐

### Q46 Flow Matching 基本原理

**核心**：不学去噪过程，而是学概率密度随时间流动的速度场，直线插值源分布到目标分布。

- 给定数据 x₀∼p₀，噪声 x₁∼p₁，构造路径 xₜ = (1-t)x₀ + tx₁，真速度 v = x₁ - x₀
- 模型 vᵩ 回归真速度；推理时用 ODE solver 沿速度场积分，从噪声推向样本
- 优势：无需离散化扩散步，路径笔直，生成效率远高于 DDPM；可用于图像/语音/分子生成

> 🏷️ 扩展 | ⭐
