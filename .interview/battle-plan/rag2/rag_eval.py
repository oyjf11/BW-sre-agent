"""
RAG 命中率测试脚本 v2(阿里通义 text-embedding-v4)
========================================================
严格按方案设计:
  1. 父子分块:父块=完整 plan+坑(不向量化),子块=场景描述(向量化)
  2. metadata:挂在子块上,parent_id + 结构化特征(领域/复杂度/多人/认证)
  3. small-to-big 检索:子块向量匹配 → 通过 parent_id 取回父块
  4. 元数据过滤:支持按 metadata 硬过滤
  5. A/B 对比:原始口语 query vs 改写后 query 的命中率

依赖:pip install dashscope numpy
环境变量:export DASHSCOPE_API_KEY=sk-xxx
"""

import os
from collections import defaultdict
from typing import Optional
import numpy as np
import dashscope
from dashscope import TextEmbedding, TextReRank
from http import HTTPStatus


from config import DASHSCOPE_API_KEY, EMBED_MODEL, EMBED_DIM, RERANK_MODEL, LLM_MODEL
from data import PARENT_DOCS, SCENE_VARIANTS, TEST_SET, STOPWORDS, TERM_MAP

MODEL = EMBED_MODEL
DIM = EMBED_DIM
dashscope.api_key = DASHSCOPE_API_KEY


def build_child_chunks(parents):
    children = []
    for p in parents:
        for idx, scene_text in enumerate(SCENE_VARIANTS[p["id"]]):
            children.append({
                "child_id": f"{p['id']}_C{idx}",
                "content": scene_text,            # 只有 content 入库
                "metadata": {
                    "parent_id": p["id"],         # ← 取回父块的钩子
                    **p["metadata"],
                },
            })
    return children


def rewrite_query(raw: str) -> str:
    r = raw
    for big_word, term in TERM_MAP.items():
        if big_word in r:
            r += " " + term
    for sw in STOPWORDS:
        r = r.replace(sw, " ")
    return " ".join(r.split())


# ============ 5. embedding(query/document 分开) ============
EMBED_BATCH_SIZE = 10


def embed(texts, text_type):
    if isinstance(texts, str):
        texts = [texts]
    embs = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        resp = TextEmbedding.call(
            model=MODEL, input=batch, dimension=DIM, text_type=text_type,
        )
        if resp.status_code != HTTPStatus.OK:
            raise RuntimeError(f"Embedding 失败: {resp.code} {resp.message}")
        embs.extend(item["embedding"] for item in resp.output["embeddings"])
    return np.array(embs, dtype=np.float32)


def cosine(a, b):
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a @ b.T


# ============ 5.5 rerank（gte-rerank 精排）============
def rerank(query: str, documents):
    """
    用 gte-rerank 对候选文档精排。
    返回 [(doc_idx, relevance_score), ...] 按相关性降序;
    失败返回 None(由调用方 fallback 回 cosine)。
    """
    if not documents:
        return []
    try:
        resp = TextReRank.call(
            model=RERANK_MODEL,
            query=query,
            documents=list(documents),
            top_n=len(documents),
            return_documents=False,
        )
    except Exception as e:  # noqa: BLE001  网络/SDK 异常都兜底
        print(f"  ⚠ rerank 调用异常,fallback 回 cosine: {e}")
        return None
    if resp.status_code != HTTPStatus.OK:
        print(f"  ⚠ rerank 失败,fallback 回 cosine: {resp.code} {resp.message}")
        return None
    results = resp.output["results"]
    return [(r["index"], float(r["relevance_score"])) for r in results]


