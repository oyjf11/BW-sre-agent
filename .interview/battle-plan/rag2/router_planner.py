"""
Router → Planner Pipeline(本地可跑)
=====================================
链路:
  用户口语
    → Router(意图识别 + RAG 检索拿范式)        [复用 rag_eval 的检索]
    → Planner(LLM 融合规划,产出结构化任务图 DAG)
        ├─ LLM 为主:qwen 融合"范式+用户需求"→ JSON DAG
        └─ 规则兜底:解析失败/缺字段/有环 → 修复或回退到范式直转
    → 自检(无环校验 + 拓扑排序 + 完整性检查)
    → 打印可执行任务图

依赖:pip install dashscope numpy
环境变量:export DASHSCOPE_API_KEY=sk-xxx

说明:Router 部分直接复用 rag_eval.py 里的检索器和数据,
     所以这个文件要和 rag_eval.py 放在同一目录。
"""

import os
import json
from collections import defaultdict, deque
from typing import Optional

import dashscope
from dashscope import Generation
from http import HTTPStatus

# 复用 Router/RAG 部分
from rag_eval import (
    PARENT_DOCS, build_child_chunks, rewrite_query,
    SmallToBigRetriever,
)

from config import DASHSCOPE_API_KEY, LLM_MODEL, LLM_TEMPERATURE

dashscope.api_key = DASHSCOPE_API_KEY


# ============================================================
# Router:意图识别(规则版) + RAG 检索
# ============================================================
def router(user_input: str, retriever: SmallToBigRetriever):
    """产出:{原始需求, 改写query, 命中范式父块, 结构化意图}"""
    rewritten = rewrite_query(user_input)
    ranked = retriever.retrieve(rewritten, top_k_parents=1, use_rerank=True)
    if not ranked:
        return None
    top_pid, score = ranked[0]
    parent = retriever.get_parent(top_pid)

    # 简单的结构化意图(真实系统这步也可以用小模型)
    intent = {
        "domain": parent["metadata"]["domain"],
        "multi_user": parent["metadata"]["multi_user"],
        "need_auth": parent["metadata"]["need_auth"],
    }
    return {
        "raw_requirement": user_input,
        "rewritten_query": rewritten,
        "matched_parent": parent,
        "match_score": score,
        "intent": intent,
    }


# ============================================================
# Planner —— LLM 为主
# ============================================================
PLANNER_SYSTEM = """你是一个全栈应用规划器(Planner)。你的任务是把【参考范式】和【用户需求】融合,产出一份结构化的任务图(DAG)。

严格遵守:
1. 优先基于【参考范式】,不要脱离范式凭空设计架构。
2. 用户需求里范式没覆盖的点,作为新任务加入,并在 source 字段标注 "requirement"。
3. 范式里和用户需求无关的步骤,要剔除,不要硬凑。
4. 用户没说清的细节,用范式默认做法,并在 note 字段标注 "默认方案,可调整"。
5. 每个任务必须能溯源:source 取值为 "pattern"(来自范式)或 "requirement"(来自需求)。
6. 任务之间用 depends_on 表达依赖(如建表 T1 要先于认证 T2)。不允许出现循环依赖。

只输出 JSON,不要任何解释、不要 markdown 代码块标记。格式:
{
  "tasks": [
    {
      "id": "T1",
      "type": "schema|auth|rls|page|logic|integration",
      "action": "简短动作描述",
      "detail": "具体内容,如表名/字段/页面名",
      "depends_on": [],
      "source": "pattern|requirement",
      "note": "可选,默认方案标注"
    }
  ]
}"""


def build_planner_prompt(router_out):
    parent = router_out["matched_parent"]
    pattern_text = {
        "title": parent["title"],
        "plan_steps": parent["plan_steps"],
        "pitfalls": parent["pitfalls"],
    }
    return f"""【用户需求】
{router_out['raw_requirement']}

【参考范式】
{json.dumps(pattern_text, ensure_ascii=False, indent=2)}

请融合两者,产出结构化任务图 JSON。"""


def planner_llm(router_out):
    """调用 qwen 做融合规划,返回 dict 或 None(失败)"""
    prompt = build_planner_prompt(router_out)
    resp = Generation.call(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        result_format="message",
        temperature=LLM_TEMPERATURE,   # 规划要稳定,温度调低
    )
    if resp.status_code != HTTPStatus.OK:
        print(f"  ⚠ LLM 调用失败: {resp.code} {resp.message}")
        return None
    text = resp.output.choices[0].message.content.strip()
    # 去掉可能的 markdown 包裹
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ⚠ LLM 返回非合法 JSON: {e}")
        print(f"     原文前 200 字: {text[:200]}")
        return None


# ============================================================
# Planner —— 规则兜底
# ============================================================
def planner_rule_fallback(router_out):
    """LLM 失败时,直接把范式的 plan_steps 线性转成 DAG(每步依赖前一步)"""
    parent = router_out["matched_parent"]
    tasks = []
    for i, step in enumerate(parent["plan_steps"]):
        tasks.append({
            "id": f"T{i+1}",
            "type": "step",
            "action": step.split(":")[0] if ":" in step else step[:10],
            "detail": step,
            "depends_on": [f"T{i}"] if i > 0 else [],
            "source": "pattern",
            "note": "规则兜底:范式线性转换",
        })
    return {"tasks": tasks}


