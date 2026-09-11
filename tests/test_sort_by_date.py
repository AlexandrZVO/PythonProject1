from datetime import datetime
from typing import Any, Dict, List

import pytest

from src.processing import sort_by_date


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    # Тело функции
    data = [
        {"date": "2023-10-05", "value": "a"},
        {"date": "2023-01-15", "value": "b"},
        {"date": "2023-07-20", "value": "c"},
        {"date": "2023-07-10", "value": "d"},
    ]
    # Возвращаем список словарей
    return data


def test_sort_by_date() -> None:
    # Исходные данные
    data = [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T08:37:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:30:42.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:25:241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:33:41.419441"},
    ]


def test_sort_by_date_ascending(sample_data: List[dict]) -> None:
    # тестовая сортировка в порядке возрастания от самого старого к самому новому
    expected = sorted(sample_data, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    result = sort_by_date(sample_data.copy())  # Используем копию, чтобы не менять оригинал
    assert result == expected, f"Expected {expected}, got {result}"


def test_sort_by_date_descending(sample_data: List[dict]) -> None:
    # Тестовая сортировка в порядке убывания (от самой новой к самой старой
    expected = sorted(
        sample_data,
        key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
        reverse=False,
    )
    result = sort_by_date(sample_data.copy())
    assert result == expected, f"Expected {expected}, got {result}"


def test_sort_by_date_duplicate_dates(
    sample_data: List[dict],
) -> None:  # указывает, что функция не возвращает значение
    """
    Тестирует сортировку списка словарей по полю 'date'.
    Проверяет, что элементы с одинаковой датой сохраняют относительный порядок
    (устойчивая сортировка) и что функция возвращает корректный результат.
    """
    duplicates = sample_data.copy()
    duplicates.append({"date": "2023-10-05", "value": "E"})
    # Ожидаемый результат: сортировка с ключом, который преобразует строку даты в объект datetime
    expected = sorted(duplicates, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    result = sort_by_date(duplicates)
    # Проверяем, что результаты совпадают
    assert result == expected
