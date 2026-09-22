import inspect
import sys
import time
from functools import wraps
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для логирования выполнения функций."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            params_str = ", ".join(f"{name}={value!r}" for name, value in bound_args.arguments.items())

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_msg = f"START: {func.__name__}({params_str}) | " f"DURATION: {duration:.4f}s | RESULT: {result!r}"
            except Exception as e:
                duration = time.time() - start_time
                log_msg = (
                    f"ERROR: {func.__name__}({params_str}) | "
                    f"DURATION: {duration:.4f}s | "
                    f"ERROR_TYPE: {type(e).__name__} | ERROR_MSG: {str(e)}"
                )
                _write_log(log_msg, filename)
                raise

            _write_log(log_msg, filename)
            return result

        return wrapper

    return decorator


def _write_log(log_msg: str, filename: Optional[str]) -> None:
    """Внутренняя функция для записи лога в файл или stdout."""
    if filename:
        with open(filename, "a", encoding="utf-8") as f:
            print(log_msg, file=f)
    else:
        print(log_msg, file=sys.stdout)
