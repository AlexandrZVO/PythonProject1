# import pytest

from src.processing import filter_by_state


def test_filter_by_state_default() -> None:
    """Тестовая фильтрация по состоянию 'EXECUTED'."""
    store = [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:25:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:25:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]
    expected = [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:25:58.425572"},
    ]
    assert filter_by_state(store) == expected


def test_filter_by_state_custom_state() -> None:
    """Тестовая фильтрация по пользовательскому состоянию."""
    store = [
        {"id": 1, "state": "PENDING"},
        {"id": 2, "state": "PROCESSED"},
        {"id": 3, "state": "EXECUTED"},
    ]
    expected = [{"id": 2, "state": "PROCESSED"}]
    assert filter_by_state(store, state="PROCESSED") == expected


def test_filter_by_state_missing_key() -> None:
    """Тест на отсутствие ключа при фильтрации по состоянию"""
    store = [{"id": 1, "date": "2019-07-03T18:35:29.512364"}]
    expected: list[str] = []  # элемент без `state` не должен попасть в результат
    assert filter_by_state(store) == expected


def test_filter_by_state_none_value() -> None:
    """Функция, которая проверяет корректность фильтрации объектов по значению None в поле state"""
    store = [{"state": None}, {"state": "EXECUTED"}]
    expected = [{"state": "EXECUTED"}]
    assert filter_by_state(store, state="EXECUTED") == expected
