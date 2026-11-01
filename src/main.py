"""Точка входа в приложение."""

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Для XLSX понадобится openpyxl, если будешь использовать этот пункт меню
# pip install openpyxl
try:
    from openpyxl import load_workbook
except ImportError:
    pass

import logging
from logging import FileHandler, Formatter

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


def search_operations(transactions: List[Dict], search_string: str) -> List[Dict]:
    """Поиск по описанию с использованием re (регистронезависимо)."""
    if not search_string:
        return transactions
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    return [op for op in transactions if pattern.search(op.get("description", ""))]


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    target = status.strip().upper()
    valid_statuses = {"EXECUTED", "CANCELED", "PENDING"}

    if target not in valid_statuses:
        return []

    result: List[Dict[str, Any]] = []
    for t in transactions:
        # Используем or "" чтобы гарантировать, что current_status - это строка, а не None
        current_status = t.get("status") or t.get("state") or ""

        clean_status = str(current_status).strip().upper()

        if clean_status == target:
            result.append(t)

    return result


def sort_transactions(transactions: List[Dict], ascending: bool = True) -> List[Dict]:
    def get_date_key(t: Dict) -> str:
        # В твоем JSON поле называется 'date'
        date_val = t.get("date", "")
        return str(date_val)

    return sorted(transactions, key=get_date_key, reverse=not ascending)


def filter_currency(transactions: List[Dict], currency: str) -> List[Dict]:
    target_curr = currency.upper()
    result = []
    for t in transactions:
        amount_data = t.get("operationAmount", {})
        currency_data = amount_data.get("currency", {})
        code = currency_data.get("code", "").upper()

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

    amount_data = tx.get("operationAmount", {})
    currency_data = amount_data.get("currency", {})

    # Безопасное получение суммы (по умолчанию 0.0)
    amount = amount_data.get("amount", 0.0)
    if not isinstance(amount, (int, float)):
        amount = 0.0

    currency = currency_data.get("code", "RUB")

    line1 = f"{date_str} {description}"
    line2 = f"Сумма: {amount} {currency}"

    return f"{line1}\n{line2}"


