"""
Mock 执行器(Executor)—— 消费 Planner 输出的 DAG
====================================================
演示 Planner 的输出是怎么被下游消费的:
  - 按并行分层逐层执行(同层并发)
  - 每个任务状态流转:pending → running → success / failed
  - 某任务失败 → 单步重试(最多 N 次),重试仍失败则标记并跳过其下游
  - 这里不真生成代码,用 sleep + 随机/指定失败来模拟

依赖:与 router_planner.py / rag_eval.py 同目录
跑法:python mock_executor.py
"""

import time
import random
from collections import defaultdict, deque

from data import DEMO_DAG


# ============================================================
# 状态枚举
# ============================================================
PENDING = "pending"
RUNNING = "running"
SUCCESS = "success"
FAILED = "failed"
SKIPPED = "skipped"   # 因上游失败而无法执行


# ============================================================
# 工具:分层(同 router_planner,独立放这避免循环依赖)
# ============================================================
def parallel_layers(tasks):
    indeg = {t["id"]: len(t["depends_on"]) for t in tasks}
    graph = defaultdict(list)
    for t in tasks:
        for dep in t["depends_on"]:
            graph[dep].append(t["id"])
    layers = []
    cur = [tid for tid, d in indeg.items() if d == 0]
    while cur:
        layers.append(cur)
        nxt = []
        for tid in cur:
            for child in graph[tid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    nxt.append(child)
        cur = nxt
    return layers


# ============================================================
# 单个任务的"执行"(mock)
# ============================================================
def execute_task(task, fail_ids, attempt):
    """
    模拟执行一个任务。
    fail_ids: 指定哪些任务第一次会失败(用来演示重试)
    attempt: 第几次尝试(从 1 开始)
    返回 True=成功 / False=失败
    """
    time.sleep(0.15)  # 模拟耗时
    # 指定任务在第 1 次尝试时失败,重试时成功(模拟"偶发失败,重试可恢复")
    if task["id"] in fail_ids and attempt == 1:
        return False
    return True


# ============================================================
# 执行器主体
# ============================================================
class MockExecutor:
    def __init__(self, dag, max_retry=2, fail_ids=None):
        self.tasks = {t["id"]: t for t in dag["tasks"]}
        self.status = {tid: PENDING for tid in self.tasks}
        self.max_retry = max_retry
        self.fail_ids = fail_ids or set()
        # 反向依赖:某任务失败后,要跳过哪些下游
        self.children = defaultdict(list)
        for t in dag["tasks"]:
            for dep in t["depends_on"]:
                self.children[dep].append(t["id"])

    def _mark_downstream_skipped(self, failed_id):
        """failed_id 失败 → 它的所有下游(传递闭包)标记 skipped"""
        q = deque(self.children[failed_id])
        while q:
            cid = q.popleft()
            if self.status[cid] in (PENDING,):
                self.status[cid] = SKIPPED
                print(f"      ↳ {cid} 因上游 {failed_id} 失败而跳过")
                for grandchild in self.children[cid]:
                    q.append(grandchild)

    def run(self, layers):
        print("\n" + "=" * 50)
        print("【执行器】开始消费 DAG")
        print("=" * 50)

        for li, layer in enumerate(layers):
            # 只执行本层中还是 pending 的(没被跳过的)
            runnable = [tid for tid in layer if self.status[tid] == PENDING]
            print(f"\n── 第 {li+1} 层(可并行 {len(runnable)} 个):{runnable}")

            for tid in runnable:
                task = self.tasks[tid]
                self.status[tid] = RUNNING
                print(f"   [{tid}] {RUNNING}... {task['action']} | {task['detail']}")

                # 执行 + 重试
                ok = False
                for attempt in range(1, self.max_retry + 1):
                    ok = execute_task(task, self.fail_ids, attempt)
                    if ok:
                        if attempt > 1:
                            print(f"        ✓ 第 {attempt} 次重试成功")
                        break
                    else:
                        print(f"        ✗ 第 {attempt} 次失败"
                              f"{',准备重试' if attempt < self.max_retry else ',重试用尽'}")

                if ok:
                    self.status[tid] = SUCCESS
                    print(f"   [{tid}] {SUCCESS} ✓")
                else:
                    self.status[tid] = FAILED
                    print(f"   [{tid}] {FAILED} ✗ —— 标记失败,跳过其下游")
                    self._mark_downstream_skipped(tid)

        self._summary()

    def _summary(self):
        print("\n" + "=" * 50)
        print("【执行结果汇总】")
        counts = defaultdict(int)
        for tid, st in self.status.items():
            counts[st] += 1
        order = [SUCCESS, FAILED, SKIPPED, PENDING]
        for st in order:
            if counts[st]:
                ids = [tid for tid, s in self.status.items() if s == st]
                print(f"   {st:8}: {counts[st]} 个 {ids}")
        total = len(self.status)
        print(f"   完成度: {counts[SUCCESS]}/{total}")


def main():
    dag = DEMO_DAG
    layers = parallel_layers(dag["tasks"])

    print("Planner 输出的任务图:")
    for t in dag["tasks"]:
        dep = f" ← {t['depends_on']}" if t["depends_on"] else ""
        print(f"   {t['id']} [{t['type']}] {t['action']}{dep}")
    print(f"\n并行分层: {layers}")

    # 场景 A:全部成功
    print("\n\n########## 场景 A:正常执行(全部成功) ##########")
    MockExecutor(dag, max_retry=2, fail_ids=set()).run(layers)

    # 场景 B:T2(认证)第一次失败 → 重试成功,不影响下游
    print("\n\n########## 场景 B:T2 偶发失败 → 单步重试成功 ##########")
    MockExecutor(dag, max_retry=2, fail_ids={"T2"}).run(layers)

    # 场景 C:T3 彻底失败(重试用尽)→ 其下游 T6 被跳过
    print("\n\n########## 场景 C:T3 彻底失败 → 下游 T6 跳过 ##########")
    # 让 T3 两次都失败:把 max_retry 设 1,fail_ids 含 T3
    MockExecutor(dag, max_retry=1, fail_ids={"T3"}).run(layers)


if __name__ == "__main__":
    main()
