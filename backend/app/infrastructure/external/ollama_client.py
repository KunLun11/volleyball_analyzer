import asyncio
import logging

import httpx

from app.infrastructure.external.exceptions import LLMError
from app.infrastructure.external.llm_client import LLMClient

logger = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str, timeout: float, max_retries: int):
        self._base_url = base_url
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)

    async def generate(self, prompt: str) -> str:
        for attempt in range(self._max_retries):
            try:
                response = await self._client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 200,
                        },
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["response"].strip()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
        raise LLMError(f"Failed after {self._max_retries} attempts")

    async def health(self) -> bool:
        try:
            response = await self._client.get(f"{self._base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except:
            return False

    async def ensure_model(self) -> bool:
        if not await self.health():
            logger.warning("Ollama not available")
            return False
        response = await self._client.get(f"{self._base_url}/api/tags")
        models = response.json().get("models", [])
        for model in models:
            if self._model in model["name"]:
                return True
        logger.info(f"Pulling model: {self._model}")
        await self._pull_model()
        return True

    async def _pull_model(self):
        try:
            await self._client.post(
                f"{self._base_url}/api/pull", json={"name": self._model}
            )
            logger.info(f"Model {self._model} pulled successfully")
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")


class OpenAIClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float,
        max_retries: int,
        max_tokens: int = 200,
    ):
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"
        self._base_url = base_url
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._max_tokens = max_tokens
        self._client = httpx.AsyncClient(timeout=timeout)

    async def generate(self, prompt: str) -> str:
        for attempt in range(self._max_retries):
            try:
                response = await self._client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Ты опытный тренер по волейболу.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": self._max_tokens,
                        "top_p": 0.9,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    # Извлекаем текст ответа
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    logger.warning(
                        f"API error: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # exponential backoff
        raise LLMError(f"Failed after {self._max_retries} attempts")

    async def health(self) -> bool:
        try:
            response = await self._client.get(
                f"{self._base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=2.0,
            )
            return response.status_code == 200
        except:
            return False
