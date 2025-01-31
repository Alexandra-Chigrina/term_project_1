from datetime import datetime, time
from pathlib import Path

import pandas as pd

from config import PATH_TO_OPERATIONS


def greeting(hour_: int, minutes_: int) -> str:
    """
    Функция приветствия
    """
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
    operations_df = read_excel(PATH_TO_OPERATIONS)
    print(operations_df)
