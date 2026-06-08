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
from dashscope import TextEmbedding
from http import HTTPStatus


from config import DASHSCOPE_API_KEY, EMBED_MODEL, EMBED_DIM

MODEL = EMBED_MODEL
DIM = EMBED_DIM
dashscope.api_key = DASHSCOPE_API_KEY


# ============ 1. 父块:完整范式(不向量化,只存) ============
PARENT_DOCS = [
    {
        "id": "P_crm",
        "title": "团队 CRM / 客户跟进范式",
        "plan_steps": [
            "数据建模:customers / follow_ups / team_members 三张表",
            "认证:Supabase Auth 邮箱登录",
            "权限:RLS 按 team_id 隔离",
            "页面:客户列表、客户详情、跟进时间线、新增跟进表单",
            "逻辑:跟进状态流转(待跟进→跟进中→已成交)",
        ],
        "pitfalls": ["忘记做 team 维度隔离", "跟进记录没做软删除"],
        "metadata": {
            "domain": "CRM", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_ecommerce",
        "title": "电商在线商城范式",
        "plan_steps": [
            "数据建模:products / orders / cart_items 表",
            "商品列表/详情页", "购物车逻辑", "下单流程 + 支付接入",
        ],
        "pitfalls": ["库存并发扣减", "支付回调幂等性"],
        "metadata": {
            "domain": "Ecommerce", "complexity": "高",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_admin",
        "title": "多角色后台管理范式",
        "plan_steps": [
            "数据建模:users / roles / permissions 表",
            "RBAC 权限模型", "通用数据表格 CRUD", "角色与权限管理页",
        ],
        "pitfalls": ["权限粒度过细难维护", "前后端权限要一致"],
        "metadata": {
            "domain": "Admin", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_blog",
        "title": "个人博客 / 内容发布范式",
        "plan_steps": [
            "数据建模:posts / categories / tags 表",
            "Markdown 编辑器", "文章列表/详情页", "分类标签筛选",
        ],
        "pitfalls": ["SEO 元信息缺失", "Markdown XSS 防护"],
        "metadata": {
            "domain": "Blog", "complexity": "低",
            "multi_user": False, "need_auth": True, "entity_count": 3,
        },
    },
    {
        "id": "P_todo",
        "title": "个人任务待办清单范式",
        "plan_steps": [
            "数据建模:tasks 表", "任务 CRUD",
            "完成状态切换", "截止日期与提醒",
        ],
        "pitfalls": ["提醒时区问题"],
        "metadata": {
            "domain": "Tool", "complexity": "低",
            "multi_user": False, "need_auth": False, "entity_count": 1,
        },
    },
    {
        "id": "P_ticket",
        "title": "客服工单系统范式",
        "plan_steps": [
            "数据建模:tickets / agents 表", "工单提交表单",
            "分配逻辑", "状态流转:待处理→处理中→已解决",
        ],
        "pitfalls": ["工单分配负载不均", "状态变更审计"],
        "metadata": {
            "domain": "Support", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
    {
        "id": "P_booking",
        "title": "预约预订系统范式",
        "plan_steps": [
            "数据建模:bookings / slots 表", "日历选时间段",
            "预约确认流程", "防重叠校验",
        ],
        "pitfalls": ["并发预约同一时段", "时区与跨天处理"],
        "metadata": {
            "domain": "Booking", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
    {
        "id": "P_inventory",
        "title": "库存进销存管理范式",
        "plan_steps": [
            "数据建模:products / stock_records 表",
            "入库/出库表单", "库存实时统计", "低库存预警",
        ],
        "pitfalls": ["库存负数", "批量操作事务"],
        "metadata": {
            "domain": "Inventory", "complexity": "中",
            "multi_user": True, "need_auth": True, "entity_count": 2,
        },
    },
]


# ============ 2. 子块:多视角场景描述(只有 content 入向量库) ============
SCENE_VARIANTS = {
    "P_crm": [
        "团队协作的客户关系管理系统,记录客户信息和跟进状态",
        "销售人员跟进客户、记录沟通历史与成交进展",
        "多人共享维护的客户资料库与跟进时间线",
    ],
    "P_ecommerce": [
        "在线商城,商品展示购物车下单支付完整流程",
        "电商网站,用户浏览商品、加购物车、结账付款",
        "面向消费者的在线零售平台,含商品订单支付",
    ],
    "P_admin": [
        "后台管理系统,多角色权限控制与数据增删改查",
        "企业内部管理平台,按角色分配不同操作权限",
        "RBAC 权限模型的管理后台,支持多角色协作",
    ],
    "P_blog": [
        "个人博客与内容发布站点,撰写文章并展示",
        "Markdown 写作发布平台,支持分类与标签",
        "面向读者的文章发布与阅读站点",
    ],
    "P_todo": [
        "个人任务待办清单工具,记录与完成任务",
        "个人事项管理,创建任务、打勾完成、设提醒",
        "轻量待办清单,跟踪每日要做的事情",
    ],
    "P_ticket": [
        "客服工单系统,客户提单、客服处理与跟踪",
        "工单提交与处理流程,分配给客服跟进解决",
        "技术支持工单平台,从提交到解决的状态跟踪",
    ],
    "P_booking": [
        "预约预订系统,用户选时间段进行预约",
        "在线预约平台,日历选时间、确认预订",
        "时间段预订与防冲突的预约管理",
    ],
    "P_inventory": [
        "库存进销存管理,商品入库出库与实时统计",
        "仓库存货管理,跟踪入库、出库与库存量",
        "商品库存系统,管理进货、出货与剩余数量",
    ],
}


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


# ============ 3. 测试集 ============
TEST_SET = [
    {"raw": "帮我做个能让团队记录客户跟进情况的小工具", "answer": "P_crm"},
    {"raw": "我想搞一个卖东西的网站,能下单付款那种", "answer": "P_ecommerce"},
    {"raw": "做个能管不同用户权限的后台", "answer": "P_admin"},
    {"raw": "弄个可以写文章发出去的地方", "answer": "P_blog"},
    {"raw": "整个记事情的清单,能打勾那种", "answer": "P_todo"},
    {"raw": "客户有问题能提单子,我们这边处理跟进", "answer": "P_ticket"},
    {"raw": "搞个让人选时间来预约的系统", "answer": "P_booking"},
    {"raw": "管仓库进货出货还有剩多少的东西", "answer": "P_inventory"},
    {"raw": "做个销售团队跟进客户、看进展的玩意儿", "answer": "P_crm"},
    {"raw": "我要一个网店,客人能加购物车结账", "answer": "P_ecommerce"},
]


# ============ 4. query 改写 ============
STOPWORDS = ["帮我", "做个", "搞一个", "搞个", "弄个", "整个", "我想", "我要",
             "的小工具", "那种", "玩意儿", "东西", "地方", "系统", "能", "可以",
             "一个", "做", "的"]

TERM_MAP = {
    "客户跟进": "客户关系管理 CRM 销售跟进",
    "跟进客户": "客户关系管理 CRM 销售跟进",
    "团队记录客户": "团队协作 客户关系管理 CRM",
    "卖东西的网站": "电商 在线商城",
    "网店": "电商 在线商城",
    "下单付款": "下单 支付",
    "加购物车结账": "购物车 下单 支付",
    "管不同用户权限": "多角色 权限控制 RBAC 后台管理",
    "写文章发出去": "内容发布 博客 文章",
    "记事情的清单": "任务 待办 清单",
    "打勾": "完成状态",
    "提单子": "工单 提交",
    "处理跟进": "工单 处理 状态跟踪",
    "选时间来预约": "预约 预订 时间段",
    "进货出货": "库存 进销存 入库 出库",
    "剩多少": "库存统计",
    "看进展": "状态跟踪",
}


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


# ============ 6. small-to-big 检索器 ============
class SmallToBigRetriever:
    def __init__(self, parents, children):
        self.parents = {p["id"]: p for p in parents}
        self.children = children
        contents = [c["content"] for c in children]
        print(f"  向量化 {len(contents)} 个子块...")
        self.child_vecs = embed(contents, text_type="document")

    def retrieve(self, query_text, top_k_parents=3, meta_filter: Optional[dict] = None):
        """
        meta_filter: 如 {"multi_user": True},检索前硬过滤子块。
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
            return []

        sims = cosine(qv, self.child_vecs[valid_idx])[0]

        # small-to-big:按 parent_id 聚合,同父块多子块取 MAX
        parent_scores = defaultdict(float)
        for local_i, sim in zip(valid_idx, sims):
            pid = self.children[local_i]["metadata"]["parent_id"]
            if sim > parent_scores[pid]:
                parent_scores[pid] = float(sim)

        return sorted(parent_scores.items(), key=lambda x: -x[1])[:top_k_parents]

    def get_parent(self, parent_id):
        return self.parents[parent_id]


# ============ 7. 主流程 ============
def main():
    if not dashscope.api_key:
        print("❌ 请先设置 DASHSCOPE_API_KEY")
        return

    children = build_child_chunks(PARENT_DOCS)
    print(f"模型: {MODEL} | 维度: {DIM}")
    print(f"父块: {len(PARENT_DOCS)} 条 | 子块: {len(children)} 条 "
          f"(平均 {len(children)/len(PARENT_DOCS):.1f} 个/父块)\n")

    retriever = SmallToBigRetriever(PARENT_DOCS, children)

    results = {"A_raw": {"top1": 0, "top3": 0}, "B_rewritten": {"top1": 0, "top3": 0}}
    rows = []

    print("\n检索测试中...")
    for case in TEST_SET:
        raw, answer = case["raw"], case["answer"]
        rewritten = rewrite_query(raw)

        a = retriever.retrieve(raw, top_k_parents=3)
        b = retriever.retrieve(rewritten, top_k_parents=3)
        a_ids = [pid for pid, _ in a]
        b_ids = [pid for pid, _ in b]

        a1 = a_ids[0] == answer if a_ids else False
        b1 = b_ids[0] == answer if b_ids else False
        a3 = answer in a_ids
        b3 = answer in b_ids

        results["A_raw"]["top1"] += a1
        results["A_raw"]["top3"] += a3
        results["B_rewritten"]["top1"] += b1
        results["B_rewritten"]["top3"] += b3

        rows.append((raw, answer, a1, a_ids[0] if a_ids else "-",
                     b1, b_ids[0] if b_ids else "-"))

    print("\n===== 逐条明细 =====")
    print(f"{'用户口语':<24}{'正确':<14}{'A原始Top1':<16}{'B改写Top1':<16}")
    print("-" * 70)
    for raw, ans, a1, atop, b1, btop in rows:
        print(f"{raw[:22]:<24}{ans:<13}"
              f"{'✓' if a1 else '✗'}({atop:<12}){'✓' if b1 else '✗'}({btop})")

    n = len(TEST_SET)
    print("\n===== 命中率汇总 =====")
    print(f"{'方案':<18}{'Top-1':<12}{'Top-3':<12}")
    print("-" * 42)
    for k, label in [("A_raw", "A 原始口语"), ("B_rewritten", "B 改写后")]:
        t1 = results[k]["top1"] / n * 100
        t3 = results[k]["top3"] / n * 100
        print(f"{label:<16}{t1:>5.0f}%{'':<7}{t3:>5.0f}%")

    a1 = results["A_raw"]["top1"] / n * 100
    b1 = results["B_rewritten"]["top1"] / n * 100
    print(f"\n>>> query 改写 Top-1 提升:{a1:.0f}% → {b1:.0f}% (+{b1 - a1:.0f}pp)")

    # 演示元数据过滤
    print("\n===== 演示:元数据过滤(multi_user=True) =====")
    demo_q = rewrite_query("做个团队用的客户跟进工具")
    ranked = retriever.retrieve(demo_q, top_k_parents=3,
                                 meta_filter={"multi_user": True})
    print(f"query: {demo_q}\nfilter: multi_user=True\n命中:")
    for pid, score in ranked:
        p = retriever.get_parent(pid)
        print(f"  {pid} | {score:.3f} | {p['title']}")

    # 演示父块召回
    if ranked:
        top_pid = ranked[0][0]
        parent = retriever.get_parent(top_pid)
        print(f"\n===== 演示:喂给 Planner 的完整父块({top_pid})=====")
        print(f"标题:{parent['title']}")
        print("plan 步骤:")
        for s in parent["plan_steps"]:
            print(f"  - {s}")
        print(f"常见坑:{', '.join(parent['pitfalls'])}")
        print(f"元数据:{parent['metadata']}")


if __name__ == "__main__":
    main()
