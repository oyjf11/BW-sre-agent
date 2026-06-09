最短路径：

cd /Users/ouyangjinfeng/sre-agent/.interview/battle-plan/rag2

# 1. 装依赖（dashscope 当前 python 还没装）

pip install dashscope numpy

# 2. 配 key —— 阿里云 DashScope 申请 https://dashscope.console.aliyun.com/

# .env 已经存在,把你的 key 写进去

echo 'DASHSCOPE_API_KEY=sk-你的 key' > .env

# 或者临时 export:

# export DASHSCOPE_API_KEY=sk-xxx

# 3a. 跑 RAG 评测(A/B/C 三路 + 实验报告四件套)

python rag_eval.py

# 3b. 跑完整 Router→Planner 链路(会额外调 qwen-plus 做规划)

python router_planner.py

# 3c. 跑 Executor mock(消费手写 DAG,不调任何 API,纯本地)

python mock_executor.py

会调用的 API 和费用提醒

- rag_eval.py：embedding（text-embedding-v4，1 次建库 24 条 + 每条 case 3 次 query × 10 case
  = 30 次） + rerank（gte-rerank，每条 case 1 次 × 10 = 10 次）。整体几分钱量级。
- router_planner.py：上面那套再加 qwen-plus 生成（每个测试 query 1 次），单次几毛钱。
- mock_executor.py：不调 API，可以白嫖随便跑。

.env 已存在但被 gitignore，文件内容格式：
DASHSCOPE_API_KEY=sk-xxxx
等号两边别留空格，config.py 是按 split("=", 1) 解析的。

跑出来长啥样：参考我上面那段 OFFLINE_LOGIC_OK 的输出——真实 dashscope
跑出来会是同样的四件套排版，但归因 pp 是真数字（mock 那个是桩数据演示）。
