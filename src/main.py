"""Точка входа в приложение."""

import logging
from logging import FileHandler, Formatter
from pathlib import Path

from external_api import convert_to_rub
from utils import load_transactions


# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = Formatter(fmt=log_format, datefmt=date_format)

    # Логгер utils
    utils_logger = logging.getLogger("utils")
    utils_logger.setLevel(logging.DEBUG)
    utils_handler = FileHandler("logs/utils.log", mode="w", encoding="utf-8")
    utils_handler.setLevel(logging.DEBUG)
    utils_handler.setFormatter(formatter)
    if not utils_logger.handlers:
        utils_logger.addHandler(utils_handler)

    # Логгер masks
    masks_logger = logging.getLogger("masks")
    masks_logger.setLevel(logging.DEBUG)
    masks_handler = FileHandler("logs/masks.log", mode="w", encoding="utf-8")
    masks_handler.setLevel(logging.DEBUG)
    masks_handler.setFormatter(formatter)
    if not masks_logger.handlers:
        masks_logger.addHandler(masks_handler)


setup_logging()


if __name__ == "__main__":
    main_logger = logging.getLogger("main")
    main_logger.info("Приложение запущено. Начинаем обработку транзакций.")

    transactions = load_transactions("data/operations.json")

    if not transactions:
        print("️ Файл пуст или не найден.")
    else:
        print(f" Загружено транзакций: {len(transactions)}\n")

        for tx in transactions:
            amount_data = tx.get("operationAmount", {})
            amount = float(amount_data.get("amount", 0))
            currency_data = amount_data.get("currency", {})
            currency = currency_data.get("code", "RUB")

            tx_id = tx.get("id", "?")
            description = tx.get("description", "Без описания")

            try:
                rub = convert_to_rub(amount, currency)

                if rub > 0:
                    print(f" #{tx_id} {description}: {amount} {currency} → {rub} RUB")
                else:
                    msg = f" #{tx_id} {description}: не удалось конвертировать (результат <= 0)"
                    print(msg)
                    # Даже если результат 0, это не ошибка сети, но можно залогировать как предупреждение
                    main_logger.warning(msg)

            except Exception as e:
                # ВОТ ЗДЕСЬ ТЕПЕРЬ ЛОГИРУЕМ ОШИБКУ В ФАЙЛ
                # exc_info=True добавит полный стек ошибки (включая тот самый 429)
                main_logger.error("Ошибка конвертации для транзакции %s (%s): %s", tx_id, currency, e, exc_info=True)
                print(f" #{tx_id} {description}: ошибка конвертации (см. лог для деталей)")
