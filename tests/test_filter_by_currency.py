import re

import pytest

from src.generators import (card_number_generator, filter_by_currency,
                            transaction_descriptions)

transactions = [
    {
        "id": 939719570,
        "state": "EXECUTED",
        "date": "2018-06-30T02:08:58.425572",
        "operationAmount": {
            "amount": "9824.07",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод организации",
        "from": "Счет 75106830613657916952",
        "to": "Счет 11776614605963066702",
    },
    {
        "id": 142264268,
        "state": "EXECUTED",
        "date": "2019-04-04T23:20:05.206878",
        "operationAmount": {
            "amount": "79114.93",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод со счета на счет",
        "from": "Счет 19708645243227258542",
        "to": "Счет 75651667383060284188",
    },
    {
        "id": 873106923,
        "state": "EXECUTED",
        "date": "2019-03-23T01:09:46.296404",
        "operationAmount": {
            "amount": "43318.34",
            "currency": {"name": "руб.", "code": "RUB"},
        },
        "description": "Перевод со счета на счет",
        "from": "Счет 44812258784861134719",
        "to": "Счет 74489636417521191160",
    },
    {
        "id": 895315941,
        "state": "EXECUTED",
        "date": "2018-08-19T04:27:37.904916",
        "operationAmount": {
            "amount": "56883.54",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод с карты на карту",
        "from": "Visa Classic 6831982476737658",
        "to": "Visa Platinum 8990922113665229",
    },
    {
        "id": 594226727,
        "state": "CANCELED",
        "date": "2018-09-12T21:27:25.241689",
        "operationAmount": {
            "amount": "67314.70",
            "currency": {"name": "руб.", "code": "RUB"},
        },
        "description": "Перевод организации",
        "from": "Visa Platinum 1246377376343588",
        "to": "Счет 14211924144426031657",
    },
]


@pytest.fixture
def usd_transactions() -> list:  # или collections.abc.Iterator, в зависимости от реализации
    return filter_by_currency(transactions, "USD")


def test_filter_by_currency_usd(usd_transactions) -> None:
    # Проверяем, что генератор корректно возвращает элементы
    usd_transactions = list(filter_by_currency(transactions, "USD"))
    assert len(usd_transactions) == 3  # или другое ожидаемое количество


def test_filter_by_currency_no_matching_transactions() -> None:
    # Прверяем, если при запросе валюта EUR
    assert len(list(filter_by_currency(transactions, "EUR"))) == 0


def test_filter_by_currency_no_such_currency() -> None:
    # Проверяем, что генератор корректно обрабатывает несуществующую валюту
    no_currency = filter_by_currency(transactions, "XXX")
    assert next(no_currency, None) is None  # Не должно быть элементов


def test_filter_by_currency_missing(usd_transactions) -> None:
    # Тест: валюты нет в транзакциях
    result = list(filter_by_currency(usd_transactions, "GBP"))
    assert len(result) == 0  # Итератор пустой — ошибок нет


def test_filter_by_currency_empty() -> None:
    # Тест, создаём пустой список
    usd_transactions = []
    result = list(filter_by_currency(usd_transactions, "USD"))
    assert len(result) == 0


def test_transaction_descriptions_empty_list() -> None:
    # Тест, пустой список
    empty_transactions = []
    result = list(transaction_descriptions(empty_transactions))
    assert result == []


def test_transaction_descriptions_order() -> None:
    # Тест,описания должны возвращаться в правильном порядке
    transactions = [
        {"description": "Перевод организации"},
        {"description": "Перевод со счета на счет"},
        {"description": "Перевод с карты на карту"},
    ]
    expected = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод с карты на карту",
    ]
    result = list(transaction_descriptions(transactions))
    assert result == expected, f"Ожидался порядок {expected}, получен {result}"


# Тесты
def test_pattern_mode_single_value() -> None:
    """Тест с граничной максимальной границей: 9999 -> 9999 9999 9999 9999"""
    gen_max = card_number_generator(9999, 9999, mode="pattern")
    assert next(gen_max) == "9999 9999 9999 9999", "Некорректно сгенерирован номер для 9999 в режиме pattern"
    with pytest.raises(StopIteration):
        next(gen_max)


def test_sequential_mode_small_range() -> None:
    """Проверка классического режима"""
    gen = card_number_generator(1, 3, mode="sequential")
    assert next(gen) == "0000 0000 0000 0001"
    assert next(gen) == "0000 0000 0000 0002"
    assert next(gen) == "0000 0000 0000 0003"
    with pytest.raises(StopIteration):
        next(gen)


def test_invalid_range() -> None:
    """Проверка ошибки при start > stop"""
    with pytest.raises(ValueError):
        list(card_number_generator(10, 5))


def test_card_format_consistency() -> None:
    """
    Проверяет корректность форматирования номеров карт.
    Критерии:
    1. Общая длина строки ровно 19 символов (16 цифр + 3 пробела).
    2. Формат строго XXXX XXXX XXXX XXXX.
    3. В каждом блоке ровно 4 цифры.
    4. Между блоками ровно один пробел.
    5. Нет лишних символов, букв или дефисов.
    """

    # Тестируем оба режима на разных диапазонах
    test_cases = [
        {"start": 1, "stop": 3, "mode": "sequential"},
        {"start": 9990, "stop": 9995, "mode": "pattern"},
        {"start": 5, "stop": 5, "mode": "sequential"},
        {"start": 7, "stop": 7, "mode": "pattern"},
    ]

    for case in test_cases:
        start, stop, mode = case["start"], case["stop"], case["mode"]
        gen = card_number_generator(start, stop, mode=mode)

        for card_number in gen:
            # 1. Проверка длины строки
            assert len(card_number) == 19, f"Неверная длина номера '{card_number}' (ожидается 19). Режим: {mode}"

            # 2. Проверка формата через регулярное выражение
            # ^ - начало строки, \d{4} - 4 цифры, ( \d{4}){3} - еще три группы "пробел+4цифры", $ - конец строки
            pattern = r"^\d{4} \d{4} \d{4} \d{4}$"
            assert re.match(
                pattern, card_number
            ), f"Неверный формат номера '{card_number}'. Ожидается XXXX XXXX XXXX XXXX. Режим: {mode}"

            # 3. Дополнительная проверка: убедимся, что там только цифры и пробелы
            assert all(
                c.isdigit() or c == " " for c in card_number
            ), f"В номере '{card_number}' найдены недопустимые символы. Режим: {mode}"
