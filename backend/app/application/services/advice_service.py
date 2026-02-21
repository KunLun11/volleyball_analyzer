from dataclasses import dataclass
from datetime import datetime

from app.application.services.context_builder import ContextBuilder
from app.application.services.prompt_templates import PromptTemplates
from app.config import Settings, settings
from app.domain.entities.matches import Match
from app.infrastructure.external.llm_client import LLMClient
from app.infrastructure.external.ollama_client import OllamaClient


@dataclass
class Advice:
    text: str
    generated_at: datetime


class AdviceService:
    def __init__(
        self,
        llm_client: LLMClient,
        context_builder: ContextBuilder,
        prompt_templates: PromptTemplates,
        config: Settings,
    ):
        self._llm = llm_client
        self._context_builder = context_builder
        self._prompt_templates = prompt_templates

    async def build(self, match: Match) -> Advice:
        context = await self._context_builder.build(match)
        prompt = self._prompt_templates.get(context)
        try:
            response = await self._llm.generate(prompt)
            advice_text = self._clean_response(response)
        except Exception:
            advice_text = self._fallback_advice(context)

        return Advice(text=advice_text, generated_at=datetime.now())

    def _clean_response(self, text: str) -> str:
        text = text.replace("Совет тренера:", "").replace("совет тренера:", "")
        text = text.strip(" \"'")
        if text:
            text = text[0].upper() + text[1:]
        if text and not text.endswith((".", "!", "?")):
            text += "."
        return text

    def _fallback_advice(self, context: dict) -> str:
        score_a = context["score_a"]
        score_b = context["score_b"]
        diff = abs(score_a - score_b)
        situation = context.get("situation", "normal")

        if situation == "match_point":
            return "Матч-бол! Сосредоточьтесь на подаче."
        if situation == "deuce":
            return "Равный счет. Играйте внимательно, не рискуйте."
        if situation == "set_point":
            return "Сет-бол! Подавайте в дальнюю зону."
        if diff >= 5 and score_a > score_b:
            return "Ведите с разрывом. Не сбавляйте темп."
        if diff >= 5 and score_a < score_b:
            return "Возьмите тайм-аут и соберитесь."
        if diff <= 2:
            return "Игра равная. Держите концентрацию."
        return "Продолжайте в том же духе!"
