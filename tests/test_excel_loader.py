import pytest
from unittest.mock import patch, MagicMock
from src.main import load_xlsx


class TestExcelLoader:
    """Группа тестов для функции загрузки Excel."""

    @patch('src.main.load_workbook')
    def test_returns_empty_list_if_no_sheet(self, mock_load):
        """Тест: если в файле нет активного листа, возвращаем пустой список."""
        mock_wb = MagicMock()
        mock_wb.active = None  # Эмулируем ситуацию, когда листа нет
        mock_load.return_value = mock_wb

        result = load_xlsx("fake_path.xlsx")

        assert result == []
        mock_load.assert_called_once()

    @patch('src.main.load_workbook', side_effect=ImportError)
    def test_handles_missing_library_gracefully(self, mock_load):
        """Тест: если нет openpyxl, функция не падает, а возвращает пустой список."""
        result = load_xlsx("fake_path.xlsx")

        assert result == []
        # Здесь можно позже добавить проверку вывода через capsys,
        # но пока достаточно проверить, что программа не упала и вернула []


# tests/test_excel_loader.py
from src.main import load_xlsx
from unittest.mock import patch, MagicMock


@patch('src.main.load_workbook')
def test_load_xlsx_returns_empty_list_when_no_active_sheet(mock_load_workbook):
    # 1. Готовим мок: workbook, у которого active = None
    mock_wb = MagicMock()
    mock_wb.active = None
    mock_load_workbook.return_value = mock_wb

    # 2. Запускаем функцию
    result = load_xlsx("any_path.xlsx")

    # 3. Проверяем результат
    assert result == []

    # 4. Проверяем, что load_workbook вообще вызвали
    mock_load_workbook.assert_called_once()

    import os

    def test_handles_real_file_with_invalid_amount(self):
        """Тест на реальном файле: проверяем, что функция не падает на битых данных."""
        # Путь к тестовому файлу (относительно папки tests)
        test_file = os.path.join(os.path.dirname(__file__), "fixtures", "broken_amount.xlsx")

        result = load_xlsx(test_file)

        # Функция не должна падать, даже если данные кривые
        assert isinstance(result, list)
        # В идеале там должна быть транзакция с amount=0.0, но хотя бы не пустой список из-за ошибки
        # assert len(result) >= 1  # Раскомментируй, если хочешь, чтобы файл точно что-то вернул


import csv
from io import StringIO
from unittest.mock import patch
from src.main import load_csv  # замени на имя своей функции


#class TestCsvLoader:

#     def test_handles_empty_csv_gracefully(self):
#         """Тест: пустой CSV не должен ломать программу."""
#         # Эмулируем пустой файл через StringIO (это как файл в памяти)
#         fake_file = StringIO("")
#
#         # Мокаем open(), чтобы он отдавал наш fake_file вместо реального диска
#         with patch('builtins.open', return_value=fake_file):
#             result = load_csv("dummy.csv")
#
#         assert result == []  # Пустой CSV -> пустой список
#
#     def test_converts_invalid_csv_amount_to_zero(self):
#         """Тест: если в CSV вместо числа мусор — ставим 0.0."""
#         csv_data = """id,amount,state
# 101,N/A,New
# 102,500.50,Done"""
#
#         fake_file = StringIO(csv_data)
#
#         with patch('builtins.open', return_value=fake_file):
#             result = load_csv("dummy.csv")
#
#         assert len(result) == 2
#         # Первая строка: amount был "N/A", должен стать 0.0
#         assert result[0]["operationAmount"]["amount"] == 0.0
#         # Вторая строка: всё ок
#         assert result[1]["operationAmount"]["amount"] == 500.5
