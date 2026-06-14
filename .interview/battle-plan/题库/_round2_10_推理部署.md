## 模型推理与部署（22 题）

### Q1 注意力计算优化方法 + ZeRO + Flash Attention

**核心**：Flash Attention 用分块+重算减少 HBM 读写，ZeRO 把优化器状态/梯度/参数分片到多卡消除冗余。

- FlashAttention：SRAM 分块计算 softmax（online softmax），避免完整 N² attention 矩阵写回 HBM，显存从 O(N²) 降到 O(N)；ZeRO-1 分片优化器状态，ZeRO-2 加梯度分片，ZeRO-3 再分片参数

> 🏷️ M26 | ⭐⭐ 了解

### Q2 KV-Cache 空间复杂度与优化策略

**核心**：KV-Cache 大小 = 2 × 层数 × 头数 × 头维度 × 序列长度 × batch size × dtype，O(L) 随序列长度线性增长。

- 1 token 的 KV 存储 ≈ 2 bytes，65B 模型 80 层每层约 8MB/token，1000 token 即 ~8GB；优化：MQA/GQA 减少头数、量化 KV-Cache 到 INT8、PagedAttention 分页管理消灭碎片、滑动窗口丢弃远距离 KV

> 🏷️ M26 | ⭐⭐ 了解

### Q3 Hive SQL 熟练度与大数据平台经验

**核心**：Hive SQL 将类 SQL 语句转为 MapReduce/Spark 任务，是离线数仓批处理的主力接口。

- 常用操作：分区表 + 分桶表设计、UDF/UDAF 自定义函数、`lateral view explode` 炸裂嵌套数据、窗口函数做累计统计；性能调优核心：map join 避免 shuffle、谓词下推提前过滤、ORC/Parquet + Snappy 列存压缩、分区裁剪避免全表扫描

> 🏷️ 独立 | ⭐⭐ 了解

### Q4 DeepSpeed 框架核心特性与架构

**核心**：DeepSpeed 是微软开源的分布式训练加速框架，核心是 ZeRO 三部曲 + 显存/计算联合优化。

- ZeRO-1 分片优化器状态 → 省 4× 显存；ZeRO-2 加梯度分片 → 省 8×；ZeRO-3 再加参数分片 → 显存与数据并行度线性扩展；配套 CPU Offload（把优化器状态搬到 CPU，用 PCIe 带宽换显存）、Activation Checkpointing（只存部分中间激活，反向计算时重算省显存）

> 🏷️ M26 | ⭐⭐ 了解

### Q5 Flash Attention 设计原理与 I/O 融合

**核心**：把 attention 从「先全量算完写 HBM、再从 HBM 读回 softmax」变成「SRAM 里逐块算完直接出结果」，减少 HBM 读写的 bandwith 瓶颈。

- 关键技术：① tiling——把 Q/K/V 沿序列维度切块，每次算一块 softmax；② online softmax——用 running max 修正，保证分块 softmax 结果与全量等价；③ 反向时在 SRAM 重算中间结果，不存回 HBM；实际效果：1-3× 加速 + 显存从 O(N²) 降到 O(N)

> 🏷️ M26 | ⭐⭐ 了解

### Q6 视频生成/推理中的加速方法常见问题

**核心**：视频推理瓶颈在时空计算量（帧数×每帧 token 数），加速方向为压缩时间维度 + 轻量化注意力。

- 采样策略：关键帧提取（运动检测阈值筛选）、自适应帧率（静态场景降帧率，动态场景升帧率）；帧间压缩：3D 卷积/时空注意力压缩、cross-frame token merging（相邻帧相似 token 合并）；模型轻量化：DiT 蒸馏、量化至 INT8、KV-Cache 跨帧复用

> 🏷️ 独立 | ⭐⭐ 了解

### Q7 显存不足时的优化技术

**核心**：梯度检查点 + 模型并行 + 量化是三大显存优化方向，可叠加使用。

- 梯度检查点：前向时不保存全部中间激活，反向时从最近的 checkpoint 重新计算——省显存换计算（约 20-30% 额外前向时间）；模型并行：张量并行（层内切分矩阵乘法，如 Megatron-LM）→ 通信量大，流水线并行（层间分片）→ 有 bubble，常结合使用；量化：权重 INT8/INT4 直接省 2-4× 显存，可与前两者叠加

> 🏷️ M27 | ⭐⭐ 了解

### Q8 模型优化方法（训练/推理/部署三维）

**核心**：训练侧用分布式+混合精度，推理侧用量化+KV-Cache 优化+框架加速，部署侧做模型压缩+服务化。

- 训练：混合精度（FP16/BF16 + loss scaling）、梯度累积模拟大 batch、FlashAttention 加速；推理：量化（INT8/INT4）、框架优化（vLLM/TensorRT-LLM）、投机采样用小模型预生成 draft token；部署：ONNX/TensorRT 图优化+算子融合、模型蒸馏缩小体积、多级缓存（KV-Cache 热加载/Semantic Cache）

