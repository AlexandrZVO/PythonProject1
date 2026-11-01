import json
from unittest.mock import patch

from src.main import load_json


def test_handles_missing_amount_key_in_json():
    """Тест: если в JSON нет ключа amount, сумма становится 0.0."""
    raw_data = [
        {"id": 101, "state": "New"},  # Нет amount
        {"id": 102, "amount": 250.75, "state": "Done"},  # Есть amount
    ]

    json_string = json.dumps(raw_data)

    # Чистый способ мока через with
    with patch("builtins.open") as mock_open:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = json_string

        result = load_json("dummy.json")

    assert len(result) == 2
    # Первая запись: amount не было -> safe_float вернёт 0.0
    assert result[0]["operationAmount"]["amount"] == 0.0
    # Вторая запись: всё ок
    assert result[1]["operationAmount"]["amount"] == 250.75


def test_handles_invalid_json_format():
    """Тест: битый JSON не ломает программу, возвращает []."""
    broken_json = '[{"id": 1, "amount": 100}'  # Синтаксическая ошибка

    with patch("builtins.open") as mock_open:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = broken_json

        result = load_json("dummy.json")

    assert result == []
