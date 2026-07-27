def get_mask_card_number(card: str) -> str:
    """Функция принимает на вход номер карты и возвращает его маску."""
    alpha = "".join(char for char in card if not char.isdigit())
    return f"{alpha} {card[-16:-12]} {card[-12:-10]}{"**"} {"****"} {card[-4:]}"

def get_mask_account(card: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску."""
    number = 2
    return f"Счет {'*' * number}{card.replace(' ', '')[-4:]}"


#print(get_mask_card_number("7000792289606361"))
#print(get_mask_account("73654108430135874305"))