def normalize_tasks(dag):
    """规则层:补全缺失字段,保证下游能用"""
    if not dag or "tasks" not in dag or not isinstance(dag["tasks"], list):
        return None
    fixed = []
    seen_ids = set()
    for i, t in enumerate(dag["tasks"]):
        tid = t.get("id") or f"T{i+1}"
        # 去重 id
        while tid in seen_ids:
            tid = tid + "_dup"
        seen_ids.add(tid)
        fixed.append({
            "id": tid,
            "type": t.get("type", "unknown"),
            "action": t.get("action", ""),
            "detail": t.get("detail", ""),
            "depends_on": [d for d in t.get("depends_on", []) if d],
            "source": t.get("source", "pattern"),
            "note": t.get("note", ""),
        })
    # 清理掉指向不存在节点的依赖
    valid_ids = {t["id"] for t in fixed}
    for t in fixed:
        t["depends_on"] = [d for d in t["depends_on"] if d in valid_ids]
    return {"tasks": fixed}


# ============================================================
# 自检:无环校验 + 拓扑排序 + 完整性
# ============================================================
def topo_sort(tasks):
    """Kahn 算法。返回 (执行顺序, 是否有环)"""
    indeg = {t["id"]: 0 for t in tasks}
    graph = defaultdict(list)
    for t in tasks:
        for dep in t["depends_on"]:
            graph[dep].append(t["id"])
            indeg[t["id"]] += 1

    queue = deque([tid for tid, d in indeg.items() if d == 0])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    has_cycle = len(order) != len(tasks)
    return order, has_cycle


def parallel_layers(tasks):
    """按依赖分层,同层可并行执行"""
    indeg = {t["id"]: len(t["depends_on"]) for t in tasks}
    graph = defaultdict(list)
    tmap = {t["id"]: t for t in tasks}
    for t in tasks:
        for dep in t["depends_on"]:
            graph[dep].append(t["id"])

    layers = []
    cur = [tid for tid, d in indeg.items() if d == 0]
    done = set()
    while cur:
        layers.append(cur)
        nxt = []
        for tid in cur:
            done.add(tid)
            for child in graph[tid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    nxt.append(child)
        cur = nxt
    return layers


def self_check(dag, router_out):
    """完整性 / 一致性自检,返回问题列表(空=通过)"""
    issues = []
    tasks = dag["tasks"]

    # 1. 无环
    order, has_cycle = topo_sort(tasks)
    if has_cycle:
        issues.append("存在循环依赖,无法拓扑排序")

    # 2. 需认证场景必须有 auth 任务
    if router_out["intent"]["need_auth"]:
        if not any(t["type"] == "auth" for t in tasks):
            issues.append("场景需要认证,但 plan 缺少 auth 任务")

    # 3. 多人协作场景检查 RLS(对应范式 pitfall:忘记 team 隔离)
    if router_out["intent"]["multi_user"]:
        has_rls = any(t["type"] == "rls" or "隔离" in t.get("detail", "")
                      or "RLS" in t.get("detail", "") for t in tasks)
        if not has_rls:
            issues.append("多人协作场景但缺少权限隔离(RLS)任务[范式 pitfall]")

    # 4. 必须有数据建模
    if not any(t["type"] == "schema" for t in tasks):
        issues.append("缺少数据建模(schema)任务")

    return issues


# ============================================================
# 编排:Router → Planner → 自检
# ============================================================
def run_pipeline(user_input, retriever, use_llm=True):
    print("=" * 60)
    print(f"【用户输入】{user_input}")

    # --- Router ---
    r = router(user_input, retriever)
    if not r:
        print("Router 未命中任何范式")
        return
    print(f"\n[Router] 改写: {r['rewritten_query']}")
    print(f"[Router] 命中范式: {r['matched_parent']['title']} (score={r['match_score']:.3f})")
    print(f"[Router] 结构化意图: {r['intent']}")

    # --- Planner ---
    dag = None
    if use_llm and dashscope.api_key:
        print(f"\n[Planner] 调用 LLM({LLM_MODEL})融合规划...")
        dag = planner_llm(r)
    if dag is None:
        print("[Planner] 走规则兜底(范式直转 DAG)")
        dag = planner_rule_fallback(r)
    else:
        print("[Planner] LLM 规划成功")

    dag = normalize_tasks(dag)
    if dag is None:
        print("[Planner] 任务图非法,无法继续")
        return

    # --- 自检 ---
    issues = self_check(dag, r)
    print(f"\n[自检] {'通过 ✓' if not issues else '发现问题:'}")
    for iss in issues:
        print(f"   ✗ {iss}")

    # --- 拓扑排序 + 分层 ---
    order, has_cycle = topo_sort(dag["tasks"])
    print(f"\n[任务图] 共 {len(dag['tasks'])} 个任务")
    tmap = {t["id"]: t for t in dag["tasks"]}
    for t in dag["tasks"]:
        dep = f" ← 依赖 {t['depends_on']}" if t["depends_on"] else ""
        print(f"   {t['id']} [{t['type']}] {t['action']} | {t['detail']}"
              f" ({t['source']}){dep}")
        if t.get("note"):
            print(f"        note: {t['note']}")

    if not has_cycle:
        print(f"\n[执行顺序] {' → '.join(order)}")
        layers = parallel_layers(dag["tasks"])
        print(f"[并行分层] (同层可并行)")
        for i, layer in enumerate(layers):
            print(f"   第 {i+1} 层: {layer}")

    return dag


# ============================================================
def main():
    if not dashscope.api_key:
        print("⚠ 未设置 DASHSCOPE_API_KEY,将只跑规则兜底(无 LLM)\n")

    children = build_child_chunks(PARENT_DOCS)
    print(f"建库:父块 {len(PARENT_DOCS)} / 子块 {len(children)}")
    retriever = SmallToBigRetriever(PARENT_DOCS, children)

    # 跑几个例子
    tests = [
        "帮我做个能让团队记录客户跟进情况的小工具,但我们不需要成交金额,只要看进度",
        "做个能管不同用户权限的后台",
    ]
    for t in tests:
        run_pipeline(t, retriever, use_llm=True)
        print()


if __name__ == "__main__":
    main()
