import pytest

from src.widget import mask_account_card


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ("", "None"),  # Отсутствует номер
        ("683198247677658", "неверный формат карты"),  # неверный формат карты
        ("Счет 1234567890", "Счет **7890"),  # Короткий номер счет
        ("Счет   1234 5678 90", "Счет **7890"),  # Пробелы игнорируются
        ("Счет-1234-5678-90", "Счет **7890"),  # Другой формат
        ("1234567890123456", "1234 56** **** 3456"),  # Карта без имени
        ("4556364607935616", "4556 36** **** 5616"),
        (
            "Visa Classic 6831982476737658",
            "Visa Classic 6831 98** **** 7658",
        ),  # Карта без пробелов
    ],
)
def test_mask_account_card(input_data: str, expected: str) -> None:
    assert mask_account_card(input_data) == expected
