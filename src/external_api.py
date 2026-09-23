"""Модуль для конвертации валют через API Apilayer."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("APILAYER_API_KEY", "")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"
HEADERS = {"apikey": API_KEY}


def get_exchange_rate(from_currency: str, to_currency: str = "RUB") -> float:
    """Получает курс валюты через API Apilayer."""
    if not API_KEY:
        print(" Ошибка: API_KEY не найден в .env")
        return 0.0

    params = {"from": from_currency, "to": to_currency, "amount": str(1)}  # <-- Важно: mypy любит строки в params

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("result")
        if result is None:
            print(f" Поле 'result' не найдено в ответе API для {from_currency}")
            return 0.0
        return float(result)
    except requests.exceptions.RequestException as exc:
        print(f" Ошибка запроса к API: {exc}")
        return 0.0
    except (ValueError, TypeError) as exc:
        print(f" Ошибка преобразования курса: {exc}")
        return 0.0


def convert_to_rub(amount: float, currency: str) -> float:
    """Конвертирует сумму в рубли по текущему курсу."""
    if currency.upper() == "RUB":
        return round(float(amount), 2)

    rate = get_exchange_rate(currency, "RUB")
    if rate == 0.0:
        return 0.0
    return round(amount * rate, 2)
