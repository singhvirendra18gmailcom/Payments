from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.services import gemini_service
from app.services.gemini_service import GeminiService


def make_service(mock_client: Mock) -> GeminiService:
    with patch.object(gemini_service.genai, "Client", return_value=mock_client):
        return GeminiService()


def test_init_creates_gemini_client_with_api_key():
    mock_client = Mock()

    with patch.object(gemini_service.genai, "Client", return_value=mock_client) as client:
        service = GeminiService()

    client.assert_called_once_with(api_key=gemini_service.GEMINI_API_KEY)
    assert service.client == mock_client
    assert service.model == gemini_service.GEMINI_MODEL


def test_init_raises_error_when_api_key_missing():
    with patch.object(gemini_service, "GEMINI_API_KEY", ""):
        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            GeminiService()


def test_ask_returns_response_text():
    mock_client = Mock()
    mock_client.models.generate_content.return_value = SimpleNamespace(
        text="MT103 is a SWIFT customer credit transfer."
    )
    service = make_service(mock_client)

    result = service.ask("What is MT103?")

    assert result == "MT103 is a SWIFT customer credit transfer."
    mock_client.models.generate_content.assert_called_once()


def test_ask_raises_validation_error_for_empty_question():
    service = make_service(Mock())

    with pytest.raises(ValueError, match="Question cannot be empty"):
        service.ask("   ")


def test_ask_returns_fallback_message_when_response_has_no_text():
    mock_client = Mock()
    mock_client.models.generate_content.return_value = SimpleNamespace(text="")
    service = make_service(mock_client)

    result = service.ask("Explain pacs.008")

    assert result == "AI could not generate a response. Please try again."


def test_ask_raises_unavailable_error_when_api_fails():
    mock_client = Mock()
    mock_client.models.generate_content.side_effect = RuntimeError("API failed")
    service = make_service(mock_client)

    with pytest.raises(
        RuntimeError,
        match="AI service is currently unavailable. Please try again later.",
    ):
        service.ask("Explain MT103")


def test_health_check_returns_true_when_model_responds():
    mock_client = Mock()
    mock_client.models.generate_content.return_value = SimpleNamespace(text="OK")
    service = make_service(mock_client)

    assert service.health_check() is True


def test_health_check_returns_false_when_api_fails():
    mock_client = Mock()
    mock_client.models.generate_content.side_effect = RuntimeError("API failed")
    service = make_service(mock_client)

    assert service.health_check() is False
