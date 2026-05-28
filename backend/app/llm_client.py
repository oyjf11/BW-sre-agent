"""LLM Client for AI-powered nodes."""
import os
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, List

# Load .env file if exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

logger = logging.getLogger(__name__)


def _get_llm_provider() -> str:
    """Re-read LLM_PROVIDER from os.getenv (supports hot reload)."""
    return os.getenv("LLM_PROVIDER", "minimax").lower()


LLM_PROVIDER = _get_llm_provider()


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        group_id: Optional[str] = None,
    ):
        try:
            from app.core.config import get_settings
            settings = get_settings()
            # OpenAI config
            self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
            self.model = model or settings.openai_model
            # MiniMax config
            self.minimax_api_key = settings.minimax_api_key or os.getenv("MINIMAX_API_KEY", "")
            self.minimax_group_id = group_id or settings.minimax_group_id or os.getenv("MINIMAX_GROUP_ID", "")
            self.minimax_model = settings.minimax_model
            # DeepSeek config
            self.deepseek_api_key = settings.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY", "")
            self.deepseek_model = settings.deepseek_model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.deepseek_api_base = "https://api.deepseek.com"
        except Exception:
            # Fallback to env vars if settings are unavailable (e.g., during tests)
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
            self.minimax_api_key = os.getenv("MINIMAX_API_KEY", "")
            self.minimax_group_id = group_id or os.getenv("MINIMAX_GROUP_ID", "")
            self.minimax_model = os.getenv("MINIMAX_MODEL", "abab6.5s-chat")
            self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
            self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.deepseek_api_base = "https://api.deepseek.com"
        self.minimax_api_base = "https://api.minimax.chat/v1"
    
    async def complete(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate completion from prompt."""
        
        provider = _get_llm_provider()
        if provider == "minimax":
            return await self._minimax_complete(prompt, system_prompt, temperature, max_tokens)
        elif provider == "deepseek":
            return await self._deepseek_complete(prompt, system_prompt, temperature, max_tokens)
        else:
            return await self._openai_complete(prompt, system_prompt, temperature, max_tokens)
    
    async def _minimax_complete(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call MiniMax API directly."""
        if not self.minimax_api_key or not self.minimax_group_id:
            logger.warning("MiniMax API key or group ID not configured")
            return self._fallback_complete(prompt, system_prompt)
        
        url = f"{self.minimax_api_base}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.minimax_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"MiniMax API error: {resp.status} - {error_text}")
                        return self._fallback_complete(prompt, system_prompt)
                    
                    result = await resp.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.info(f"MiniMax response: {content[:100]}...")
                    return content
        except Exception as e:
            logger.error(f"MiniMax call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)
    
    async def _openai_complete(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call OpenAI API directly."""
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return self._fallback_complete(prompt, system_prompt)
        
        from langchain_openai import ChatOpenAI
        
        try:
            llm = ChatOpenAI(model=self.model, api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("user", prompt))
            
            response = await llm.agenerate([messages])
            content = response.generations[0][0].text
            logger.info(f"OpenAI response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)
    
    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Generate completion and parse as JSON."""
        full_prompt = f"{prompt}\n\nRespond in valid JSON format only."
        response = await self.complete(full_prompt, system_prompt, temperature)
        
        try:
            import re
            for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
                match = re.search(pattern, response)
                if match:
                    return json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
        
        return {}
    
    def _fallback_complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Fallback when no API key available."""
        logger.warning("Using LLM fallback response")
        return "fallback_response"

    async def _deepseek_complete(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call DeepSeek API (OpenAI-compatible)."""
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured")
            return self._fallback_complete(prompt, system_prompt)

        url = f"{self.deepseek_api_base}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.deepseek_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"DeepSeek API error: {resp.status} - {error_text}")
                        return self._fallback_complete(prompt, system_prompt)
                    result = await resp.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.info(f"DeepSeek response: {content[:100]}...")
                    return content
        except Exception as e:
            logger.error(f"DeepSeek call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)

    def _deepseek_complete_sync(
        self, prompt: str, system_prompt: Optional[str], temperature: float
    ) -> str:
        """Synchronous DeepSeek API call."""
        import requests

        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured")
            return self._fallback_complete(prompt, system_prompt)

        url = f"{self.deepseek_api_base}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.deepseek_model,
            "messages": messages,
            "temperature": temperature,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code != 200:
                logger.error(f"DeepSeek API error: {resp.status_code} - {resp.text}")
                return self._fallback_complete(prompt, system_prompt)
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"DeepSeek response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"DeepSeek sync call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)
    
    def complete_sync(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Synchronous LLM call using requests."""
        provider = _get_llm_provider()
        if provider == "minimax":
            return self._minimax_complete_sync(prompt, system_prompt, temperature)
        elif provider == "deepseek":
            return self._deepseek_complete_sync(prompt, system_prompt, temperature)
        else:
            return self._openai_complete_sync(prompt, system_prompt, temperature)
    
    def _minimax_complete_sync(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Synchronous MiniMax API call using requests."""
        import requests
        
        if not self.minimax_api_key or not self.minimax_group_id:
            logger.warning("MiniMax API key or group ID not configured")
            return self._fallback_complete(prompt, system_prompt)
        
        url = f"{self.minimax_api_base}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.minimax_model,
            "messages": messages,
            "temperature": temperature,
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code != 200:
                logger.error(f"MiniMax API error: {resp.status_code} - {resp.text}")
                return self._fallback_complete(prompt, system_prompt)
            
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"MiniMax response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"MiniMax call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)
    
    def _openai_complete_sync(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Synchronous OpenAI API call via requests."""
        import requests

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Set LLM_PROVIDER=minimax to use MiniMax instead, "
                "or provide OPENAI_API_KEY."
            )

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code != 200:
                logger.error(f"OpenAI API error: {resp.status_code} - {resp.text}")
                return self._fallback_complete(prompt, system_prompt)

            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"OpenAI response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"OpenAI sync call failed: {e}")
            return self._fallback_complete(prompt, system_prompt)


llm_client = LLMClient()


def reload_llm_client():
    """Hot-reload the LLM client singleton with updated .env settings."""
    from app.core.config import clear_settings_cache

    clear_settings_cache()
    load_dotenv(env_path, override=True)
    global llm_client
    llm_client = LLMClient()
    logger.info("LLM client reloaded successfully")
