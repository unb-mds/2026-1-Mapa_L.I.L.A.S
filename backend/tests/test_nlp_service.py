import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.nlp_service import get_dynamic_keywords

@patch.dict(os.environ, {"USE_MOCK_IA": "true"})
def test_get_dynamic_keywords_mock_mode():
    seeds = ["feminicídio", "violência doméstica"]
    result = get_dynamic_keywords(seeds)
    assert isinstance(result, list)
    assert len(result) > 0
    assert "mock_keyword_1" in result

@patch.dict(os.environ, {"USE_MOCK_IA": "false", "GEMINI_API_KEY": "fake_key"})
@patch('app.services.nlp_service.genai.Client')
def test_get_dynamic_keywords_success(mock_client_class):
    mock_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '["direitos da mulher", "lei maria da penha"]'
    mock_instance.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_instance

    seeds = ["direitos da mulher"]
    result = get_dynamic_keywords(seeds)

    assert isinstance(result, list)
    assert result == ["direitos da mulher", "lei maria da penha"]
    mock_instance.models.generate_content.assert_called_once()

@patch.dict(os.environ, {"USE_MOCK_IA": "false", "GEMINI_API_KEY": "fake_key"})
@patch('app.services.nlp_service.genai.Client')
def test_get_dynamic_keywords_fallback(mock_client_class):
    mock_instance = MagicMock()
    mock_instance.models.generate_content.side_effect = Exception("Gemini API is down")
    mock_client_class.return_value = mock_instance

    seeds = ["feminicídio", "violência doméstica"]
    result = get_dynamic_keywords(seeds)

    assert result == seeds
    mock_instance.models.generate_content.assert_called_once()
