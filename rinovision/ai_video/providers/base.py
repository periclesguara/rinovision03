from abc import ABC, abstractmethod


class AIVideoProvider(ABC):
    @abstractmethod
    def create_request(self, prompts: list[dict]) -> dict:
        raise NotImplementedError

    @abstractmethod
    def submit(self, request: dict) -> dict:
        raise NotImplementedError
