import os

from .local_stub import LocalAssistantStub


class OpenAIAdapter:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self._client = None

    def _get_client(self):
        if not self.api_key:
            return None
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def complete(self, prompt: str, context: dict | None = None) -> str:
        client = self._get_client()
        if client is None:
            return LocalAssistantStub().complete(prompt, context)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are the RinoVision creator pipeline assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""
