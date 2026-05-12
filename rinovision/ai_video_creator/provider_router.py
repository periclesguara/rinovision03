from rinovision.core.pipeline import transition

from .providers.local_stub import LocalStubVideoProvider
from .providers.openai_video import OpenAIVideoProvider


def get_provider(provider_name: str = "local_stub", dry_run: bool = True):
    if provider_name == "local_stub":
        return LocalStubVideoProvider()
    if provider_name == "openai_video":
        return OpenAIVideoProvider(dry_run=dry_run)
    raise ValueError(f"unknown AI video provider: {provider_name}")


def select_provider(project, provider_name: str = "local_stub", dry_run: bool = True):
    provider = get_provider(provider_name, dry_run=dry_run)
    if project.status == "AI_PROMPTS_CREATED":
        transition(project, "AI_PROVIDER_SELECTED")
    return provider
