# import pytest

from src.masks import get_mask_account


def test_get_mask_account() -> None:
    # Стандартные случаи
    assert get_mask_account("12345678901234567890") == "**7890", "Пример с длинной строкой"
    assert get_mask_account("1234") == "**1234", "Пример с короткой строкой (ровно 4 цифры)"
    assert get_mask_account("123") == "**123", "Пример с очень короткой строкой"

    # Разные форматы (с лишними пробелами)
    assert get_mask_account("1 234 5678") == "**5678", "Пример с пробелами"
    assert get_mask_account("  1234  5678  ") == "**5678", "Пример с пробелами по краям"

    # Слишком длинный (для демонстрации гибкости)
    assert get_mask_account("1" * 20) == "**1111", "Пример с очень длинным числом"
