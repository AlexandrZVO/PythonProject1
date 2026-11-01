import pytest
import requests  # <--- ЭТА СТРОКА БЫЛА ЗАБЫТА, ОНА РЕШАЕТ ПРОБЛЕМУ
from unittest.mock import patch, MagicMock
from src.external_api import get_exchange_rate, convert_to_rub


@patch("src.external_api.os.getenv")
def test_get_exchange_rate_no_api_key(mock_getenv):
    """Тест: API_KEY не найден в .env"""
    mock_getenv.return_value = None
    result = get_exchange_rate("USD")
    assert result == 0.0


@patch("src.external_api.os.getenv")
@patch("src.external_api.requests.get")
def test_get_exchange_rate_network_error(mock_get, mock_getenv):
    """Тест: Ошибка сети (ConnectionError, Timeout)"""
    mock_getenv.return_value = "fake_key"
    # Теперь эта строка сработает, так как мы импортировали requests
    mock_get.side_effect = requests.exceptions.ConnectionError("Network down")

    result = get_exchange_rate("USD")
    assert result == 0.0


@patch("src.external_api.os.getenv")
@patch("src.external_api.requests.get")
def test_get_exchange_rate_http_error(mock_get, mock_getenv):
    """Тест: Сервер вернул ошибку (404, 500)"""
    mock_getenv.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 500
    # Теперь эта строка сработает
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    mock_get.return_value = mock_response

    result = get_exchange_rate("USD")
    assert result == 0.0


@patch("src.external_api.os.getenv")
@patch("src.external_api.requests.get")
def test_get_exchange_rate_missing_result_field(mock_get, mock_getenv):
    """Тест: В ответе API нет поля 'result'"""
    mock_getenv.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_field": 123}
    mock_get.return_value = mock_response

    result = get_exchange_rate("USD")
    assert result == 0.0


@patch("src.external_api.os.getenv")
@patch("src.external_api.requests.get")
def test_get_exchange_rate_invalid_conversion(mock_get, mock_getenv):
    """Тест: Ошибка преобразования в float (ValueError)"""
    mock_getenv.return_value = "fake_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "not_a_number"}
    mock_get.return_value = mock_response

    result = get_exchange_rate("USD")
    assert result == 0.0


@patch("src.external_api.get_exchange_rate")
def test_convert_to_rub_same_currency(mock_get_rate):
    """Тест: Конвертация RUB в RUB"""
    result = convert_to_rub(100.5, "RUB")
    assert result == 100.5


@patch("src.external_api.get_exchange_rate")
def test_convert_to_rub_success(mock_get_rate):
    """Тест: Успешная конвертация валюты"""
    mock_get_rate.return_value = 90.5
    result = convert_to_rub(100, "USD")
    assert result == 9050.0


@patch("src.external_api.get_exchange_rate")
def test_convert_to_rub_zero_rate(mock_get_rate):
    """Тест: Если курс вернулся 0.0"""
    mock_get_rate.return_value = 0.0
    result = convert_to_rub(100, "USD")
    assert result == 0.0
