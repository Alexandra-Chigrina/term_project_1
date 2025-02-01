from datetime import datetime, time
from pathlib import Path

import pandas as pd

from config import PATH_TO_OPERATIONS


def greeting(hour_: int, minutes_: int) -> str:
    """
    Функция приветствия
    """
    if not isinstance(hour_, int) or not isinstance(minutes_, int):
        raise TypeError(
            f"Ошибка: Часы и минуты должны быть целыми числами.")

    if not (0 <= hour_ <= 23):
        raise ValueError(f"Ошибка: недопустимое значение часов: {hour_}. Должно быть от 0 до 23.")

    if not (0 <= minutes_ <= 59):
        raise ValueError(f"Ошибка: недопустимое значение минут: {minutes_}. Должно быть от 0 до 59.")

    if time(hour=22) <= time(hour_, minutes_) <= time(hour=23, minute=59, second=59) or time(hour=0) <= time(
        hour_, minutes_
    ) < time(hour=6):
        return "Доброй ночи"
    elif time(hour=6) <= time(hour_, minutes_) < time(hour=11, minute=59, second=59):
        return "Доброе утро"
    elif time(hour=12) <= time(hour_, minutes_) < time(hour=17, minute=59, second=59):
        return "Добрый день"
    else:
        return "Добрый вечер"


def read_excel(path: str | Path, datetime_to_timestamp: bool = True) -> pd.DataFrame:
    """
    Функция чтения XLSX-файла
    """
    try:
        operations_df = pd.read_excel(path)
        if datetime_to_timestamp:
            operations_df["Дата операции"] = pd.to_datetime(operations_df["Дата операции"], dayfirst=True)
        return operations_df

    except FileNotFoundError:
        print(f"Ошибка: Файл {path} не найден.")
        return pd.DataFrame()

    except ValueError as e:
        print(f"Ошибка при чтении Excel-файла: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    date_now = datetime.now().time()
    hour = date_now.hour
    minutes = date_now.minute
    print(greeting(hour, minutes))
    operations = read_excel(PATH_TO_OPERATIONS)
    print(operations)
