from datetime import datetime
from typing import Any

from config import PATH_TO_OPERATIONS
from src.utils import convert_excel_into_list


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """
    Округляет траты с учетом данного порога округления,
    разницу между тратами и суммой округления отправляет в Инвесткопилку.
    Возвращает сумму, которую удалось отложить в Инвесткопилку за заданный месяц
    """
    money_box = []
    for transaction in transactions:
        if transaction.get("Статус") != "OK":
            continue

        amount = transaction.get("Сумма платежа")
        if not isinstance(amount, (int, float)):
            try:
                amount = float(str(amount).replace(",", "."))
            except ValueError:
                continue
        if amount >= 0:
            continue

        date_value = transaction.get("Дата операции")
        if isinstance(date_value, str):
            try:
                operation_date = datetime.strptime(date_value, "%Y-%m-%d")
                operation_month = operation_date.strftime("%Y-%m")
            except ValueError:
                continue
        else:
            continue

        if month == operation_month:
            if isinstance(amount, (int, float)):
                investment = round(limit - (abs(amount) % limit), 2)
            else:
                continue
            money_box.append(investment)

    return round(sum(money_box), 2) if money_box else 0.0


if __name__ == "__main__":
    my_transactions = convert_excel_into_list(PATH_TO_OPERATIONS)
    result = investment_bank("2020-02", my_transactions, 50)
    print(result)
