"""Settings API — LLM configuration management with hot-reload."""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

_LLM_KEYS = {
    "LLM_PROVIDER",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "MINIMAX_API_KEY",
    "MINIMAX_GROUP_ID",
    "MINIMAX_MODEL",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_MODEL",
}

_PROVIDER_REQUIRED = {
    "openai": ["openai_api_key"],
    "minimax": ["minimax_api_key", "minimax_group_id"],
    "deepseek": ["deepseek_api_key"],
}


class LlmConfig(BaseModel):
    provider: str = Field(default="minimax", description="LLM provider: openai | minimax | deepseek")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    minimax_api_key: str = Field(default="", description="MiniMax API key")
    minimax_group_id: str = Field(default="", description="MiniMax group ID")
    minimax_model: str = Field(default="abab6.5s-chat", description="MiniMax model name")
    deepseek_api_key: str = Field(default="", description="DeepSeek API key")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek model name")


def _read_env_file() -> Dict[str, str]:
    if not _ENV_PATH.exists():
        return {}
    result = {}
    with open(_ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)\s*$", line)
            if m:
                result[m.group(1)] = m.group(2)
    return result


def _write_env_file(updates: Dict[str, str]) -> None:
    current = _read_env_file()
    current.update(updates)

    lines = []
    seen: set = set()
    if _ENV_PATH.exists():
        with open(_ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=", stripped) if stripped else None
                key = m.group(1) if m else ""
                if key in _LLM_KEYS:
                    if key in updates:
                        lines.append(f"{key}={updates[key]}\n")
                        seen.add(key)
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

    for key, value in updates.items():
        if key not in seen:
            lines.append(f"{key}={value}\n")

    with open(_ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    logger.info(f"Updated .env with LLM settings: {list(updates.keys())}")


@router.get("/llm", response_model=LlmConfig)
async def get_llm_config():
    current = _read_env_file()
    return LlmConfig(
        provider=current.get("LLM_PROVIDER", "minimax"),
        openai_api_key=current.get("OPENAI_API_KEY", ""),
        openai_model=current.get("OPENAI_MODEL", "gpt-4o"),
        minimax_api_key=current.get("MINIMAX_API_KEY", ""),
        minimax_group_id=current.get("MINIMAX_GROUP_ID", ""),
        minimax_model=current.get("MINIMAX_MODEL", "abab6.5s-chat"),
        deepseek_api_key=current.get("DEEPSEEK_API_KEY", ""),
        deepseek_model=current.get("DEEPSEEK_MODEL", "deepseek-chat"),
    )


@router.put("/llm", response_model=Dict[str, Any])
async def update_llm_config(config: LlmConfig):
    provider = config.provider.lower()
    if provider not in ("openai", "minimax", "deepseek"):
        raise HTTPException(status_code=400, detail="provider must be 'openai', 'minimax', or 'deepseek'")

    required_keys = _PROVIDER_REQUIRED.get(provider, [])
    for rk in required_keys:
        val = getattr(config, rk, "")
        if not val:
            raise HTTPException(status_code=400, detail=f"{rk.upper()} is required for provider={provider}")

    updates = {
        "LLM_PROVIDER": provider,
        "OPENAI_API_KEY": config.openai_api_key,
        "OPENAI_MODEL": config.openai_model,
        "MINIMAX_API_KEY": config.minimax_api_key,
        "MINIMAX_GROUP_ID": config.minimax_group_id,
        "MINIMAX_MODEL": config.minimax_model,
        "DEEPSEEK_API_KEY": config.deepseek_api_key,
        "DEEPSEEK_MODEL": config.deepseek_model,
    }

    _write_env_file(updates)

    from dotenv import load_dotenv
    load_dotenv(_ENV_PATH, override=True)

    from app.llm_client import reload_llm_client
    reload_llm_client()

    return {
        "status": "ok",
        "message": f"LLM config updated. Provider: {provider}. Hot-reload applied.",
        "provider": provider,
    }
