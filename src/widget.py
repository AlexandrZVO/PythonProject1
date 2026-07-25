from datetime import datetime


def mask_account_card(card: str) -> str:
    """Функция принимает на вход номер карты или счет и возвращает его маску."""
    digits = "".join(filter(str.isdigit, str(card)))
    masked_digits = digits[:4] + " " + digits[4:6] + "**" + " " + "****" + " " + digits[-4:]
    if not digits.isdigit() or len(digits) < 4:
        return "INVALID"
    if "Visa Platinum" in card:
        return f"Visa Platinum {masked_digits}"
    if "Visa Gold" in card:
        return f"Visa Gold {masked_digits}"
    if "Visa Classic" in card:
        return f"Visa Classic {masked_digits}"
    if "Maestro" in card:
        return f"Maestro {masked_digits}"
    if "MasterCard" in card:
        return f"MasterCard {masked_digits}"
    if "Счет" in card:
        masked_digits = "**" + digits[-4:]
    return f"Счет {masked_digits}"


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
