"""Точка входа в приложение."""

import csv
import json
import re
import logging
from logging import FileHandler, Formatter
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List, Optional

# Для XLSX понадобится openpyxl: pip install openpyxl
try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None


# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = Formatter(fmt=log_format, datefmt=date_format)

    for logger_name in ("utils", "masks"):
        current_logger = logging.getLogger(logger_name)
        current_logger.setLevel(logging.DEBUG)
        if not current_logger.handlers:
            handler = FileHandler(f"logs/{logger_name}.log", mode="w", encoding="utf-8")
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            current_logger.addHandler(handler)


setup_logging()


# --- Конвертация валют без запросов к API ---
RATES_TO_RUB: Dict[str, float] = {
    "RUB": 1.0,
    "USD": 90.0,
    "EUR": 100.0,
    "GBP": 115.0,
    "CNY": 12.5,
}


def convert_to_rub(amount: float, currency_code: str) -> float:
    """Конвертирует сумму в рубли. Неизвестную валюту не роняет, а возвращает сумму как есть."""
    code = str(currency_code or "").strip().upper()
    if code in RATES_TO_RUB:
        return round(amount * RATES_TO_RUB[code], 2)
    return round(amount, 2)


def safe_float(value: Optional[Any]) -> float:
    """Универсальная защита: превращает что угодно в float или 0.0"""
    if value is None:
        return 0.0
    try:
        clean_val = str(value).strip().replace(",", ".")
        return float(clean_val)
    except (ValueError, TypeError):
        return 0.0


def load_json(path: str) -> List[Dict[str, Any]]:
    """
    Загружает JSON и приводит транзакции к единому формату.
    Поддерживает оба формата:
    1. вложенный: {"id", "state", "date", "description", "operationAmount": {"amount", "currency": {"name", "code"}}}
    2. плоский:   {"id", "state", "date", "description", "amount", "currency_code", "currency_name"}
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("JSON должен содержать список транзакций")
            return []

        transactions: List[Dict[str, Any]] = []

        for row in data:
            if not isinstance(row, dict):
                continue

            amount_data = row.get("operationAmount") or {}
            currency_data = amount_data.get("currency") or {}

            # Берём вложенный формат, если он есть; иначе — плоские поля
            raw_amount = amount_data.get("amount", row.get("amount"))
            currency_code = currency_data.get("code", row.get("currency_code", "UNK"))
            currency_name = currency_data.get("name", row.get("currency_name", "Неизвестно"))

            tx: Dict[str, Any] = {
                "id": row.get("id"),
                "state": row.get("state", "Unknown") or "Unknown",
                "date": row.get("date") or "",
                "description": row.get("description", "Без описания") or "Без описания",
                "operationAmount": {
                    "amount": safe_float(raw_amount),
                    "currency": {
                        "name": currency_name or "Неизвестно",
                        "code": str(currency_code or "UNK").upper(),
                    },
                },
            }
            transactions.append(tx)

        return transactions

    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Невалидный JSON: {e}")
        return []
    except Exception as e:
        print(f"Ошибка чтения JSON: {e}")
        return []


def load_csv(path: str) -> List[Dict[str, Any]]:
    """Загружает CSV с разделителем ';' и нормализует суммы."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            transactions: List[Dict[str, Any]] = []

            for row in reader:
                tx: Dict[str, Any] = {
                    "id": row.get("id"),
                    "state": row.get("state"),
                    "date": row.get("date"),
                    "description": row.get("description", "Без описания"),
                    "operationAmount": {
                        "amount": safe_float(row.get("amount")),
                        "currency": {
                            "name": row.get("currency_name", "Неизвестно"),
                            "code": row.get("currency_code", "UNK"),
                        },
                    },
                }
                transactions.append(tx)

            return transactions

    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        return []
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return []


