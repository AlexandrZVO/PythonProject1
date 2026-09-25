"""Модуль маскировки номеров карт и счетов."""

import logging
from logging import FileHandler, Formatter
from pathlib import Path

# Папка logs создаётся в корне проекта
Path("logs").mkdir(exist_ok=True)

# Создан отдельный объект логера для модуля masks
logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)  # уровень не меньше DEBUG

# Настроен file_handler: лог перезаписывается при каждом запуске (mode="w")
file_handler = FileHandler("logs/masks.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Настроен file_formatter: время, имя модуля, уровень, сообщение
file_formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Установлен форматер для handler
file_handler.setFormatter(file_formatter)
# Добавлен handler для логера
logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str:
    """Принимает номер карты и возвращает его маску."""
    try:
        if not isinstance(card_number, str):
            raise TypeError(f"Ожидалась строка, получен {type(card_number).__name__}")

        digits = "".join(char for char in card_number if char.isdigit())

        if len(digits) != 16:
            logger.warning("Некорректная длина номера карты: %d символов", len(digits))
            return digits

        first_six = digits[:6]
        last_four = digits[-4:]
        masked = f"{first_six[:4]} {first_six[4:6]}** **** {last_four}"

        # Логирование успешного случая
        logger.info("Маска карты создана: %s", masked)
        return masked

    except Exception as e:
        # Логирование ошибочного случая: уровень не ниже ERROR
        logger.error(
            "Ошибка в get_mask_card_number: %s, вход: %r",
            e,
            card_number,
            exc_info=True,
        )
        return digits


def get_mask_account(card: str) -> str:
    """Принимает номер счета и возвращает его маску."""
    try:
        if not isinstance(card, str):
            raise TypeError(f"Ожидалась строка, получен {type(card).__name__}")

        clean_card = card.replace(" ", "")

        if len(clean_card) < 4:
            logger.warning("Номер счета слишком короткий: %d символов", len(clean_card))
            return clean_card

        masked = f"**{clean_card[-4:]}"

        # Логирование успешного случая
        logger.info("Маска счета создана: %s", masked)
        return masked

    except Exception as e:
        logger.error(
            "Ошибка в get_mask_account: %s, вход: %r",
            e,
            card,
            exc_info=True,
        )
        return card.replace(" ", "")


print(get_mask_account("7000792  289606361"))
print(get_mask_account("73654108430135874305  "))
print(get_mask_account("1" * 20))
print(get_mask_account("Visa Platinum 7000792289606361"))
print(get_mask_account("Счет 64686473678894779589"))
print(get_mask_account("Visa Gold 5999414228426353"))
print(get_mask_account("Maestro 1596837868705199"))
