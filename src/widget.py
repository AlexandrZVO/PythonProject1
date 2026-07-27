from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(card: str) -> str:
    """Функция принимает на вход номер карты,счета и возвращает его маску."""
    if "Счет" in card:
        return get_mask_account(card)
    else:
        return get_mask_card_number(card)


print(mask_account_card("Visa Platinum 7000792289606361"))
print(mask_account_card("Visa Classic 6831982476737658"))
print(mask_account_card("Visa Gold 5999414228426353"))
print(mask_account_card("Maestro 1596837868705199"))
print(mask_account_card("MasterCard 7158300734726758"))
print(mask_account_card("Счет 73654108430135874305"))
print(mask_account_card("Счет 64686473678894779589"))


def get_date(date_str: str) -> str:
    """Функция преобразует дату в формат 'DD.MM.YYYY'"""
    parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    return parsed_date.strftime("%d.%m.%Y")


print(get_date("2024-03-11T02:26:18.671407"))