def load_xlsx(path: str) -> List[Dict[str, Any]]:
    if load_workbook is None:
        print("Библиотека openpyxl не установлена. Установите её: pip install openpyxl")
        return []

    try:
        # data_only=True важно, чтобы брать значения из формул, а не сами формулы
        wb = load_workbook(filename=path, data_only=True)
        ws = wb.active

        if ws is None:
            print("В файле нет активных листов.")
            return []

        transactions: List[Dict[str, Any]] = []

        # Заголовки из первой строки
        header_row = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1), [])]
        headers = [str(h).strip().lower() if h is not None else "" for h in header_row]

        def get_col_index(*names: str) -> Optional[int]:
            for name in names:
                if name in headers:
                    return headers.index(name)
            return None

        idx_id = get_col_index("id")
        idx_state = get_col_index("state", "status")
        idx_date = get_col_index("date")
        idx_amount = get_col_index("amount")
        idx_currency_code = get_col_index("currency_code", "code")
        idx_description = get_col_index("description")

        if idx_id is None or idx_amount is None:
            print("Не найдены обязательные колонки (id, amount). Проверьте структуру XLSX.")
            return []

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or all(cell is None for cell in row):
                continue

            def cell_value(idx: Optional[int], default: Any = "") -> Any:
                if idx is None or idx >= len(row):
                    return default
                return row[idx] if row[idx] is not None else default

            raw_id = cell_value(idx_id, None)
            raw_state = cell_value(idx_state, "")
            raw_date = cell_value(idx_date, "")
            raw_amount = cell_value(idx_amount, 0)
            raw_currency = cell_value(idx_currency_code, "UNK")
            raw_desc = cell_value(idx_description, "Без описания")

            tx: Dict[str, Any] = {
                "id": raw_id,
                "state": str(raw_state).strip() if raw_state else "",
                "date": str(raw_date).strip() if raw_date else "",
                "description": str(raw_desc).strip(),
                "operationAmount": {
                    "amount": safe_float(raw_amount),
                    "currency": {
                        "name": "Неизвестно",
                        "code": str(raw_currency).strip().upper() if raw_currency else "UNK",
                    },
                },
            }
            transactions.append(tx)

        return transactions

    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        return []
    except Exception as e:
        print(f"Ошибка чтения XLSX: {e}")
        return []


def search_operations(transactions: List[Dict], search_string: str) -> List[Dict]:
    """Поиск по описанию с использованием re (регистронезависимо)."""
    if not search_string:
        return transactions
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    return [op for op in transactions if pattern.search(str(op.get("description", "")))]


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    target = status.strip().upper()
    valid_statuses = {"EXECUTED", "CANCELED", "PENDING"}

    if target not in valid_statuses:
        return []

    result: List[Dict[str, Any]] = []
    for t in transactions:
        current_status = t.get("state") or t.get("status") or ""
        clean_status = str(current_status).strip().upper()
        if clean_status == target:
            result.append(t)

    return result


def sort_transactions(transactions: List[Dict], ascending: bool = True) -> List[Dict]:
    def get_date_key(t: Dict) -> str:
        return str(t.get("date") or "")

    return sorted(transactions, key=get_date_key, reverse=not ascending)


def filter_currency(transactions: List[Dict], currency: str) -> List[Dict]:
    target_curr = currency.upper()
    result = []
    for t in transactions:
        amount_data = t.get("operationAmount", {}) or {}
        currency_data = amount_data.get("currency", {}) or {}
        code = str(currency_data.get("code", "") or "").upper()

        if code == target_curr:
            result.append(t)
    return result


def format_transaction_output(tx: Dict[str, Any]) -> str:
    date_raw = tx.get("date", "Дата не указана")
    date_str = str(date_raw)

    # Обработка даты (убираем время)
    if isinstance(date_raw, str) and "T" in date_raw:
        try:
            date_part = date_raw.split("T")[0]
            parts = date_part.split("-")
            if len(parts) == 3:
                date_str = f"{parts[2]}.{parts[1]}.{parts[0]}"
        except Exception:
            pass

    description = tx.get("description", "Без описания")

    amount_data = tx.get("operationAmount", {}) or {}
    currency_data = amount_data.get("currency", {}) or {}

    amount = amount_data.get("amount", 0.0)
    if not isinstance(amount, (int, float)):
        amount = 0.0

    currency = currency_data.get("code", "RUB")

    return f"{date_str} {description}\nСумма: {amount} {currency}"


def count_transaction_categories(
    transactions: List[Dict[str, Any]], categories: List[str]
) -> Dict[str, int]:
    """
    Подсчитывает количество транзакций по заданным категориям на основе поля description.

    - Поиск по подстроке (регистронезависимо).
    - Одна транзакция может попасть в несколько категорий.
    - Все запрошенные категории гарантированно присутствуют в результате.
    """
    normalized_keywords = [cat.lower() for cat in categories]
    counter = Counter({cat: 0 for cat in categories})

    for tx in transactions:
        description = str(tx.get("description", "")).lower()
        for i, keyword in enumerate(normalized_keywords):
            if keyword in description:
                counter[categories[i]] += 1

    return dict(counter)