# ============ 6. small-to-big 检索器 ============
class SmallToBigRetriever:
    def __init__(self, parents, children):
        self.parents = {p["id"]: p for p in parents}
        self.children = children
        contents = [c["content"] for c in children]
        print(f"  向量化 {len(contents)} 个子块...")
        self.child_vecs = embed(contents, text_type="document")

    def retrieve(self, query_text, top_k_parents=3, meta_filter: Optional[dict] = None,
                 use_rerank=False, recall_k=8, debug: Optional[dict] = None):
        """
        meta_filter: 如 {"multi_user": True},检索前硬过滤子块。
        use_rerank: True 时走两阶段——向量粗排 top-recall_k → gte-rerank 精排。
        recall_k:  粗排召回送精排的子块数。
        debug:     可选 dict,会写入 {"used_rerank": bool} 供调用方展示(如表里标 *)。
        返回 [(parent_id, score), ...] 按聚合分数降序。
        """
        qv = embed(query_text, text_type="query")

        # 元数据过滤(在子块层面)
        if meta_filter:
            mask = np.array([
                all(c["metadata"].get(k) == v for k, v in meta_filter.items())
                for c in self.children
            ])
            valid_idx = np.where(mask)[0]
        else:
            valid_idx = np.arange(len(self.children))

        if len(valid_idx) == 0:
            if debug is not None:
                debug["used_rerank"] = False
            return []

        sims = cosine(qv, self.child_vecs[valid_idx])[0]

        # child_score[local_i in valid_idx] -> 用于 small-to-big 聚合的分数
        scored = list(zip(valid_idx, sims.astype(float)))
        used_rerank = False

        if use_rerank:
            # 阶段一(粗排):向量取 top-recall_k 候选,缩小精排集合
            coarse = sorted(scored, key=lambda x: -x[1])[:recall_k]
            cand_idx = [int(i) for i, _ in coarse]
            cand_docs = [self.children[i]["content"] for i in cand_idx]
            # 阶段二(精排):gte-rerank 对候选打分
            rr = rerank(query_text, cand_docs)
            if rr is not None:
                # rr: [(候选内局部下标, relevance_score)],映回全局子块下标
                scored = [(cand_idx[local], score) for local, score in rr]
                used_rerank = True
            # rr is None -> fallback:沿用 cosine 的 scored,used_rerank=False

        if debug is not None:
            debug["used_rerank"] = used_rerank

        # small-to-big:按 parent_id 聚合,同父块多子块取 MAX
        parent_scores = defaultdict(float)
        for child_i, score in scored:
            pid = self.children[int(child_i)]["metadata"]["parent_id"]
            if score > parent_scores[pid]:
                parent_scores[pid] = float(score)

        return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]

    def get_parent(self, parent_id):
        return self.parents[parent_id]


# ============ 6.5 关键词检索器 ============
class KeywordRetriever:
    """纯关键词倒排索引检索:tokenize→匹配→small-to-big 聚合。"""

    def __init__(self, parents, children):
        self.parents = {p["id"]: p for p in parents}
        self.children = children
        self.inverted = defaultdict(list)  # token → [child_idx, ...]
        for idx, c in enumerate(children):
            for tok in self._tokenize(c["content"]):
                self.inverted[tok].append(idx)

    @staticmethod
    def _tokenize(text):
        import re
        tokens = set()
        # 提取中文连续段和英文/数字连续段
        segments = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', text.lower())
        for seg in segments:
            if re.match(r'^[\u4e00-\u9fff]+$', seg):
                # 中文:单字 + 二元组
                for i in range(len(seg)):
                    tokens.add(seg[i])
                    if i < len(seg) - 1:
                        tokens.add(seg[i:i + 2])
            else:
                tokens.add(seg)
        return tokens

    def retrieve(self, query_text, top_k_parents=3, meta_filter=None):
        qt = self._tokenize(query_text)
        if not qt:
            return []

        # token → IDF 权重(稀有词权重高)
        n_docs = len(self.children)
        idf = {}
        for tok in qt:
            df = len(self.inverted.get(tok, []))
            idf[tok] = math.log((n_docs + 1) / (df + 1)) + 1 if df > 0 else 0

        # 累加每个 child 的 IDF 加权命中分
        child_scores = defaultdict(float)
        for tok in qt:
            w = idf.get(tok, 0)
            if w == 0:
                continue
            for idx in self.inverted.get(tok, []):
                child_scores[idx] += w

        if not child_scores:
            return []

        # 归一化到 [0,1]:除以最大可能分数(query 所有 token IDF 和)
        max_possible = sum(idf.values())
        if max_possible > 0:
            for idx in child_scores:
                child_scores[idx] /= max_possible

        # small-to-big:按 parent_id 聚合,取 MAX
        parent_scores = defaultdict(float)
        for child_idx, score in child_scores.items():
            pid = self.children[child_idx]["metadata"]["parent_id"]
            if score > parent_scores[pid]:
                parent_scores[pid] = score

        return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]


def hybrid_retrieve(vec_retriever, kw_retriever, query_text,
                    top_k_parents=3, alpha=0.6):
    """向量 + 关键词加权融合。alpha 越高,向量权重越大。"""
    # 获取两路 child 级分数
    qv = embed(query_text, text_type="query")
    vec_sims = cosine(qv, vec_retriever.child_vecs)[0]

    qt = kw_retriever._tokenize(query_text)
    n_docs = len(kw_retriever.children)
    idf = {}
    for tok in qt:
        df = len(kw_retriever.inverted.get(tok, []))
        idf[tok] = math.log((n_docs + 1) / (df + 1)) + 1 if df > 0 else 0
    kw_raw = defaultdict(float)
    for tok in qt:
        w = idf.get(tok, 0)
        for idx in kw_retriever.inverted.get(tok, []):
            kw_raw[idx] += w
    max_kw = sum(idf.values())
    kw_scores = np.array([kw_raw.get(i, 0) / max_kw if max_kw > 0 else 0
                           for i in range(len(kw_retriever.children))],
                          dtype=np.float32)

    # 加权融合
    hybrid = alpha * vec_sims + (1 - alpha) * kw_scores

    # small-to-big 聚合
    parent_scores = defaultdict(float)
    for child_idx in range(len(vec_retriever.children)):
        score = float(hybrid[child_idx])
        pid = vec_retriever.children[child_idx]["metadata"]["parent_id"]
        if score > parent_scores[pid]:
            parent_scores[pid] = score

    return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]


