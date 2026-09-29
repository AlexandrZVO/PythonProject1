"""Модуль для чтения финансовых операций из CSV- и XLSX-файлов."""

import os
from typing import Any, Dict, List, cast

import pandas as pd


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Очищает DataFrame от пустых строк и приводит типы числовых колонок.

    Параметры:
        df: исходный DataFrame.

    Возвращает:
        Очищенный DataFrame.
    """
    df = df.dropna(how="all")
    if "id" in df.columns:
        df["id"] = df["id"].astype("Int64")
    if "amount" in df.columns:
        df["amount"] = df["amount"].astype("Int64")
    return df


def read_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из CSV-файла.

    Параметры:
        file_path: путь к CSV-файлу.

    Возвращает:
        Список словарей, где каждый словарь — одна транзакция.

    Вызывает:
        FileNotFoundError: если файл не найден.
        ValueError: если возникла ошибка при чтении файла.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        df = pd.read_csv(file_path, sep=";", encoding="utf-8")
        df = _clean_dataframe(df)
        return cast(List[Dict[str, Any]], df.to_dict(orient="records"))
    except Exception as e:
        raise ValueError(f"Ошибка при чтении CSV-файла: {e}") from e


def read_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из XLSX-файла.

    Параметры:
        file_path: путь к XLSX-файлу.

    Возвращает:
        Список словарей, где каждый словарь — одна транзакция.

    Вызывает:
        FileNotFoundError: если файл не найден.
        ValueError: если возникла ошибка при чтении файла.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        df = pd.read_excel(file_path)
        df = _clean_dataframe(df)
        return cast(List[Dict[str, Any]], df.to_dict(orient="records"))
    except Exception as e:
        raise ValueError(f"Ошибка при чтении Excel-файла: {e}") from e


if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    csv_path = os.path.join(DATA_DIR, "transactions.csv")
    xlsx_path = os.path.join(DATA_DIR, "transactions_excel.xlsx")

    print("CSV:", len(read_transactions_from_csv(csv_path)), "транзакций")
    print("XLSX:", len(read_transactions_from_excel(xlsx_path)), "транзакций")
