from .context import build_context
from .providers.openai_adapter import OpenAIAdapter


def _provider(provider=None):
    return provider or OpenAIAdapter()


def suggest_edit_plan(project, provider=None) -> str:
    return _provider(provider).complete("Suggest a practical edit plan for this project.", build_context(project))


def suggest_social_caption(project, provider=None) -> str:
    return _provider(provider).complete("Suggest a social caption for this project.", build_context(project))


def suggest_ai_video_brief(project, provider=None) -> str:
    return _provider(provider).complete("Suggest an AI video brief for this project.", build_context(project))
