import pytest
from unittest.mock import patch
from io import StringIO
from src.main import load_csv


# Класс убираем совсем!

def test_converts_invalid_csv_amount_to_zero():
    """Тест: мусор становится 0.0, нормальные числа парсятся."""
    # ВАЖНО: разделитель ;, как в функции load_csv
    csv_data = """id;amount;state
101;N/A;New
102;500.50;Done"""

    fake_file = StringIO(csv_data)

    with patch('builtins.open', return_value=fake_file):
        result = load_csv("dummy.csv")

    assert len(result) == 2
    assert result[0]["operationAmount"]["amount"] == 0.0
    assert result[1]["operationAmount"]["amount"] == 500.5


def test_load_csv_returns_empty_list_on_missing_file():
    """Тест: если файла нет, возвращаем [] и не крашимся."""
    with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
        result = load_csv("non_existent_file.csv")

    assert result == []


def test_load_csv_handles_invalid_id_gracefully():
    """Тест: даже если id не число, мы всё равно парсим строку и не падаем."""
    csv_data = """id;amount;state
bad_id;100.00;Done
102;200.50;New"""

    fake_file = StringIO(csv_data)

    with patch('builtins.open', return_value=fake_file):
        result = load_csv("dummy.csv")

    # Мы не должны упасть. ID может быть строкой, это ок.
    assert len(result) == 2
    assert result[0]["operationAmount"]["amount"] == 100.0
    assert result[1]["operationAmount"]["amount"] == 200.5

def test_load_csv_returns_empty_list_on_missing_file():
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = load_csv("non_existent.csv")
    assert result == []