# ============ 6.6 多意图拆分器 ============
import re

# 连接词：从左到右优先级递减
_SPLIT_PATTERNS = [
    # 显式多意图
    r'(?:既要|既能|可以).+?(?:也要|还能|又能)',
    r'(?:既要|既能|可以).+?(?:还要|还要能)',
    # 中等强度
    r'还要能|还要有|还要',
    r'也要能|也要',
    r'同时还要|同时也',
    r'还能|又能',
    # 弱信号
    r'同时',
    r'\+|、',
    r'带个|外加|再加上|以及',
]


def _segment_by_pattern(text, pattern):
    """按 pattern 拆分,保留分隔符两侧内容。返回片段列表。"""
    parts = re.split(f'({pattern})', text)
    # parts: [left, sep, right, sep, ...] 或 [full] if no match
    if len(parts) == 1:
        return [text]
    # 把相邻非分隔符片段合并成子句
    segments = []
    buf = ""
    for p in parts:
        if re.fullmatch(pattern, p):
            if buf.strip():
                segments.append(buf.strip())
            buf = ""
        else:
            buf += p
    if buf.strip():
        segments.append(buf.strip())
    return segments if len(segments) > 1 else [text]


def decompose_by_rules(text):
    """规则拆分:按中文连接词拆成独立子句。"""
    text = text.strip()
    # 试每个 pattern,找到就拆
    for pat in _SPLIT_PATTERNS:
        segs = _segment_by_pattern(text, pat)
        if len(segs) > 1:
            # 清理：去掉残余的"搞个""做个""能""可以"等口头禅
            cleaned = []
            for s in segs:
                s = re.sub(r'^(搞个|做个|能|可以|的|东西|系统|平台|玩意儿)\s*', '', s).strip()
                if s and len(s) >= 2:
                    cleaned.append(s)
            if len(cleaned) > 1:
                return cleaned
            # 不够 2 个有效片段,继续试下一个 pattern
    return [text]


def decompose_by_llm(text):
    """LLM 拆分:调用 qwen-plus 把多意图句子拆成独立子问题。"""
    prompt = (
        "把用户的一句话拆成独立可检索的子问题,每个子问题只包含一个意图。\n"
        "只输出子问题列表,每行一个,不要序号和解释。\n"
        "如果只有一个意图,就原样输出一行。\n"
        "如果是模糊词(如\"聊天\"),补全为完整描述。\n\n"
        f"用户输入: {text}"
    )
    try:
        import dashscope
        resp = dashscope.Generation.call(
            model=LLM_MODEL,
            prompt=prompt,
            temperature=0.0,
            max_tokens=200,
        )
        if resp.status_code == 200:
            lines = [l.strip() for l in resp.output.text.strip().split("\n")
                     if l.strip() and not l.strip().startswith("#")]
            return lines if len(lines) > 0 else [text]
        else:
            print(f"  ⚠ LLM 拆分失败({resp.code}),回退规则拆分: {resp.message}")
            return decompose_by_rules(text)
    except Exception as e:
        print(f"  ⚠ LLM 拆分异常,回退规则拆分: {e}")
        return decompose_by_rules(text)


def decomp_retrieve(vec_retriever, raw_query, top_k_parents=3):
    """拆分(规则)+检索+合并:子句各自检索 → union + max 聚合。"""
    subs = decompose_by_rules(raw_query)
    if len(subs) == 1:
        # 没拆开,直接用改写检索(等同 B 路)
        rewritten = rewrite_query(raw_query)
        return vec_retriever.retrieve(rewritten, top_k_parents=top_k_parents)

    parent_scores = defaultdict(float)
    for sub in subs:
        rewritten = rewrite_query(sub)
        for pid, score in vec_retriever.retrieve(rewritten, top_k_parents=top_k_parents):
            if score > parent_scores[pid]:
                parent_scores[pid] = score
    return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]


def decomp_retrieve_llm(vec_retriever, raw_query, top_k_parents=3):
    """同上,但用 LLM 拆分。"""
    subs = decompose_by_llm(raw_query)
    if len(subs) == 1:
        rewritten = rewrite_query(raw_query)
        return vec_retriever.retrieve(rewritten, top_k_parents=top_k_parents)

    parent_scores = defaultdict(float)
    for sub in subs:
        rewritten = rewrite_query(sub)
        for pid, score in vec_retriever.retrieve(rewritten, top_k_parents=top_k_parents):
            if score > parent_scores[pid]:
                parent_scores[pid] = score
    return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]


# ============ 7. 排序质量指标（跨方案可比,纯排名）============
import math


