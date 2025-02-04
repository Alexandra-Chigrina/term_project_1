import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable


def log_result_into_file(filename: Path) -> Callable:
    """
    Декоратор, записывающий результат функции в файл
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if filename:
                os.makedirs("logs", exist_ok=True)
                path_to_filename = os.path.join("logs", filename)
                with open(path_to_filename, "a", encoding="utf-8") as file:
                    file.write(f"Результат: {result}\n")

            return result

        return wrapper

    return decorator
