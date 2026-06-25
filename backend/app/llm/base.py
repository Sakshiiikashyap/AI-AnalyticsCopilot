from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, max_output_tokens: int = 1024) -> str:
        raise NotImplementedError