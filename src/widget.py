from datetime import datetime


def mask_account_card(card: str) -> str:
    # Ваш код здесь
    digits = "".join(
        [char for char in card if char.isdigit() and not char.isspace()]
    )  # извлекает все цифры из строки card и собирает их в одну новую строку
    if card == "":
        return "None"
    if "Счет" in card:
        number = 2
        return f"Счет {'**' + digits[-4:]}"
    if not ("Счёт" in card) and len(str(digits)) == 16:
        alpha = "".join(char for char in card if not char.isdigit())  # удаляет все цифры  из строки card
        return f"{alpha}{digits[-16:-12]} {digits[-12:-10]}{"**"} {"****"} {digits[-4:]}"
    if not digits or len(str(digits)) != 16:
        return "неверный формат карты"
    return ""


print(mask_account_card(""))
print(mask_account_card("Visa Classic 683198247677658"))
print(mask_account_card("Visa Classic 683 1982 4767 37658"))
print(mask_account_card("Visa Gold 599941 4228426353"))
print(mask_account_card("Maestro 159683786 8705199"))
print(mask_account_card("MasterCard 7158 300734726758"))
print(mask_account_card("Счет-1234-5678-90"))
print(mask_account_card("4556364607935616"))
print(mask_account_card("Счет 646864  7367889ccc4779  589"))


from datetime import datetime


def get_date(date_str: str) -> str:
    """Функция преобразует дату в формат 'DD.MM.YYYY'"""
    if date_str == "":
        return "None"
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        return parsed_date.strftime("%d.%m.%Y")
    except ValueError:
        return "неверный формат даты"


print(get_date("2024-03-11T02:26:18.671407"))
print(get_date("2025-06-20T15:30:45.123456"))
print(get_date("2025-13-04"))
print(get_date(""))
