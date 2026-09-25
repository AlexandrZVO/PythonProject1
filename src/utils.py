"""Модуль для работы с файлами транзакций."""

import json
import logging
from typing import Any, Dict, List

# Получаем логгер по имени.
# ВАЖНО: Хендлер и формат уже настроены в main.py при старте.
logger = logging.getLogger("utils")


def load_transactions(path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON-файла."""
    try:
        logger.info("load_transactions: попытка загрузки файла. path=%s", path)

        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            logger.warning(
                "load_transactions: неверный формат данных. Ожидался список, получено %s. path=%s",
                type(data).__name__,
                path,
            )
            return []

        count = len(data)
        logger.info("load_transactions: успех. Загружено транзакций: %d. path=%s", count, path)
        return data

    except FileNotFoundError:
        # Ошибочный случай: уровень ERROR
        logger.error("load_transactions: файл не найден. path=%s", path, exc_info=True)
        return []

    except json.JSONDecodeError as e:
        # Ошибочный случай: уровень ERROR
        logger.error("load_transactions: ошибка декодирования JSON. path=%s, error=%s", path, e, exc_info=True)
        return []

    except Exception as e:
        # Любой другой сбой: уровень ERROR
        logger.error(
            "load_transactions: непредвиденная ошибка. path=%s, error=%s",
            path,
            e,
            exc_info=True,
        )
        return []
