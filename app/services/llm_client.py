import json
import re
from typing import Dict, Optional

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings


class ModelClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_answer(
        self,
        messages: list,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict:
        if self.settings.openai_api_key and not self.settings.mock_mode:
            return self._invoke_real_model(messages, model_name or self.settings.default_model, temperature, max_tokens)
        return self._invoke_mock_model(messages, model_name or "mock-search-qa-model")

    def judge_answer(
        self,
        judge_prompt: str,
        model_name: Optional[str] = None,
    ) -> Dict:
        if self.settings.openai_api_key and not self.settings.mock_mode and self.settings.enable_llm_judge:
            messages = [("system", "You are an impartial LLM evaluation judge."), ("human", judge_prompt)]
            result = self._invoke_real_model(messages, model_name or self.settings.default_model, 0.0, 512)
            return {"mode": "llm_judge", "raw_output": result["text"]}
        return {
            "mode": "mock_llm_judge",
            "raw_output": "Mock judge placeholder. Enable OPENAI_API_KEY and set MOCK_MODE=false to call a real judge model.",
        }

    def _invoke_real_model(
        self,
        messages: list,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict:
        llm = ChatOpenAI(
            model=model_name,
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response = llm.invoke(messages)
        return {"mode": "real", "text": response.content}

    def _invoke_mock_model(self, messages: list, model_name: str) -> Dict:
        rendered = "\n".join([getattr(message, "content", str(message)) for message in messages])
        lower_text = rendered.lower()

        answer = self._extract_first_hint(rendered, ["参考答案：", "参考答案:", "Reference answer:"])
        context = self._extract_first_hint(rendered, ["上下文：", "上下文:", "Context:"])
        if not answer:
            answer = self._first_sentence(context) if context else "根据当前提供的信息，暂时无法安全回答这个问题。"
        if "bullet" in lower_text or "要点" in rendered:
            answer = "- 回答：{answer}\n- 证据：{evidence}".format(
                answer=answer,
                evidence=self._first_sentence(context) if context else "上下文不足。",
            )
        elif "json" in lower_text or "json" in rendered.lower():
            payload = {
                "answer": answer,
                "evidence": self._first_sentence(context) if context else "上下文不足。",
            }
            answer = json.dumps(payload, ensure_ascii=False)
        elif ("insufficient" in lower_text and "context" in lower_text) or ("上下文不足" in rendered):
            if not context:
                answer = "当前上下文不足，无法给出可靠回答。"

        return {
            "mode": "mock",
            "model_name": model_name,
            "text": answer,
        }

    @staticmethod
    def _extract_first_hint(text: str, markers: list) -> str:
        for marker in markers:
            extracted = ModelClient._extract_hint(text, marker)
            if extracted:
                return extracted
        return ""

    @staticmethod
    def _extract_hint(text: str, marker: str) -> str:
        if marker not in text:
            return ""
        content = text.split(marker, 1)[1]
        stops = [
            "\n类别：", "\n类别:", "\nCategory:",
            "\n难度：", "\n难度:", "\nDifficulty:",
            "\n标签：", "\n标签:", "\nTags:",
            "\n备注：", "\n备注:", "\nNotes:",
            "\n\n", "\n回答", "\nAnswer",
        ]
        for stop in stops:
            if stop in content:
                content = content.split(stop, 1)[0]
        return content.strip()

    @staticmethod
    def _first_sentence(text: str) -> str:
        if not text:
            return ""
        parts = re.split(r"[。！？.!?]", text)
        for part in parts:
            if part.strip():
                return part.strip()
        return text.strip()
