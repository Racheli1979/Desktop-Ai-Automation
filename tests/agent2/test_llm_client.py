from unittest.mock import patch

import pytest

from agent2_meeting_agent import llm_client


SERVICE_NAME = "DesktopAiAutomation"
OPENAI_KEY_NAME = "openai_api_key"


def test_create_llm_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        llm_client.keyring,
        "get_password",
        lambda service, username: None,
    )

    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        llm_client.create_llm()


def test_create_llm_uses_default_model(monkeypatch):
    monkeypatch.setattr(
        llm_client.keyring,
        "get_password",
        lambda service, username: "test-key",
    )

    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    with patch.object(llm_client, "ChatOpenAI") as mock_chat:
        llm_client.create_llm()

        mock_chat.assert_called_once_with(
            model="gpt-4.1-mini",
            api_key="test-key",
        )


def test_create_llm(monkeypatch):
    monkeypatch.setattr(
        llm_client.keyring,
        "get_password",
        lambda service, username: "test-key",
    )

    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    with patch.object(llm_client, "ChatOpenAI") as mock_chat:
        llm_client.create_llm()

        mock_chat.assert_called_once_with(
            model="test-model",
            api_key="test-key",
        )


def test_get_api_key_uses_saved_key(monkeypatch):
    monkeypatch.setattr(
        llm_client.keyring,
        "get_password",
        lambda service, username: "test-key",
    )

    assert llm_client.get_api_key() == "test-key"


def test_get_api_key_requires_configuration(monkeypatch):
    monkeypatch.setattr(
        llm_client.keyring,
        "get_password",
        lambda service, username: None,
    )

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        llm_client.get_api_key()