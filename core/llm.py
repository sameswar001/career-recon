"""LLM provider factory.

Provider is swappable via the LLM_PROVIDER env var (anthropic | openai |
ollama), defaulting to ollama for free, local iteration during
development. Swapping to a cloud provider for the actual interview demo
is a one-line env var change, not a code change — every node calls
get_llm() rather than importing a specific provider's client directly.
"""

import os

from langchain.chat_models import init_chat_model

DEFAULT_MODELS = {
    "ollama": "llama3.1",
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o-mini",
}


def get_llm():
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODELS[provider])
    return init_chat_model(model, model_provider=provider)
