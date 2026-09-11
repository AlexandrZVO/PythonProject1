from datetime import datetime

import pytest

from src.processing import sort_by_date


@pytest.fixture
def sample_data():
    return [
        {"date": "2023-10-05", "value": "A"},
        {"date": "2023-01-15", "value": "B"},
        {"date": "2023-07-20", "value": "C"},
        {"date": "2023-07-10", "value": "D"},
    ]


def test_sort_by_date():
    # Исходные данные
    data = [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T08:37:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:30:42.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:25:241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:33:41.419441"},
    ]


def test_sort_by_date_ascending(sample_data):
    """тестовая сортировка в порядке возрастания от самого старого к самому новому."""
    expected = sorted(
        sample_data, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
    )
    result = sort_by_date(
        sample_data.copy()
    )  # Используем копию, чтобы не менять оригинал
    assert result == expected, f"Expected {expected}, got {result}"


def test_sort_by_date_descending(sample_data):
    """Тестовая сортировка в порядке убывания (от самой новой к самой старой)."""
    expected = sorted(
        sample_data,
        key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
        reverse=False,
    )
    result = sort_by_date(sample_data.copy())
    assert result == expected, f"Expected {expected}, got {result}"


def test_sort_by_date_duplicate_dates(sample_data):
    """Тестовая сортировка, если несколько элементов имеют одинаковую дату."""
    duplicates = sample_data.copy()
    duplicates.append({"date": "2023-10-05", "value": "E"})
    expected = sorted(
        duplicates, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
    )
    result = sort_by_date(duplicates)
    assert result == expected
