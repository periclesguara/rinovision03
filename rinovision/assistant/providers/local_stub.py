from .base import AssistantProvider


class LocalAssistantStub(AssistantProvider):
    def complete(self, prompt: str, context: dict | None = None) -> str:
        return f"[local_stub] {prompt}"
