from abc import ABC, abstractmethod


class AssistantProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, context: dict | None = None) -> str:
        raise NotImplementedError
