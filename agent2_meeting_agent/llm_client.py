import os

import keyring
from langchain_openai import ChatOpenAI


SERVICE_NAME = "DesktopAiAutomation"
OPENAI_KEY_NAME = "openai_api_key"


def get_api_key() -> str:
    api_key = keyring.get_password(
        SERVICE_NAME,
        OPENAI_KEY_NAME,
    )

    if not api_key:
        raise ValueError(
            "OpenAI API key is not configured. "
            "Run the application setup first."
        )

    return api_key


def create_llm() -> ChatOpenAI:
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )

    return ChatOpenAI(
        model=model,
        api_key=get_api_key(),
    )