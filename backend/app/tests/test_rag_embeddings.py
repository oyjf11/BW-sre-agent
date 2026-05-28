from app.rag.embeddings import get_embedding_model_name


def test_get_embedding_model_name_uses_config_default():
    assert get_embedding_model_name() == "BAAI/bge-small-zh-v1.5"
