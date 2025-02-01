import json
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from config import PATH_TO_OPERATIONS, PATH_TO_INVESTMENT_RESULT
from src.utils import read_excel
from src.decorators import log_result_into_file


@log_result_into_file(PATH_TO_INVESTMENT_RESULT)
def spending_by_category(df_transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Возвращает траты по заданной категории за последние три месяца (от переданной даты), если дата не задана,
    то берется текущая дата
    """
    if date is None:
        end_date = datetime.today()
    else:
        try:
            end_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Неверный формат даты. Используйте YYYY-MM-DD"

    start_date = end_date - timedelta(days=90)
    df_transactions["Дата операции"] = pd.to_datetime(df_transactions["Дата операции"])

    df_transactions = df_transactions[
        (df_transactions["Сумма платежа"] < 0)
        & (df_transactions["Статус"] == "OK")
        & (df_transactions["Дата операции"] >= start_date)
        & (df_transactions["Дата операции"] <= end_date)
    ]

    expenses = df_transactions[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
    expenses["Сумма платежа"] = expenses["Сумма платежа"].abs()
    expenses_category = expenses[expenses["Категория"] == category.capitalize()]

    if expenses_category.empty:
        return f"Нет данных по категории '{category}' за указанный период"

    expenses_dict = expenses_category.to_dict(orient="records")

    return json.dumps(expenses_dict, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    transactions = read_excel(PATH_TO_OPERATIONS)
    result = spending_by_category(transactions, "переводы", "2021-02-28")
    print(result)
