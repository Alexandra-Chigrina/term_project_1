import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from config import PATH_TO_INVESTMENT_RESULT, PATH_TO_OPERATIONS
from src.decorators import log_result_into_file
from src.utils import read_excel

logger = logging.getLogger("reports")
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), "..", "logs", "reports.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("{asctime} {filename} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


@log_result_into_file(PATH_TO_INVESTMENT_RESULT)
def spending_by_category(df_transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Возвращает траты по заданной категории за последние три месяца (от переданной даты), если дата не задана,
    то берется текущая дата
    """
    logger.info(f"Вызов spending_by_category: category='{category}', date='{date}'")

    if date is None:
        end_date = datetime.today()
    else:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logger.error("Ошибка: Неверный формат даты")
            return "Неверный формат даты. Используйте YYYY-MM-DD"

    start_date = end_date - timedelta(days=90)
    df_transactions["Дата операции"] = pd.to_datetime(df_transactions["Дата операции"])

    df_transactions = df_transactions[
        (df_transactions["Сумма платежа"] < 0)
        & (df_transactions["Статус"] == "OK")
        & (df_transactions["Дата операции"] >= start_date)
        & (df_transactions["Дата операции"] <= end_date)
    ]

    logger.info(f"Фильтрация завершена. Найдено {len(df_transactions)} записей за период {start_date} - {end_date}")

    expenses = df_transactions[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
    expenses["Сумма платежа"] = expenses["Сумма платежа"].abs()
    expenses_category = expenses[expenses["Категория"] == category.capitalize()]

    if expenses_category.empty:
        logger.info(f"Нет данных по категории '{category}' за указанный период")
        return f"Нет данных по категории '{category}' за указанный период"

    expenses_dict = expenses_category.to_dict(orient="records")

    logger.info(f"Данные по категории '{category}' успешно сформированы")

    return json.dumps(expenses_dict, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    transactions = read_excel(PATH_TO_OPERATIONS)
    result = spending_by_category(transactions, "переводы", "2021-02-28")
    print(result)
