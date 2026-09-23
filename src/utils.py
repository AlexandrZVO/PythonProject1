"""Модуль для работы с файлами транзакций."""

import json
from typing import Any


def load_transactions(path: str) -> list[dict[str, Any]]:
    """Загружает транзакции из JSON-файла.

    Args:
        path: Путь до JSON-файла.

    Returns:
        Список словарей с транзакциями.
        Если файл пустой, не найден или содержит не список — пустой список.
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return data
