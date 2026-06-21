import google.generativeai as genai

from app.core.config import settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._model.generate_content(
            [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["Understood. I will answer strictly from the provided data context."]},
                {"role": "user", "parts": [user_prompt]},
            ],
            generation_config={"temperature": 0.2, "max_output_tokens": 1024},
        )
        return response.text