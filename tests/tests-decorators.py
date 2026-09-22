from pathlib import Path


import pytest

from src.decorators import log

# --- Тесты успешного выполнения (вывод в консоль) ---


def test_successful_console_log(capsys: pytest.CaptureFixture[str]) -> None:
    """Успешный вызов, консоль"""

    @log()
    def add(a: int, b: int) -> int:
        return a + b

    result: int = add(5, 3)
    assert result == 8

    captured = capsys.readouterr()
    assert "START: add" in captured.out
    assert "RESULT: 8" in captured.out
    assert "a=5" in captured.out
    assert "b=3" in captured.out


def test_default_args_logged(capsys: pytest.CaptureFixture[str]) -> None:
    """Аргументы по умолчанию"""

    @log()
    def func(x: int, y: int, z: int = 10) -> int:
        return x + y + z

    func(1, 2)
    captured = capsys.readouterr()
    assert "x=1" in captured.out
    assert "y=2" in captured.out
    assert "z=10" in captured.out


def test_keyword_args_logged(capsys: pytest.CaptureFixture[str]) -> None:
    """Именованные аргументы"""

    @log()
    def greet(name: str, greeting: str = "Привет") -> str:
        return f"{greeting}, {name}!"

    greet("Алексей", greeting="Добрый день")
    captured = capsys.readouterr()
    assert "name='Алексей'" in captured.out
    assert "greeting='Добрый день'" in captured.out


# --- Тесты обработки исключений (вывод в консоль) ---


def test_exception_logged_and_reraised(capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка пробрасывается"""

    @log()
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Деление на ноль!")
        return a / b

    with pytest.raises(ValueError, match="Деление на ноль!"):
        divide(10, 0)

    captured = capsys.readouterr()
    assert "ERROR: divide" in captured.out
    assert "ERROR_TYPE: ValueError" in captured.out
    assert "ERROR_MSG: Деление на ноль!" in captured.out


def test_duration_present(capsys: pytest.CaptureFixture[str]) -> None:
    """Наличие времени выполнения"""
    import time

    @log()
    def slow_func() -> str:
        time.sleep(0.05)
        return "done"

    slow_func()
    captured = capsys.readouterr()
    assert "DURATION:" in captured.out
    assert "s |" in captured.out


# --- Тесты логирования в файл ---


def test_file_logging(tmp_path: Path) -> None:
    """Запись в файл (успех)"""
    log_file: Path = tmp_path / "test_log.txt"

    @log(str(log_file))
    def add(a: int, b: int) -> int:
        return a + b

    add(2, 3)
    assert log_file.exists()
    content: str = log_file.read_text(encoding="utf-8")
    assert "START: add" in content
    assert "RESULT: 5" in content


def test_file_logging_error(tmp_path: Path) -> None:
    """Запись в файл (ошибка)"""
    log_file: Path = tmp_path / "error_log.txt"

    @log(str(log_file))
    def fail() -> None:
        raise RuntimeError("Что-то сломалось")

    with pytest.raises(RuntimeError):
        fail()

    content: str = log_file.read_text(encoding="utf-8")
    assert "ERROR: fail" in content
    assert "ERROR_TYPE: RuntimeError" in content
    assert "ERROR_MSG: Что-то сломалось" in content


def test_file_append_mode(tmp_path: Path) -> None:
    """Режим добавления в файл"""
    log_file: Path = tmp_path / "append_log.txt"

    @log(str(log_file))
    def add(a: int, b: int) -> int:
        return a + b

    add(1, 1)
    add(2, 2)

    content: str = log_file.read_text(encoding="utf-8")
    assert content.count("START: add") == 2
    assert "RESULT: 2" in content
    assert "RESULT: 4" in content


# --- Тест сохранения метаданных ---


def test_preserves_function_name(capsys: pytest.CaptureFixture[str]) -> None:
    """Сохранение __name__ и __doc__"""

    @log()
    def my_special_function(x: int) -> int:
        """Документация функции."""
        return x

    assert my_special_function.__name__ == "my_special_function"
    assert my_special_function.__doc__ == "Документация функции."
