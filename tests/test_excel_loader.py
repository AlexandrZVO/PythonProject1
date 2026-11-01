from unittest.mock import MagicMock, patch

from src.main import load_xlsx


class TestExcelLoader:
    """Группа тестов для функции загрузки Excel."""

    @patch("src.main.load_workbook")
    def test_returns_empty_list_if_no_sheet(self, mock_load):
        """Тест: если в файле нет активного листа, возвращаем пустой список."""
        mock_wb = MagicMock()
        mock_wb.active = None  # Эмулируем ситуацию, когда листа нет
        mock_load.return_value = mock_wb

        result = load_xlsx("fake_path.xlsx")

        assert result == []
        mock_load.assert_called_once()

    @patch("src.main.load_workbook", side_effect=ImportError)
    def test_handles_missing_library_gracefully(self, mock_load):
        """Тест: если нет openpyxl, функция не падает, а возвращает пустой список."""
        result = load_xlsx("fake_path.xlsx")

        assert result == []
        # Здесь можно позже добавить проверку вывода через capsys,
        # но пока достаточно проверить, что программа не упала и вернула []


@patch("src.main.load_workbook")
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
