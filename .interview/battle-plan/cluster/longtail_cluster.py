"""
长尾摸底四步法 · 实战演示
场景：AI 运维 Agent 历史工单500条，跑聚类，找长尾，校准覆盖率目标

四步：
1. 真实数据采样（这里用生成数据模拟，真实场景换成从 DB 随机采样）
2. Case 聚类分析（TF-IDF 向量化 + KMeans）
3. 长尾识别（频率低但数量不少的 cluster）
4. 覆盖率目标校准
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

np.random.seed(42)

# ─────────────────────────────────────────────
# 第1步：真实数据采样（模拟500条历史工单）
# ─────────────────────────────────────────────
TEMPLATES = [
    # 高频 cluster：数量多
    ("服务重启",    ["服务无响应重启", "pod重启失败", "进程崩溃重启", "服务自动重启循环", "强制重启服务"], 120),
    ("数据库慢查",  ["数据库查询超时", "SQL慢查询告警", "索引缺失导致全表扫", "数据库连接池耗尽", "查询响应P99升高"], 100),
    ("磁盘满",      ["磁盘使用率超90%", "日志文件撑满磁盘", "磁盘IO等待升高", "存储空间告警", "磁盘写入失败"], 80),
    # 中频 cluster
    ("内存泄漏",    ["内存持续上涨未释放", "OOM Killer触发", "堆内存泄漏", "容器内存超限被杀", "GC频繁Full GC"], 60),
    ("网络抖动",    ["网络丢包率升高", "跨机房延迟抖动", "DNS解析超时", "TCP连接重置", "带宽打满"], 50),
    # 低频长尾 cluster：频率低，但真实存在，AI难覆盖
    ("证书过期",    ["SSL证书即将过期", "HTTPS握手失败证书问题", "证书链不完整", "证书吊销检查失败"], 30),
    ("时钟漂移",    ["NTP同步失败时钟偏差", "服务间时间戳不一致", "定时任务时区异常", "日志时序混乱"], 25),
    ("配置漂移",    ["配置文件被意外修改", "环境变量丢失", "feature flag配置不一致", "灰度配置回滚失败"], 20),
    ("依赖版本冲突",["依赖包版本不兼容", "第三方SDK升级引发异常", "运行时库版本冲突"], 15),
]

rows = []
for label, phrases, count in TEMPLATES:
    for i in range(count):
        text = phrases[i % len(phrases)]
        # 加点噪声词让数据更真实
        noise = np.random.choice(["告警", "线上", "生产", "P2", "紧急", ""], p=[.15,.15,.1,.1,.1,.4])
        rows.append({"text": f"{noise} {text}".strip(), "true_label": label})

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
print(f"✅ 第1步：采样完成，共 {len(df)} 条工单\n")

# ─────────────────────────────────────────────
# 第2步：Case 聚类分析
# K 怎么定：先用手肘法（inertia）扫 K=3~12，找拐点
# ─────────────────────────────────────────────
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), max_features=500)
X = normalize(vectorizer.fit_transform(df['text']))

print("📐 第2步：手肘法扫描最优 K ...")
inertias = []
K_range = range(3, 13)
for k in K_range:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X)
    inertias.append(km.inertia_)

# 找拐点：二阶差分最大的地方
diffs2 = np.diff(np.diff(inertias))
best_k = list(K_range)[np.argmax(diffs2) + 1]
print(f"   手肘法推荐 K = {best_k}（二阶差分最大点）")

# 实际我们知道9类，这里用9
K = 9
km_final = KMeans(n_clusters=K, n_init=20, random_state=42)
df['cluster'] = km_final.fit_predict(X)
print(f"   最终使用 K={K} 跑聚类\n")

# ─────────────────────────────────────────────
# 第3步：长尾识别 + 热力图
# ─────────────────────────────────────────────
# 统计每个 cluster 的大小、代表性词
cluster_stats = []
for cid in range(K):
    mask = df['cluster'] == cid
    size = mask.sum()
    # 找这个 cluster 最有代表性的几条文本
    sample_texts = df[mask]['text'].head(3).tolist()
    # 主要真实标签（用于验证聚类质量）
    top_label = df[mask]['true_label'].value_counts().index[0]
    cluster_stats.append({
        'cluster_id': cid,
        'size': size,
        'pct': round(size / len(df) * 100, 1),
        'top_true_label': top_label,
        'sample': ' / '.join(sample_texts[:2]),
    })

stats_df = pd.DataFrame(cluster_stats).sort_values('size', ascending=False)

TOTAL = len(df)
# 定义长尾：占比 < 8%（即绝对数 < 40条）
LONGTAIL_THRESHOLD = 8.0

print("📊 第3步：Cluster 热力图（按频率排序）\n")
print(f"{'ID':>4} {'数量':>6} {'占比':>6}  {'类型':>8}  {'代表文本'}")
print("-" * 80)
for _, row in stats_df.iterrows():
    tag = "🔴 长尾" if row['pct'] < LONGTAIL_THRESHOLD else "🟢 主干"
    print(f"  {int(row['cluster_id']):>2}  {int(row['size']):>5}  {row['pct']:>5}%  {tag}  {row['sample'][:50]}")

longtail = stats_df[stats_df['pct'] < LONGTAIL_THRESHOLD]
mainstream = stats_df[stats_df['pct'] >= LONGTAIL_THRESHOLD]
longtail_total = longtail['size'].sum()
mainstream_total = mainstream['size'].sum()

print(f"\n   主干 cluster: {len(mainstream)} 个，覆盖 {mainstream_total} 条（{round(mainstream_total/TOTAL*100,1)}%）")
print(f"   长尾 cluster: {len(longtail)} 个，覆盖 {longtail_total} 条（{round(longtail_total/TOTAL*100,1)}%）\n")

# ─────────────────────────────────────────────
# 第4步：覆盖率目标校准
# ─────────────────────────────────────────────
print("🎯 第4步：覆盖率目标校准\n")

ideal_coverage = 100.0
realistic_coverage = round(mainstream_total / TOTAL * 100, 1)

print(f"   理想覆盖率目标（拍脑袋）：{ideal_coverage}%")
print(f"   现实覆盖率目标（数据驱动）：{realistic_coverage}%")
print(f"\n   长尾占 {round(longtail_total/TOTAL*100,1)}%，建议 PRD 写明：")
print("   ┌─────────────────────────────────────────────────────┐")
for _, row in longtail.iterrows():
    print(f"   │  cluster-{int(row['cluster_id'])}（{row['top_true_label']}）: 暂不覆盖，转人工处理  │")
print("   └─────────────────────────────────────────────────────┘")

print(f"""
─────────────────────────────────────────────
结论（面试可以直接说这几句）：

  1. 500条工单跑聚类，发现 {K} 个 cluster，
     其中 {len(mainstream)} 个主干 cluster 占 {realistic_coverage}%，
     {len(longtail)} 个长尾 cluster 占 {round(longtail_total/TOTAL*100,1)}%。

  2. 长尾不是不重要，是暂不覆盖、转人工，
     把 AI 的精力集中在主干上提升准确率。

  3. 覆盖率目标从"拍脑袋100%"校准到"数据驱动{realistic_coverage}%"，
     这个数字写进 PRD，是对产品能力的诚实承诺。
─────────────────────────────────────────────
""")