def mrr(cases_ranked, key="correct_rank"):
    """Mean Reciprocal Rank:1/rank 的均值,rank 越靠前越接近 1。"""
    rr_sum = 0.0
    n = 0
    for r in cases_ranked:
        rank = r.get(key, 0)
        if rank and rank > 0:
            rr_sum += 1.0 / rank
            n += 1
    return rr_sum / n if n > 0 else 0.0


def ndcg_at_k(cases_ranked, k, key="correct_rank"):
    """NDCG@k:二元相关性(命中=1,未命中=0),仅一份相关文档。"""
    total = 0.0
    n = 0
    for r in cases_ranked:
        rank = r.get(key, 0)
        if 0 < rank <= k:
            total += 1.0 / math.log2(rank + 1)
        n += 1
    return total / n if n > 0 else 0.0


# ============ 8. A/B/C/D/E 实验评测 ============
# 五路递进:A=裸向量, B=+改写, C=+rerank, D=纯关键词, E=向量+关键词Hybrid
ARMS = [
    ("A", "A 裸向量"),
    ("B", "B +改写"),
    ("C", "C +rerank"),
    ("D", "D 关键词"),
    ("E", "E Hybrid"),
]


def eval_one(ranked, answer):
    """把一路检索结果归一成可对比的指标。answer 可以是 str(单意图) 或 list(多意图)。"""
    ids = [pid for pid, _ in ranked]
    top1_pid = ids[0] if ids else "-"
    top1_score = ranked[0][1] if ranked else 0.0
    top2_score = ranked[1][1] if len(ranked) >= 2 else 0.0

    answers = answer if isinstance(answer, list) else [answer]
    n_answers = len(answers)

    # 命中判断(多意图:Top-1 命中任意一个即算 hit1)
    hit1 = top1_pid in answers
    hit3 = any(a in ids for a in answers)

    # 排名:取所有正确答案中最靠前的那个
    ranks = []
    for a in answers:
        try:
            ranks.append(ids.index(a) + 1)
        except ValueError:
            pass
    correct_rank = min(ranks) if ranks else 0

    # 覆盖度 / 精度(仅多意图有意义,单意图等价于 hit1)
    coverage1 = sum(1 for a in answers if a == top1_pid) / n_answers
    coverage3 = sum(1 for a in answers if a in ids) / n_answers
    precision1 = sum(1 for a in answers if a == top1_pid) / 1   # = coverage1
    precision3 = sum(1 for a in answers if a in ids[:3]) / min(3, len(ids)) if ids else 0.0

    return {
        "top1_pid": top1_pid,
        "top1_score": top1_score,
        "margin": top1_score - top2_score,
        "hit1": hit1,
        "hit3": hit3,
        "correct_rank": correct_rank,
        "coverage1": coverage1,
        "coverage3": coverage3,
        "precision1": precision1,
        "precision3": precision3,
        "is_multi": n_answers > 1,
        "num_answers": n_answers,
    }


def run_eval(retriever, kw_retriever=None):
    """对每条 case 跑 A/B/C/D/E 五路,收集结构化结果。"""
    cases = []
    for case in TEST_SET:
        raw = case["raw"]
        answer = case.get("answers", case.get("answer"))  # list 或 str
        rewritten = rewrite_query(raw)
        dbg = {}

        ranked = {
            "A": retriever.retrieve(raw, top_k_parents=3),
            "B": retriever.retrieve(rewritten, top_k_parents=3),
            "C": retriever.retrieve(rewritten, top_k_parents=3,
                                    use_rerank=True, debug=dbg),
        }
        if kw_retriever is not None:
            ranked["D"] = kw_retriever.retrieve(rewritten, top_k_parents=3)
            ranked["E"] = hybrid_retrieve(retriever, kw_retriever,
                                          rewritten, top_k_parents=3)
        arms = {k: eval_one(v, answer) for k, v in ranked.items()}
        if "C" in arms:
            arms["C"]["used_rerank"] = dbg.get("used_rerank", False)
        cases.append({
            "raw": raw, "answer": answer,
            "difficulty": case.get("difficulty", "unknown"),
            "arms": arms,
        })
    return cases


def bar(pct, width=10):
    fill = round(pct / 100 * width)
    return "█" * fill + "░" * (width - fill)


def _dw(s):
    """字符串显示宽度:CJK/全角算 2,其余算 1。"""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(s))


def pad(s, width):
    """按显示宽度左对齐补空格(解决中文双宽错位)。超宽则按显示宽度截断。"""
    s = str(s)
    if _dw(s) > width:
        out = ""
        for ch in s:
            if _dw(out + ch) > width:
                break
            out += ch
        s = out
    return s + " " * (width - _dw(s))


