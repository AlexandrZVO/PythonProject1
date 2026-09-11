def get_mask_card_number(card_number: str) -> str:
    # Убеждаемся, что на вход пришла строка
    digits = "".join(char for char in card_number if char.isdigit())  # Убираем всё, кроме цифрZ
    if len(digits) != 16:
        return digits
    card_str = str(digits)
    # Извлекаем первые 6 цифр и последние 4
    first_six = card_str[:6]
    last_four = card_str[-4:]
    #  Создаём маску: первые 6 цифр + (** для 2 цифр + 4 звездочки) + последние 4
    masked = f"{first_six[:4]} {first_six[4:6]}** **** {last_four}"
    return masked


def get_mask_account(card: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску."""
    number = 2
    # return f"Счет {'*' * number}{card.replace(' ', '')[-4:]}"
    return f"{'*' * number}{card.replace(' ', '')[-4:]}"


# print(get_mask_card_number("123456g781 2345678"))
print(get_mask_account("73654108430135874305"))
# print(get_mask_card_number("12345"))
# print(get_mask_card_number("123a4567-8901-20345"))
# print(get_mask_card_number("1234 567812345 678"))
# print(get_mask_card_number("1234567812345678"))
print(get_mask_account("7000792  289606361"))
print(get_mask_account("73654108430135874305  "))
print(get_mask_account("1" * 20))
print(get_mask_account("Visa Platinum 7000792289606361"))
print(get_mask_account("Счет 64686473678894779589"))
print(get_mask_account("Visa Gold 5999414228426353"))
print(get_mask_account("Maestro 1596837868705199"))
