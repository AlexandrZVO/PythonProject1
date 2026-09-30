"""Тесты для модуля чтения финансовых транзакций."""

import os
import tempfile
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.transactions import (read_transactions_from_csv,
                              read_transactions_from_excel)


@pytest.fixture
def sample_csv_path() -> Iterator[str]:
    """Создаёт временный CSV-файл для тестов."""
    content = (
        "id;state;date;amount;currency_name;"
        "currency_code;from;to;description\n"
        "1;EXECUTED;2023-01-01;100;Ruble;RUB;"
        "Visa 123;Счет 456;Перевод\n"
        "2;CANCELED;2023-01-02;200;Euro;EUR;"
        "Visa 789;Счет 012;Перевод\n"
        ";;;;;;;;\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def sample_xlsx_path() -> Iterator[str]:
    """Создаёт временный XLSX-файл для тестов."""
    data = {
        "id": [1, 2, None],
        "state": ["EXECUTED", "CANCELED", None],
        "date": ["2023-01-01", "2023-01-02", None],
        "amount": [100, 200, None],
        "currency_name": ["Ruble", "Euro", None],
        "currency_code": ["RUB", "EUR", None],
        "from": ["Visa 123", "Visa 789", None],
        "to": ["Счет 456", "Счет 012", None],
        "description": ["Перевод", "Перевод", None],
    }
    df = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    df.to_excel(path, index=False)
    yield path
    os.unlink(path)


def test_csv_read_success(sample_csv_path: str) -> None:
    """Тест успешного чтения CSV."""
    result = read_transactions_from_csv(sample_csv_path)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["amount"] == 100
    assert result[1]["state"] == "CANCELED"


def test_csv_empty_rows_skipped(sample_csv_path: str) -> None:
    """Тест: пустые строки пропускаются."""
    result = read_transactions_from_csv(sample_csv_path)
    assert len(result) == 2
    for row in result:
        assert row["id"] is not None


def test_csv_file_not_found() -> None:
    """Тест: FileNotFoundError при отсутствии файла."""
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        read_transactions_from_csv("nonexistent_file.csv")


@patch("src.transactions.pd.read_csv")
@patch("src.transactions.os.path.exists")
def test_csv_mock_read(mock_exists: MagicMock, mock_read_csv: MagicMock) -> None:
    """Тест чтения CSV через mock."""
    mock_exists.return_value = True
    mock_df = MagicMock()
    mock_df.dropna.return_value = mock_df
    mock_df.__contains__ = lambda self, key: key in ["id", "amount"]
    mock_df.to_dict.return_value = [{"id": 42, "amount": 500}]
    mock_read_csv.return_value = mock_df

    result = read_transactions_from_csv("dummy.csv")
    assert result == [{"id": 42, "amount": 500}]
    mock_read_csv.assert_called_once()


@patch("src.transactions.pd.read_csv")
@patch("src.transactions.os.path.exists")
def test_csv_read_error(mock_exists: MagicMock, mock_read_csv: MagicMock) -> None:
    """Тест: ValueError при ошибке чтения CSV."""
    mock_exists.return_value = True
    mock_read_csv.side_effect = Exception("boom")

    with pytest.raises(ValueError, match="Ошибка"):
        read_transactions_from_csv("dummy.csv")


def test_excel_read_success(sample_xlsx_path: str) -> None:
    """Тест успешного чтения XLSX."""
    result = read_transactions_from_excel(sample_xlsx_path)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["amount"] == 100
    assert result[1]["state"] == "CANCELED"


def test_excel_empty_rows_skipped(sample_xlsx_path: str) -> None:
    """Тест: пустые строки пропускаются."""
    result = read_transactions_from_excel(sample_xlsx_path)
    assert len(result) == 2
    for row in result:
        assert row["id"] is not None


def test_excel_file_not_found() -> None:
    """Тест: FileNotFoundError при отсутствии файла."""
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        read_transactions_from_excel("nonexistent_file.xlsx")


@patch("src.transactions.pd.read_excel")
@patch("src.transactions.os.path.exists")
def test_excel_mock_read(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:
    """Тест чтения XLSX через mock."""
    mock_exists.return_value = True
    mock_df = MagicMock()
    mock_df.dropna.return_value = mock_df
    mock_df.__contains__ = lambda self, key: key in ["id", "amount"]
    mock_df.to_dict.return_value = [{"id": 42, "amount": 500}]
    mock_read_excel.return_value = mock_df

    result = read_transactions_from_excel("dummy.xlsx")
    assert result == [{"id": 42, "amount": 500}]
    mock_read_excel.assert_called_once()


@patch("src.transactions.pd.read_excel")
@patch("src.transactions.os.path.exists")
def test_excel_read_error(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:
    """Тест: ValueError при ошибке чтения XLSX."""
    mock_exists.return_value = True
    mock_read_excel.side_effect = Exception("boom")

    with pytest.raises(ValueError, match="Ошибка"):
        read_transactions_from_excel("dummy.xlsx")
