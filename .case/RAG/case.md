环境安装
pip install llama-index chromadb sentence-transformers
pip install llama-index-embeddings-huggingface
pip install llama-index-vector-stores-chroma
pip install llama-index-postprocessor-flag-embedding-reranker

完整实现代码（分步讲解）

# rag_system.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb

# ===== 步骤 1：配置嵌入模型 =====

# BGE-small-zh：免费、本地运行、支持中文、效果好

# 首次运行会自动下载模型（约 130MB）

Settings.embed_model = HuggingFaceEmbedding(
model_name="BAAI/bge-small-zh-v1.5"
)

# 分块配置：chunk_size 控制每块大小，chunk_overlap 控制相邻块重叠

# 重叠是为了避免信息在分块边界处被截断丢失

Settings.node_parser = SentenceSplitter(
chunk_size=512, # 每块约 512 个 token（约 400-600 个中文字）
chunk_overlap=50 # 前后各 50 个 token 重叠，防止信息断层
)

# ===== 步骤 2：初始化向量数据库 =====

# ChromaDB：数据持久化到本地 ./chroma_db 文件夹

db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("my_knowledge_base")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# ===== 步骤 3：加载文档并构建索引 =====

# SimpleDirectoryReader 自动识别目录中的文档格式

# 支持：PDF、Word、Markdown、TXT、HTML 等

print("正在加载文档并构建索引，首次运行较慢...")
documents = SimpleDirectoryReader(
"./docs", # 把你的文档放在这个文件夹里
recursive=True # 递归扫描子文件夹
).load_data()
print(f"加载了 {len(documents)} 个文档片段")

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
documents,
storage_context=storage_context,
show_progress=True # 显示进度条
)
print("索引构建完成！")

# ===== 步骤 4：配置重排序器 =====

# 先召回 20 个候选，重排序后取 Top5，大幅提升精准度

reranker = FlagEmbeddingReranker(
model="BAAI/bge-reranker-base",
top_n=5 # 最终保留 5 个最相关片段
)

# ===== 步骤 5：构建查询引擎 =====

query_engine = index.as_query_engine(
similarity_top_k=20, # 向量检索召回 Top20 候选
node_postprocessors=[reranker], # 重排序精选 Top5
response_mode="compact" # 压缩模式：自动合并相关信息
)

# ===== 步骤 6：查询测试 =====

def ask(question):
print(f"
问题：{question}")
response = query_engine.query(question)
print(f"回答：{response.response}")
print("
参考来源：")
for i, node in enumerate(response.source_nodes):
print(f" [{i+1}] {node.metadata.get('file_name', '未知')} "
f"（相关度: {node.score:.3f}）")
return response

ask("公司的年假政策是什么？")
ask("如何申请报销？需要哪些材料？")

反幻觉核心 Prompt
这个 Prompt 是 RAG 系统中最重要的设计之一，让大模型只基于检索到的内容回答：

# 在 query_engine 配置中加入这个 Prompt

from llama_index.core import PromptTemplate

ANTI_HALLUCINATION_PROMPT = PromptTemplate(
"""你是企业内部知识库助手。请严格基于以下检索到的文档内容回答问题。

规则（必须遵守）：

1. 只回答文档中明确记载的内容，不要推断或编造
2. 每个关键信息点必须标注来源（格式：[来源：文件名]）
3. 如果文档中没有相关信息，直接回答"文档中暂无相关记录"
4. 不要在答案中混入文档以外的知识

参考文档：
{context_str}

用户问题：{query_str}

请基于以上文档内容回答："""
)

# 设置自定义 Prompt

query_engine = index.as_query_engine(
similarity_top_k=20,
node_postprocessors=[reranker],
text_qa_template=ANTI_HALLUCINATION_PROMPT # 使用反幻觉 Prompt
)
