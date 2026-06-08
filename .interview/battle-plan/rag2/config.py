"""
rag2 目录统一配置
=================
优先级：.env 文件 > 环境变量 > 默认值
"""

import os
from pathlib import Path

_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

EMBED_MODEL = "text-embedding-v4"
EMBED_DIM = 1024

LLM_MODEL = "qwen-plus"
LLM_TEMPERATURE = 0.2

RERANK_MODEL = os.getenv("RERANK_MODEL", "gte-rerank")