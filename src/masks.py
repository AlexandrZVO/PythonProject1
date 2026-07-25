def get_mask_card_number(card, number=4):
    """Функция принимает на вход номер карты и возвращает его маску."""
    return f"{card.replace(' ', '')[0:4]} {card.replace(' ', '')[4:6]}** {'*' * number} {card.replace(' ', '')[-4:]}"


def get_mask_account(card, number=2):
    """Функция принимает на вход номер счета и возвращает его маску."""
    return f"{'*' * number}{card.replace(' ', '')[-4:]}"


print(get_mask_card_number("7000792289606361"))
print(get_mask_account("73654108430135874305"))