# ---------- ① 逐条明细 ----------
def print_detail_table(cases):
    print("\n══════════ ① 逐条明细(✓命中 ✗未命中,括号内为 Top1 范式+分数)══════════")
    arm_width = 15
    header = pad("用户口语", 26) + pad("正确", 14)
    for _, label in ARMS:
        header += pad(label, arm_width)
    print(header)
    print("-" * (26 + 14 + arm_width * len(ARMS)))
    for c in cases:
        cells = []
        for k, _ in ARMS:
            a = c["arms"].get(k)
            if a is None:
                cells.append(pad("-", arm_width))
                continue
            mark = "✓" if a["hit1"] else "✗"
            star = "" if a.get("used_rerank", True) else "*"
            cells.append(pad(f"{mark}{a['top1_pid']} {a['top1_score']:.2f}{star}", arm_width))
        answer_disp = "+".join(c["answer"]) if isinstance(c["answer"], list) else c["answer"]
        print(pad(c["raw"], 26) + pad(answer_disp, 14) + "".join(cells))
    if any(not c["arms"].get("C", {}).get("used_rerank", True) for c in cases if "C" in c["arms"]):
        print("  (* = 该条 rerank 调用失败,已回退 cosine 分数)")


# ---------- ② 翻盘 / 翻车归因 ----------
def print_attribution_cases(cases):
    print("\n══════════ ② 翻盘 / 翻车归因(把提升归因到具体优化)══════════")
    flips = []
    for c in cases:
        a, b, cc = c["arms"]["A"], c["arms"]["B"], c["arms"]["C"]
        q = c["raw"][:20]
        if not a["hit1"] and b["hit1"]:
            flips.append(f"✅ 翻盘 [改写救场]   \"{q}\"  A:{a['top1_pid']}✗ → B:{b['top1_pid']}✓")
        if a["hit1"] and not b["hit1"]:
            flips.append(f"⚠️ 翻车 [改写带偏]   \"{q}\"  A:{a['top1_pid']}✓ → B:{b['top1_pid']}✗")
        if not b["hit1"] and cc["hit1"]:
            flips.append(f"✅ 翻盘 [rerank救场] \"{q}\"  B:{b['top1_pid']}✗ → C:{cc['top1_pid']}✓")
        if b["hit1"] and not cc["hit1"]:
            flips.append(f"⚠️ 翻车 [rerank带偏] \"{q}\"  B:{b['top1_pid']}✓ → C:{cc['top1_pid']}✗")
    if flips:
        for line in flips:
            print("  " + line)
    else:
        print("  (本轮三路 Top-1 命中一致,无翻盘/翻车)")


# ---------- ③ 置信度对比 ----------
def print_confidence(cases):
    print("\n══════════ ③ 置信度对比(仅统计命中项)══════════")
    header = pad("", 16) + "".join(pad(label, 12) for _, label in ARMS)
    print(header)
    avg_score, avg_margin = {}, {}
    for k, _ in ARMS:
        hits = [c["arms"][k] for c in cases if c["arms"][k]["hit1"]]
        avg_score[k] = np.mean([h["top1_score"] for h in hits]) if hits else 0.0
        avg_margin[k] = np.mean([h["margin"] for h in hits]) if hits else 0.0
    print(pad("平均 Top1 分数", 16)
          + "".join(pad(f"{avg_score[k]:.3f}", 12) for k, _ in ARMS))
    print(pad("平均 margin", 16)
          + "".join(pad(f"{avg_margin[k]:.3f}", 12) for k, _ in ARMS))
    print("  margin = top1分 − top2分,越大越敢下结论(rerank 通常显著拉大)")
    print("  ⚠️ A/B 用 cosine 相似度(0~1),C 用 gte-rerank relevance_score,"
          "尺度不同,Top1 分数横比仅供定性参考，应以⑤排名指标为准")


# ---------- ④ 命中率汇总 + 归因 ----------
def print_summary_attribution(cases):
    n = len(cases)
    top1 = {k: sum(c["arms"][k]["hit1"] for c in cases) / n * 100 for k, _ in ARMS}
    top3 = {k: sum(c["arms"][k]["hit3"] for c in cases) / n * 100 for k, _ in ARMS}

    print("\n══════════ ④ 命中率汇总 + 归因 ══════════")
    print(f"{'方案':<14}{'Top-1':<18}{'Top-3':<8}")
    print("-" * 46)
    for k, label in ARMS:
        print(f"{label:<13}{top1[k]:>4.0f}% {bar(top1[k])}   {top3[k]:>4.0f}%")

    print("\n归因分解(Top-1):")
    print(f"  query 改写贡献  {top1['B'] - top1['A']:+5.0f} pp"
          f"  (A {top1['A']:.0f}% → B {top1['B']:.0f}%)")
    print(f"  rerank   贡献  {top1['C'] - top1['B']:+5.0f} pp"
          f"  (B {top1['B']:.0f}% → C {top1['C']:.0f}%)")
    print("  " + "─" * 28)
    print(f"  总提升        {top1['C'] - top1['A']:+5.0f} pp"
          f"  ({top1['A']:.0f}% → {top1['C']:.0f}%)")


