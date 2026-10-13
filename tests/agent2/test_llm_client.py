import pytest

from agent2_meeting_agent import llm_client


def test_create_llm_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )

    with pytest.raises(ValueError):
        llm_client.create_llm()


def test_create_llm_requires_model(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    with pytest.raises(ValueError):
        llm_client.create_llm()


def test_create_llm(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )

    model = llm_client.create_llm()

    assert model is not None
    assert model.model_name == "test-model"