> 🏷️ M26/M27 | ⭐⭐ 了解

### Q9 大模型推理框架对比（vLLM/TensorRT-LLM/TGI）

**核心**：vLLM 吞吐最高（PagedAttention），TensorRT-LLM 延迟最低（NVIDIA 算子极致优化），TGI 上手最快（HuggingFace 生态）。

- vLLM：PagedAttention 分页管理 KV-Cache 消除显存碎片、continuous batching 保持 GPU 满载、开源社区活跃支持模型最广；TensorRT-LLM：算子融合 + FP8/INT8 极致优化、inflight batching、NVIDIA GPU 独占；TGI：一行 Docker 起动、内置 continuous batching + 量化、对 HuggingFace 模型零代码接入

> 🏷️ M26 | ⭐⭐ 了解

### Q10 推理框架性能/易用性/扩展性对比

**核心**：vLLM 性能+扩展性最强，TensorRT-LLM 单卡性能极致但绑硬件，TGI 易用性最好。

- 性能：TensorRT-LLM > vLLM ≈ SGLang > TGI（同硬件）；易用性：TGI > vLLM > TensorRT-LLM（后者需手写模型定义+编译）；扩展性：vLLM 支持 Prefix Cache、speculative decoding、多 LoRA 热切换等高级特性；SGLang 的 RadixAttention 在复杂 prompt 场景（如 Agent 多轮）对 vLLM 有竞争力

> 🏷️ M26 | ⭐⭐ 了解

### Q11 13B 模型 INT8/INT4 量化估算与影响

**核心**：FP16 存储 ≈ 26GB，INT8 ≈ 13GB（2×），INT4 ≈ 6.5GB（4×）；推理延迟降 20-40%，吞吐涨 1.5-2×。

- 计算：13B × 2 bytes(FP16) = 26GB；INT8 每参数 1 byte = 13GB；INT4 每参数 0.5 byte = 6.5GB（group scale 额外约 5%）；延迟收益：显存带宽压力减小 + 量化算子（如 INT8 GEMM）计算更快；代价：INT4 通常精度损失 1-3%（通用文本），数学推理类可能 5%+

> 🏷️ M27 | ⭐⭐ 了解

### Q12 主流推理框架性能/易用性/硬件支持对比

**核心**：vLLM 通用性最强（支持 NVIDIA/AMD/Intel），TensorRT-LLM 仅 NVIDIA 但性能极致，llama.cpp 在消费级 CPU/GPU 上跑量化的最佳选择。

- NVIDIA GPU：TensorRT-LLM > vLLM > TGI；AMD/Intel GPU：vLLM 有官方支持；CPU 推理：llama.cpp（GGUF 量化格式，M 系列 Mac 也能跑）；Apple Silicon：MLX 框架 + llama.cpp Metal 后端；通用性选 vLLM，极致性能选 TensorRT-LLM，消费级硬件选 llama.cpp

> 🏷️ M26 | ⭐⭐ 了解

### Q13 FAISS 核心原理与索引结构

**核心**：FAISS 用粗量化+细量化两阶段做近似最近邻（ANN）搜索，牺牲微小精度换百倍速度。

- 索引结构：IVF（Inverted File）— 先 K-Means 聚类成 Voronoi 单元，查询时只搜附近几个聚类中心，减少 90%+ 距离计算；PQ（Product Quantization）— 将高维向量切成多段，每段独立聚类编码，存储从 4×d bytes 压缩到 d bytes 以内；IVF+PQ 组合（IVFPQ）：先 IVF 粗筛，再 PQ 压缩存储，万亿级向量 <= 10ms 返回

> 🏷️ 独立 | ⭐⭐ 了解

### Q14 超长上下文处理的技术手段

**核心**：三向发力——位置编码拓展（RoPE 插值/NTK-aware）、分块策略（Sliding Window/Sparse Attention）、缓存优化（KV-Cache 压缩/卸载）。

- 位置编码：NTK-aware 插值——训练时基频 10000，推理时动态放大到更高频率，让 RoPE 高频部分外推更平滑；YaRN 在 NTK 基础上加温度调节，适配超长距离衰减；分块：Sliding Window（Mistral 的 4096 窗）+ Truncation/Chunking（分块独立 encode 后拼接）；存储：StreamingLLM 保留头尾 KV 丢弃中间、KV-Cache 量化（INT8）

> 🏷️ M26 | ⭐⭐ 了解

### Q15 PyTorch 计算图与自动微分机制

**核心**：PyTorch 用动态计算图——每执行一个操作就在运行时建立边，反向按拓扑序自动求导（autograd），用完即销毁。

- 动态图优势：天然支持条件分支和可变长度输入（if x>0: path_a else: path_b 直接记录实际执行的分支），调试直观（pdb 打断点看 tensor 值）；静态图（TF 1.x）优势是编译优化更激进（图融合、内存预规划）；PyTorch 2.0 compile 模式折中——动态写、静态编译（TorchDynamo 捕获图 + Inductor 后端优化）

> 🏷️ 独立 | ⭐⭐ 了解

