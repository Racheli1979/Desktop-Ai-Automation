import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def create_llm() -> ChatOpenAI:

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured"
        )

    if not model:
        raise ValueError(
            "OPENAI_MODEL is not configured"
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
    )