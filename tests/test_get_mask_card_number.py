import pytest

from src.masks import get_mask_card_number


def test_get_mask_card_number():
    # Тест корректного номера
    assert (
        get_mask_card_number("1234567812345678") == "1234 56** **** 5678"
    ), "Некорректная маскировка для 16-значного номера"

    # Тест с номером, содержащим пробелы
    assert (
        get_mask_card_number("12 345 678 12345 678") == "1234 56** **** 5678"
    ), "Некорректная маскировка с пробелами"

    # Тест с номером с нецифровыми символами
    assert (
        get_mask_card_number("123a4567-8901-23245") == "1234 56** **** 3245"
    ), "Некорректная маскировка с нецифровыми символами"

    # Тест с пустым значением
    try:
        get_mask_card_number(None)
    except TypeError:
        # Если функция должна корректно обрабатывать None, тест должен пройти
        pass
    else:
        assert False, "Функция должна raise TypeError для None"


def test_get_mask_card_number_len_card():
    # Тест, если не 16 номеров.
    assert (
        get_mask_card_number("123456789123456789") == "123456789123456789"
    ), "Некорректная длина номера крты"
