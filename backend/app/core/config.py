"""Application configuration - Twelve-Factor App compliant."""

import os
from enum import Enum
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from functools import lru_cache


class AppEnv(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OpsPilot"
    app_version: str = "0.1.0"
    debug: bool = False

    app_env: AppEnv = AppEnv.DEV

    # LLM provider selection: "minimax" | "openai"
    llm_provider: str = "minimax"

    # OpenAI settings (only required when llm_provider=openai)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    llm_timeout: int = 60
    llm_max_retries: int = 3

    # MiniMax settings (only required when llm_provider=minimax)
    minimax_api_key: str = ""
    minimax_group_id: str = ""
    minimax_model: str = "abab6.5s-chat"

    # DeepSeek settings (only required when llm_provider=deepseek)
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite+aiosqlite:///./opspilot.db"

    http_timeout: int = 30
    sse_timeout: int = 300

    cors_origins: List[str] = ["*"]

    tool_adapter_mode: str = "mock"

    # MySQL settings (for aliyun real adapter)
    mysql_host: str = ""
    mysql_port: int = 3306
    mysql_user: str = ""
    mysql_password: str = ""
    mysql_db: str = ""
    mysql_pool_size: int = 5
    mysql_readonly: bool = True

    # Kubernetes settings (for aliyun real adapter)
    k8s_config_path: str = ""
    k8s_context: str = ""
    k8s_allowed_namespaces: List[str] = []

    # Alibaba Cloud SLB settings (for aliyun real adapter)
    alibaba_access_key_id: str = ""
    alibaba_access_key_secret: str = ""
    alibaba_region_id: str = "cn-hangzhou"

    # Alibaba Cloud OSS settings (for OSS adapter)
    alibaba_oss_bucket: str = ""
    alibaba_oss_endpoint: str = ""

    # Alibaba Cloud CMS / K8s metrics
    k8s_cluster_id: str = ""

    log_level: str = "INFO"

    rag_enabled: bool = False
    rag_persist_dir: str = "./storage/chroma"
    rag_collection_name: str = "opspilot_knowledge"
    rag_embedding_model: str = "BAAI/bge-small-zh-v1.5"
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 80
    rag_runbook_dir: str = "./knowledge/runbooks"
    rag_top_k: int = 5
    rag_enable_reranker: bool = False

    tracing_provider: str = "local"
    tracing_project: str = "opspilot"
    tracing_base_url: str = ""
    tracing_public_base_url: str = ""
    langsmith_api_key: str = ""
    langsmith_endpoint: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = ""

    def validate_for_production(self):
        """Fail-fast validation for production environment."""
        errors = []

        if self.app_env == AppEnv.PROD:
            if self.cors_origins == ["*"]:
                errors.append("CORS=* is not allowed in production")

            if self.tool_adapter_mode == "mock":
                errors.append("Mock executor is not allowed in production")

            if self.debug:
                errors.append("debug=True is not allowed in production")

        # LLM provider-specific key validation (non-dev only)
        if self.app_env != AppEnv.DEV:
            if self.llm_provider == "openai" and not self.openai_api_key:
                errors.append("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
            elif self.llm_provider == "minimax" and (
                not self.minimax_api_key or not self.minimax_group_id
            ):
                errors.append(
                    "MINIMAX_API_KEY and MINIMAX_GROUP_ID are required when LLM_PROVIDER=minimax"
                )
            elif self.llm_provider == "deepseek" and not self.deepseek_api_key:
                errors.append(
                    "DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek"
                )

            tracing_provider = self.tracing_provider.lower()
            if tracing_provider == "langsmith":
                if not self.langsmith_api_key:
                    errors.append("LANGSMITH_API_KEY is required when TRACING_PROVIDER=langsmith")
            if tracing_provider == "langfuse":
                if not self.langfuse_public_key or not self.langfuse_secret_key:
                    errors.append(
                        "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are required when "
                        "TRACING_PROVIDER=langfuse"
                    )

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_for_production()
    return settings

def clear_settings_cache():
    """Clear cached settings so next call re-reads .env."""
    get_settings.cache_clear()