def load_xlsx(path: str) -> List[Dict[str, Any]]:
    try:

        # data_only=True важно, чтобы брать значения из формул, а не сами формулы
        wb = load_workbook(filename=path, data_only=True)
        ws = wb.active  # Может вернуть None, если листов нет!

        # ГЛАВНОЕ ИСПРАВЛЕНИЕ: проверяем, что лист действительно существует
        if ws is None:
            print("В файле нет активных листов.")
            return []

        transactions: List[Dict[str, Any]] = []

        # Получаем заголовки из первой строки
        # ws.iter_rows() теперь безопасен, потому что мы уже проверили, что ws не None
        header_row = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1), [])]

        # Нормализуем заголовки (убираем пробелы, приводим к нижнему регистру для удобства)
        # Ожидаем примерно такие колонки: id, state, date, amount, currency_code и т.д.
        headers = [str(h).strip().lower() if h else "" for h in header_row]

        # Находим индексы нужных колонок (защита от отсутствия колонок)
        def get_col_index(name: str) -> int | None:
            try:
                return headers.index(name)
            except ValueError:
                return None

        idx_id = get_col_index("id")
        idx_state = get_col_index("state") or get_col_index("status")
        idx_date = get_col_index("date")
        idx_amount = get_col_index("amount")
        idx_currency_code = get_col_index("currency_code") or get_col_index("code")
        idx_description = get_col_index("description")

        # Если критически важных колонок нет (например, id или amount), лучше выйти
        if idx_id is None or idx_amount is None:
            print(" Не найдены обязательные колонки (id, amount). Проверьте структуру XLSX.")
            # Можно вернуть пустой список или попробовать прочитать как есть — зависит от твоей логики
            return []

        # Читаем остальные строки
        for row in ws.iter_rows(min_row=2, values_only=True):
            # Защита от пустых строк в конце файла
            if not row or all(cell is None for cell in row):
                continue

            # Безопасное получение значений по индексам
            raw_id = row[idx_id] if idx_id < len(row) else None
            raw_state = row[idx_state] if idx_state is not None and idx_state < len(row) else ""
            raw_date = row[idx_date] if idx_date is not None and idx_date < len(row) else ""
            raw_amount = row[idx_amount] if idx_amount < len(row) else 0
            raw_currency = (
                row[idx_currency_code] if idx_currency_code is not None and idx_currency_code < len(row) else "UNK"
            )
            raw_desc = (
                row[idx_description] if idx_description is not None and idx_description < len(row) else "Без описания"
            )

            # Преобразование типов
            try:
                if raw_amount is None:
                    amount_val = 0.0
                elif isinstance(raw_amount, (int, float)):
                    # Если это уже число (даже Decimal), просто приводим к float
                    amount_val = float(raw_amount)
                elif isinstance(raw_amount, str):
                    # Если строка — пытаемся превратить в число
                    try:
                        amount_val = float(raw_amount.replace(",", "."))  # На случай, если там "10,5"
                    except ValueError:
                        amount_val = 0.0
                else:
                    # Если там дата, время или какой-то объект openpyxl — ставим 0
                    amount_val = 0.0

            except (ValueError, TypeError):
                amount_val = 0.0

            tx: Dict[str, Any] = {
                "id": raw_id,
                "state": str(raw_state).strip() if raw_state else "",
                "date": str(raw_date).strip() if raw_date else "",
                "description": str(raw_desc).strip(),
                "operationAmount": {
                    "amount": amount_val,
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
        print(f" Ошибка чтения XLSX: {e}")
        return []


def safe_float(value: Optional[Any]) -> float:
    """Универсальная защита: превращает что угодно в float или 0.0"""
    if value is None:
        return 0.0
    try:
        clean_val = str(value).strip().replace(",", ".")
        return float(clean_val)
    except (ValueError, TypeError):
        return 0.0


def load_csv(path: str) -> List[Dict[str, Any]]:
    """Загружает CSV с разделителем ';' и нормализует суммы."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            transactions: List[Dict[str, Any]] = []

            for row in reader:
                raw_amount = row.get("amount")
                currency_code = row.get("currency_code", "UNK")
                currency_name = row.get("currency_name", "Неизвестно")

                amount_val = safe_float(raw_amount)

                tx: Dict[str, Any] = {
                    "id": row.get("id"),
                    "state": row.get("state"),
                    "date": row.get("date"),
                    "description": row.get("description", "Без описания"),
                    "operationAmount": {
                        "amount": amount_val,
                        "currency": {"name": currency_name, "code": currency_code},
                    },
                }
                transactions.append(tx)

            return transactions

    except FileNotFoundError:
        print(f" Файл не найден: {path}")
        return []
    except Exception as e:
        print(f" Ошибка чтения CSV: {e}")
        return []


def load_json(path: str) -> List[Dict[str, Any]]:
    """
    Загружает JSON и приводит транзакции к единому формату.
    Ожидает список объектов.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("JSON должен содержать список транзакций")
            return []

        transactions: List[Dict[str, Any]] = []

        for row in data:
            # Получаем значения, ставим заглушки, если ключей нет
            tx_id = row.get("id")
            state = row.get("state", "Unknown")
            date = row.get("date")
            description = row.get("description", "Без описания")

            currency_code = row.get("currency_code", "UNK")
            currency_name = row.get("currency_name", "Неизвестно")
            raw_amount = row.get("amount")  # Может быть None, строкой или числом

            # Используем нашу универсальную функцию конвертации
            amount_val = safe_float(raw_amount)

            tx: Dict[str, Any] = {
                "id": tx_id,
                "state": state,
                "date": date,
                "description": description,
                "operationAmount": {
                    "amount": amount_val,
                    "currency": {"name": currency_name, "code": currency_code},
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


if __name__ == "__main__":
    main_logger = logging.getLogger("main")
    main_logger.info("Приложение запущено. Начинаем интерактивную обработку транзакций.")

    print("Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла, путь data/operations.json ")
    print("2. Получить информацию о транзакциях из CSV-файла, путь data/transactions.csv")
    print("3. Получить информацию о транзакциях из XLSX-файла, путь data/transactions_excel.xlsx")

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
        exit(1)

    transactions: List[Dict] = []

    if choice == "1":
        print("Программа: Для обработки выбран JSON-файл.")
        # Используем твою существующую функцию загрузки
        transactions = load_transactions(str(path))
    elif choice == "2":
        print("Программа: Для обработки выбран CSV-файл.")
        transactions = load_csv(str(path))
    else:
        print("Программа: Для обработки выбран XLSX-файл.")
        transactions = load_xlsx(str(path))

    if not transactions:
        print("️ Файл пуст или не удалось загрузить транзакции.")
        main_logger.warning("Список транзакций пуст после загрузки.")
        exit(0)

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
            # Тут мы используем твой старый код конвертации, если нужно,
            # но вывод делаем через новый форматтер, чтобы соответствовать ТЗ

            amount_data = tx.get("operationAmount", {})
            amount = float(amount_data.get("amount", 0))
            currency_data = amount_data.get("currency", {})
            currency = currency_data.get("code", "RUB")

            try:
                rub = convert_to_rub(amount, currency)
                # Если нужна конвертация в выводе — раскомментируй строку ниже вместо format_transaction_output
                # print(f"{format_transaction_output(tx)}\nКонвертировано в RUB: {rub}")

                print(format_transaction_output(tx))
                print()  # Пустая строка между операциями

            except Exception as e:
                main_logger.error("Ошибка конвертации для транзакции %s: %s", tx.get("id"), e, exc_info=True)
                print(f" #{tx.get('id')} Ошибка конвертации (см. лог)")