if __name__ == "__main__":
    main_logger = logging.getLogger("main")
    main_logger.info("Приложение запущено. Начинаем интерактивную обработку транзакций.")

    print("Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла, путь: data/operations.json")
    print("2. Получить информацию о транзакциях из CSV-файла, путь: data/transactions.csv")
    print("3. Получить информацию о транзакциях из XLSX-файла, путь: data/transactions_excel.xlsx")

    # --- Выбор источника данных ---
    while True:
        choice = input("Ваш выбор: ").strip()
        if choice in {"1", "2", "3"}:
            break
        print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")

    file_path = input("Введите путь к файлу: ").strip()
    path = Path(file_path)
    if not path.exists():
        print(f"Файл не найден: {path}")
        main_logger.error("Файл не найден по пути: %s", path)
        raise SystemExit(1)

    transactions: List[Dict] = []

    if choice == "1":
        print("Программа: Для обработки выбран JSON-файл.")
        transactions = load_json(str(path))
    elif choice == "2":
        print("Программа: Для обработки выбран CSV-файл.")
        transactions = load_csv(str(path))
    else:
        print("Программа: Для обработки выбран XLSX-файл.")
        transactions = load_xlsx(str(path))

    if not transactions:
        print("Файл пуст или не удалось загрузить транзакции.")
        main_logger.warning("Список транзакций пуст после загрузки.")
        raise SystemExit(0)

    main_logger.info(f"Загружено транзакций: {len(transactions)}")

    # --- Фильтрация по статусу ---
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        status_input = input(
            "Программа: Введите статус, по которому необходимо выполнить фильтрацию.\n"
            f"Доступные для фильтровки статусы: {', '.join(valid_statuses)}\n"
        ).strip()

        filtered = filter_by_status(transactions, status_input)
        if filtered:
            print(f'Программа: Операции отфильтрованы по статусу "{status_input.upper()}"')
            transactions = filtered
            break
        else:
            print(f'Статус операции "{status_input}" недоступен.')

    # --- Сортировка по дате ---
    sort_choice = input("Программа: Отсортировать операции по дате? Да/Нет\n").strip().lower()
    if sort_choice in {"да", "д", "yes", "y"}:
        while True:
            order = input("Программа: Отсортировать по возрастанию или по убыванию?\n").strip().lower()
            if order in {"по возрастанию", "возрастание", "asc", "ascending"}:
                transactions = sort_transactions(transactions, ascending=True)
                break
            elif order in {"по убыванию", "убывание", "desc", "descending"}:
                transactions = sort_transactions(transactions, ascending=False)
                break
            else:
                print("Пожалуйста, укажите 'по возрастанию' или 'по убыванию'.")

    # --- Фильтр по валюте (только рубли) ---
    rub_choice = input("Программа: Выводить только рублевые транзакции? Да/Нет\n").strip().lower()
    if rub_choice in {"да", "д", "yes", "y"}:
        transactions = filter_currency(transactions, "RUB")

    # --- Поиск по описанию ---
    search_choice = (
        input("Программа: Отфильтровать список транзакций по определенному слову в описании? Да/Нет\n").strip().lower()
    )
    if search_choice in {"да", "д", "yes", "y"}:
        search_term = input("Программа: Введите слово для поиска:\n").strip()
        transactions = search_operations(transactions, search_term)

    # --- Вывод результатов ---
    print("Программа: Распечатываю итоговый список транзакций...")

    if not transactions:
        print("Программа: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        main_logger.info("Итоговая выборка пуста.")
    else:
        print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")
        for tx in transactions:
            print(format_transaction_output(tx))
            print()  # Пустая строка между операциями

            amount_data = tx.get("operationAmount", {}) or {}
            amount = float(amount_data.get("amount", 0))
            currency = (amount_data.get("currency", {}) or {}).get("code", "RUB")

            try:
                rub = convert_to_rub(amount, currency)
                main_logger.debug("Конвертация выполнена: %s %s -> %s RUB", amount, currency, rub)
            except Exception as e:
                main_logger.error("Ошибка конвертации для транзакции %s: %s", tx.get("id"), e, exc_info=True)

    print("\nПрограмма: Хотите получить статистику по категориям операций? Да/Нет")
    stats_choice = input("> ").strip().lower()
    if stats_choice in {"да", "д", "yes", "y"}:
        print("Программа: Введите названия категорий через запятую (например: перевод, покупка, открытие, снятие):")
        categories_input = input("> ").strip()
        if categories_input:
            categories_list = [c.strip() for c in categories_input.split(",") if c.strip()]
            category_counts = count_transaction_categories(transactions, categories_list)

            print("\n--- Статистика по категориям ---")
            total_count = sum(category_counts.values())
            for cat, count in category_counts.items():
                print(f"{cat}: {count}")
            print(f"Всего учтено операций (с учётом пересечений): {total_count}")
        else:
            print("Программа: Пропуск подсчёта категорий.")
    else:
        print("Программа: Пропуск статистики по категориям.")