# ---------- ⑤ 排序质量指标(MRR / NDCG)——纯排名,跨方案可比 ----------
def print_ranking_quality(cases):
    print("\n══════════ ⑤ 排序质量指标(MRR / NDCG)══════════")
    print("  MRR 衡量『正确答案最早出现在第几位』，NDCG 衡量排名列表的整体质量。")
    print("  两者只看排名不看分数，因此 A/B/C 五路方案的分数尺度差异不影响结果。")
    print()
    print(f"{'指标':<12}" + "".join(pad(label, 14) for _, label in ARMS))
    print("-" * (12 + 14 * len(ARMS)))
    arms_data = {k: [c["arms"][k] for c in cases] for k, _ in ARMS}
    for metric_name, func, args in [
        ("MRR", mrr, {}),
        ("NDCG@1", ndcg_at_k, {"k": 1}),
        ("NDCG@3", ndcg_at_k, {"k": 3}),
    ]:
        vals = [func(arms_data[k], **args) for k, _ in ARMS]
        print(pad(metric_name, 12) + "".join(pad(f"{v:.4f}", 14) for v in vals))
    print()
    print("  解读:")
    print("  · MRR 越接近 1 说明正确答案越靠前(1=全在 Top-1,0=全未命中)")
    print("  · NDCG@1 = hit1 率(数学上等价,验证用)")
    print("  · NDCG@3 衡量 Top-3 内的排序质量,命中越靠前分越高")


# ---------- ⑥ 命中率按难度分档 ----------
def print_difficulty_breakdown(cases):
    print("\n══════════ ⑥ 命中率按难度分档 ══════════")
    tiers = ["easy", "medium", "hard", "multi"]
    tier_labels = {
        "easy": "简单(完整句子+关键词)", "medium": "中等(口语绕圈)",
        "hard": "困难(单字/边界混淆)", "multi": "多意图(一句话多需求)",
    }
    header = f"{'难度':<18}{'数量':<6}" + "".join(pad(label, 14) for _, label in ARMS)
    print(header)
    print("-" * (18 + 6 + 14 * len(ARMS)))
    for tier in tiers:
        subset = [c for c in cases if c["difficulty"] == tier]
        n = len(subset)
        if n == 0:
            continue
        h = {
            k: sum(c["arms"][k]["hit1"] for c in subset) / n * 100
            for k, _ in ARMS
        }
        print(f"{tier_labels[tier]:<18}{n:<6}"
              + "".join(f"{h[k]:>5.0f}% {bar(h[k], 6)}  " for k, _ in ARMS))
    print()
    print("  解读:难度越高命中率越低 → 方案差异越大;各路方案在不同难度档的表现可以看出")
    print("  改写/rerank 主要在哪个难度区间起作用(通常 medium/hard 档差异最显著)")


# ---------- ⑦ 置信度门控评估(阈值扫描) ----------
def print_confidence_gating(cases):
    print("\n══════════ ⑦ 置信度门控评估(阈值扫描)══════════")
    print("  设定 margin 阈值,只接受 margin ≥ 阈值的预测,其余拒答/转人工。")
    print("  阈值 ↑ → 拒答率 ↑ → 精度 ↑ → 召回 ↓,找 F1 最高点。")
    print()

    for k, label in ARMS:
        arm_data = [(c["arms"][k]["margin"], c["arms"][k]["hit1"]) for c in cases]
        margins = sorted(set(m[0] for m in arm_data))
        total_cases = len(arm_data)
        total_hits = sum(1 for _, h in arm_data if h)

        if total_hits == 0:
            print(f"  {label}: 无命中,跳过")
            continue

        # 生成阈值序列(步长自适应)
        max_m = max(margins)
        step = max(0.02, round(max_m / 15, 3))
        thresholds = [round(t, 3) for t in np.arange(0, max_m + step, step)]

        best = {"thresh": 0, "f1": 0, "prec": 0, "rec": 0, "rej": 0}
        rows = []
        for thresh in thresholds:
            accepted = [(m, h) for m, h in arm_data if m >= thresh]
            n_acc = len(accepted)
            n_hit = sum(1 for _, h in accepted if h)
            prec = n_hit / n_acc if n_acc > 0 else 0.0
            rec = n_hit / total_hits if total_hits > 0 else 0.0
            rej = (total_cases - n_acc) / total_cases
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            rows.append((thresh, prec, rec, rej, f1))
            if f1 > best["f1"]:
                best = {"thresh": thresh, "f1": f1, "prec": prec,
                        "rec": rec, "rej": rej}

        # 选 8 个代表性阈值展示
        key_ts = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50]
        show = []
        for kt in key_ts:
            nearest = min(rows, key=lambda r: abs(r[0] - kt))
            if nearest not in show:
                show.append(nearest)
        # 加最佳点
        best_row = next(r for r in rows if abs(r[0] - best["thresh"]) < 0.001)
        if best_row not in show:
            show.append(best_row)
        show.sort(key=lambda r: r[0])

        print(f"  ▸ {label}")
        print(f"    {'阈值':>8}  {'精度':>8}  {'召回':>8}  {'拒答率':>8}  {'F1':>8}")
        print(f"    {'-' * 45}")
        for thresh, prec, rec, rej, f1 in show:
            marker = " ◀ 最高F1" if abs(thresh - best["thresh"]) < 0.001 else ""
            print(f"    {thresh:>8.3f}  {prec:>7.1%}  {rec:>7.1%}  {rej:>7.1%}  {f1:>7.3f}{marker}")

        print(f"    阈值=0(不过滤):精度={best['prec']*0+rows[0][1]:.1%} → "
              f"最佳阈值={best['thresh']:.3f} 时精度={best['prec']:.1%},"
              f"拒答={best['rej']:.1%},F1={best['f1']:.3f}")
        print()

    print("  解读:")
    print("  · 门控阈值是生产决策工具:margin < 阈值 → 拒答或转人工,避免低置信度错误")
    print("  · 改写/rerank 提升 margin 不是为了命中率,而是让门控更可用(相同精度下拒答率更低)")
    print("  · C 路 rerank 的 margin 分布更宽 → 可选阈值范围更大 → 门控灵活性最好")


