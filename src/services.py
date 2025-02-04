import logging
import os
from datetime import datetime
from typing import Any

from config import PATH_TO_OPERATIONS
from src.utils import convert_excel_into_list

logger = logging.getLogger("services")
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), "..", "logs", "services.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("{asctime} {filename} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """
    Округляет траты с учетом данного порога округления,
    разницу между тратами и суммой округления отправляет в Инвесткопилку.
    Возвращает сумму, которую удалось отложить в Инвесткопилку за заданный месяц
    """
    logger.info(f"Вызов investment_bank: month={month}, limit={limit}, количество транзакций={len(transactions)}")

    money_box = []
    for transaction in transactions:
        if transaction.get("Статус") != "OK":
            continue

        amount = transaction.get("Сумма платежа")
        if not isinstance(amount, (int, float)):
            try:
                amount = float(str(amount).replace(",", "."))
            except ValueError:
                logger.warning(f"Пропущена транзакция с некорректной суммой: {transaction}")
                continue
        if amount >= 0:
            continue

        date_value = transaction.get("Дата операции")
        if isinstance(date_value, str):
            try:
                operation_date = datetime.strptime(date_value, "%Y-%m-%d")
                operation_month = operation_date.strftime("%Y-%m")
            except ValueError:
                logger.warning(f"Пропущена транзакция с некорректной датой: {transaction}")
                continue
        else:
            logger.debug(f"Пропущена транзакция без даты: {transaction}")
            continue

        if month == operation_month:
            if isinstance(amount, (int, float)):
                investment = round(limit - (abs(amount) % limit), 2)
            else:
                continue
            money_box.append(investment)

    logger.info(f"Общая сумма, отправленная в Инвесткопилку за {month}: {round(sum(money_box), 2)}")
    return round(sum(money_box), 2) if money_box else 0.0


if __name__ == "__main__":
    my_transactions = convert_excel_into_list(PATH_TO_OPERATIONS)
    result = investment_bank("2020-02", my_transactions, 50)
    print(result)