### Q16 MoE 在增强 Agent 能力中的应用

**核心**：MoE 将单一大模型拆为多个专家子网 + 路由器，天然适合 Agent 的模块化决策——不同子任务激活不同专家。

- 任务路由：Router 根据输入语义动态选择 Top-K 专家（类似 Agent 根据 intent 选 tool）；多技能调度：不同专家预训练不同领域能力（代码/数学/推理），Agent 调用时隐式路由不再需要手工 dispatch；挑战：负载不均衡（热门专家过载/冷门专家退化）、专家间知识割裂、推理时所有专家权重仍在显存（MoE 省计算不省显存）

> 🏷️ 独立 | ⭐⭐ 了解

### Q17 训练可视化：识别问题与调参

**核心**：loss 曲线看拟合态、梯度直方图看训练健康度、激活值分布看层间数值稳定性。

- 过拟合：train loss 持续降而 val loss 反弹→ 增大正则化（weight decay/L2）+ dropout + early stop，或加数据增强；梯度消失：深层梯度接近 0 → 换激活函数（Sigmoid→ReLU/GeLU）+ residual connection 或调高学习率 warmup；梯度爆炸：loss 变 NaN → 减小学习率 + gradient clipping；激活值分布过大或饱和 → 检查 LayerNorm 位置，考虑 Pre-LN

> 🏷️ 独立 | ⭐⭐ 了解

### Q18 为何不选更大模型做数据质量分层

**核心**：大模型对数据分层任务边际收益低——区分「高质量/中等/低质量」是粗粒度判断，7B 与 70B 准确率差 2-3%，但成本差 10×。

- 成本：70B 推理延迟 5-10× 于 7B，API 价格 10-20×，处理百万级数据时绝对成本不可忽略；效率：分层任务本质是分类/打分，非深度推理，小模型+few-shot 已足够；边际收益递减：增大模型带来的 2% 分层精度提升，对下游训练收益微乎其微——下游模型本身有容错能力

> 🏷️ 独立 | ⭐⭐ 了解

### Q19 视频切帧优化方法

**核心**：在「不丢关键信息」和「不重复冗余帧」间取平衡——用场景检测自适应抽取而非固定间隔采样。

- 关键帧提取：基于帧间差（pixel-wise/HOG/SSIM）设定阈值，超过说明场景切换 → 保留该帧；运动检测：光流法/帧差法识别运动区域，运动剧烈区域提高采样率，静态背景降低；自适应采样：两阶段——先用大步长粗扫定位变化区间，再细粒度抽帧；工程优化：GPU 解码（NVDEC）+ 多线程并行处理多视频段

> 🏷️ 独立 | ⭐⭐ 了解

### Q20 大模型系统工程化核心目标

**核心**：可靠性（SLA 99.9%+ 不掉链子）、可扩展性（弹性伸缩应对流量峰谷）、延迟优化（TTFT/TPOT 可控）、成本控制（GPU 利用率最大化）。

- 可靠性：多副本部署 + 健康检查 + 自动故障切换，fallback 链（主模型→备用模型→规则兜底）；可扩展：根据 latency/GPU utilization/QPS 指标自动 HPA 伸缩，模型热加载无停机升级；延迟：prefix cache 复用、speculative decoding 加速首 token、流式输出降低感知延迟；成本：spot instance 弹性补充、GPU 分时复用、模型量化减小单卡开销

> 🏷️ 独立 | ⭐⭐ 了解

### Q21 VecEnv 向量化环境工作原理

**核心**：VecEnv 串联 N 个独立环境并行 step，将单线程序列交互变成批量并行执行，消除环境交互的串行瓶颈。

- 原理：N 个环境各维护独立状态，每步用 list comprehension 或 multiprocessing 并行执行 N 个 `env.step(action)` → 返回 batch observations/rewards/dones → 训练时一次前向处理 batch；实现：`SubprocVecEnv`(multiprocessing) 利用多核并行，`DummyVecEnv`(单进程顺序) 适合调试；收益：N 子进程时环境交互吞吐 ≈ N× 单环境，适合 on-policy 算法（PPO/A2C）的 rollout 加速

> 🏷️ 独立 | ⭐⭐ 了解

### Q22 LoRA vs 全量微调的训练时间开销

**核心**：LoRA 训练时间通常与全量微调接近或稍快，不会更慢——计算大头在 forward/backward 的激活计算，权重更新的代价占比很小。

- 前向：LoRA 多一次 BAx 小矩阵乘法（d×r + r×d），计算量可忽略（r=8 时仅占原 Wx 的 0.2%）；反向：LoRA 只计算 A/B 梯度，不更新冻结的 W——但反向仍需算完整个链路的激活梯度（这部分开销与全量一致）；优化器更新：LoRA 只更新 A/B（参数量＜原模型 1%），省去 optimizer state 的读写开销；实际 wall time：LoRA 单步快 5-10%，但收敛可能需稍多 epoch → 总耗时相当

> 🏷️ M32 | ⭐⭐ 了解