# ---------- ⑧ 多意图覆盖度 ----------
def print_multi_intent_coverage(cases):
    multi = [c for c in cases if c["arms"].get("A", {}).get("is_multi")]
    if not multi:
        print("\n══════════ ⑧ 多意图覆盖度(无多意图 case,跳过)══════════")
        return

    print("\n══════════ ⑧ 多意图覆盖度(Co=覆盖了几成意图,Pr=Top-K 里几成相关)══════════")
    print(f"  共 {len(multi)} 条多意图 case, 每条 2 个正确答案")

    # 逐条明细
    col_w = 16
    header = pad("用户口语", 24) + pad("正确答案", 22)
    for _, label in ARMS:
        header += pad(label, col_w)
    print(header)
    print("-" * (24 + 22 + col_w * len(ARMS)))
    for c in multi:
        ans_str = "+".join(c["answer"]) if isinstance(c["answer"], list) else c["answer"]
        row = pad(c["raw"], 24) + pad(ans_str, 22)
        for k, _ in ARMS:
            a = c["arms"][k]
            # 显示: Top1 pid + coverage@3
            cov3 = a["coverage3"]
            marker = "✓" if cov3 == 1.0 else ("◐" if cov3 >= 0.5 else "✗")
            row += pad(f"{marker}{a['top1_pid']} Co3={cov3:.0%}", col_w)
        print(row)

    # 汇总
    print(f"\n  {'指标':<14}", end="")
    for _, label in ARMS:
        print(f"{label:<16}", end="")
    print()
    print("  " + "-" * (14 + 16 * len(ARMS)))

    for metric_name, key in [("Coverage@1", "coverage1"), ("Coverage@3", "coverage3"),
                              ("Precision@3", "precision3")]:
        vals = [np.mean([c["arms"][k][key] for c in multi]) for k, _ in ARMS]
        print(f"  {metric_name:<14}", end="")
        for v in vals:
            print(f"{v:<16.1%}", end="")
        print()

    # F1@3 = 2 * Cov@3 * Pr@3 / (Cov@3 + Pr@3)
    print(f"  {'F1@3':<14}", end="")
    for k, _ in ARMS:
        cov = np.mean([c["arms"][k]["coverage3"] for c in multi])
        prc = np.mean([c["arms"][k]["precision3"] for c in multi])
        f1 = 2 * cov * prc / (cov + prc) if (cov + prc) > 0 else 0.0
        print(f"{f1:<16.3f}", end="")
    print()

    print()
    print("  解读:")
    print("  · Coverage@k:用户 N 个意图中,Top-K 检索覆盖了几个(100%=全找到)")
    print("  · Precision@k:Top-K 返回的结果中,几成是用户真正要的")
    print("  · F1@3:覆盖度与精度的调和平均,综合衡量检索质量")
    print("  · 多意图场景下,向量检索通常偏好『最像』的那个而忽略次要意图")


# ---------- ⑨ 多意图拆分方案对比(仅多意图 case) ----------
def print_decomp_comparison(cases, retriever):
    multi = [c for c in cases if isinstance(c.get("answer"), list)]
    if not multi:
        return

    print("\n══════════ ⑨ 多意图拆分方案对比(规则 vs LLM)══════════")
    print(f"  共 {len(multi)} 条多意图 case,对比 B(不拆分) / F(规则拆分) / G(LLM拆分)")

    # 逐条:显示拆分结果
    print(f"\n  {'原句':<22}{'F 规则拆分子句':<38}{'G LLM拆分子句':<38}")
    print("  " + "-" * 98)

    results = {"F": [], "G": [], "B": []}

    for c in multi:
        raw = c["raw"]
        answer_list = c["answer"]

        # B 路(已有)
        b_arm = c["arms"]["B"]
        results["B"].append({
            "coverage3": b_arm["coverage3"], "precision3": b_arm["precision3"],
            "hit1": b_arm["hit1"], "hit3": b_arm["hit3"],
        })

        # F:规则拆分
        f_subs = decompose_by_rules(raw)
        f_ranked = decomp_retrieve(retriever, raw)
        f_eval = eval_one(f_ranked, answer_list)
        results["F"].append({
            "coverage3": f_eval["coverage3"], "precision3": f_eval["precision3"],
            "hit1": f_eval["hit1"], "hit3": f_eval["hit3"],
        })

        # G:LLM拆分
        g_subs = decompose_by_llm(raw)
        g_ranked = decomp_retrieve_llm(retriever, raw)
        g_eval = eval_one(g_ranked, answer_list)
        results["G"].append({
            "coverage3": g_eval["coverage3"], "precision3": g_eval["precision3"],
            "hit1": g_eval["hit1"], "hit3": g_eval["hit3"],
        })

        f_str = " | ".join(f_subs[:3])
        g_str = " | ".join(g_subs[:3])
        print(f"  {pad(raw, 22)}{pad(f_str, 38)}{pad(g_str, 38)}")

    # 汇总
    print(f"\n  {'指标':<16}{'B 不拆分':<14}{'F 规则拆分':<14}{'G LLM拆分':<14}")
    print("  " + "-" * 58)
    for metric_name, key in [("Coverage@3", "coverage3"),
                              ("Precision@3", "precision3")]:
        vals = [np.mean([r[key] for r in results[arm]]) for arm in ["B", "F", "G"]]
        print(f"  {metric_name:<16}" + "".join(f"{v:<14.1%}" for v in vals))
    # F1@3
    print(f"  {'F1@3':<16}", end="")
    for arm in ["B", "F", "G"]:
        cov = np.mean([r["coverage3"] for r in results[arm]])
        prc = np.mean([r["precision3"] for r in results[arm]])
        f1 = 2 * cov * prc / (cov + prc) if (cov + prc) > 0 else 0.0
        print(f"{f1:<14.3f}", end="")
    print()
    # Hit1
    print(f"  {'Hit1(Top1准确)':<16}", end="")
    for arm in ["B", "F", "G"]:
        h = np.mean([r["hit1"] for r in results[arm]])
        print(f"{h:<14.1%}", end="")
    print()

    print(f"\n  解读:")
    print("  · 规则拆分:零延迟,但对\"还要/同时\"等连接词覆盖不全,口语绕圈拆不开")
    print(f"  · LLM拆分:+1 次 {LLM_MODEL} 调用,能理解隐含意图、补全模糊词")
    print("  · 最佳生产策略:优先规则拆分 → 拆不开时 fallback LLM")


# ============ 9. 主流程 ============
def main():
    if not dashscope.api_key:
        print("❌ 请先设置 DASHSCOPE_API_KEY")
        return

    children = build_child_chunks(PARENT_DOCS)
    print(f"模型: {MODEL} | 维度: {DIM} | rerank: {RERANK_MODEL}")
    print(f"父块: {len(PARENT_DOCS)} 条 | 子块: {len(children)} 条 "
          f"(平均 {len(children)/len(PARENT_DOCS):.1f} 个/父块)")

    retriever = SmallToBigRetriever(PARENT_DOCS, children)

    print("  构建关键词倒排索引...")
    kw_retriever = KeywordRetriever(PARENT_DOCS, children)

    print("\n检索测试中(每条跑 A/B/C/D/E 五路)...")
    cases = run_eval(retriever, kw_retriever)

    print_detail_table(cases)
    print_attribution_cases(cases)
    print_confidence(cases)
    print_summary_attribution(cases)
    print_ranking_quality(cases)
    print_difficulty_breakdown(cases)
    print_confidence_gating(cases)
    print_multi_intent_coverage(cases)
    print_decomp_comparison(cases, retriever)

    # 演示元数据过滤(走精排)
    print("\n══════════ 演示:元数据过滤(multi_user=True) + rerank ══════════")
    demo_q = rewrite_query("做个团队用的客户跟进工具")
    ranked = retriever.retrieve(demo_q, top_k_parents=3,
                                meta_filter={"multi_user": True}, use_rerank=True)
    print(f"query: {demo_q}\nfilter: multi_user=True\n命中:")
    for pid, score in ranked:
        p = retriever.get_parent(pid)
        print(f"  {pid} | {score:.3f} | {p['title']}")

    # 演示父块召回
    if ranked:
        top_pid = ranked[0][0]
        parent = retriever.get_parent(top_pid)
        print(f"\n══════════ 演示:喂给 Planner 的完整父块({top_pid})══════════")
        print(f"标题:{parent['title']}")
        print("plan 步骤:")
        for s in parent["plan_steps"]:
            print(f"  - {s}")
        print(f"常见坑:{', '.join(parent['pitfalls'])}")
        print(f"元数据:{parent['metadata']}")


if __name__ == "__main__":
    main()
