import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_TO_OPERATIONS, PATH_TO_USER_SETTINGS
from src.utils import greeting, read_excel

load_dotenv()
API_KEY_EXCHANGE_RATES = os.getenv("API_KEY_EXCHANGE_RATES")
API_KEY_FINANCIAL_MODELING = os.getenv("API_KEY_FINANCIAL_MODELING")
API_KEY_ALPHA_VANTAGE = os.getenv("API_KEY_ALPHA_VANTAGE")


def filter_transactions_date(df_transactions: pd.DataFrame, date: datetime) -> pd.DataFrame:
    """
    Получение операций за период с начала указанного месяца по заданную дату
    """
    df_transactions["Дата операции"] = pd.to_datetime(df_transactions["Дата операции"])
    year_, month_, day_ = date.year, date.month, date.day
    start_date = datetime(year_, month_, 1)
    end_date = datetime(year_, month_, day_, 23, 59, 59)
    df_range_date = df_transactions[
        (df_transactions["Дата операции"] >= start_date) & (df_transactions["Дата операции"] <= end_date)
    ].reset_index(drop=True)
    return df_range_date


def get_card_info(df_transactions: pd.DataFrame) -> list[dict]:
    """
    Возвращает данные по каждой карте на указанную дату
    """

    df_transactions = df_transactions[(df_transactions["Сумма платежа"] < 0) & (df_transactions["Статус"] == "OK")]
    expenses_by_cards = (
        df_transactions.groupby("Номер карты").agg({"Сумма платежа": "sum", "Кэшбэк": "sum"}).reset_index()
    )
    cards_info = []
    for card_dict in expenses_by_cards.to_dict(orient="records"):
        card_details = {
            "last_digits": card_dict["Номер карты"][-4:],
            "total_spent": abs(float(card_dict["Сумма платежа"])),
            "cashback": round(abs(float(card_dict["Сумма платежа"])) * 0.01, 2),
        }
        cards_info.append(card_details)

    return cards_info


def get_top_transactions(df_transactions: pd.DataFrame) -> list[dict]:
    """
    Возвращает 5 транзакций с наибольшей суммой платежа
    """

    df_transactions = df_transactions[df_transactions["Статус"] == "OK"]
    df_transactions.loc[:, "Сумма платежа"] = df_transactions["Сумма платежа"].abs()
    top_transactions = df_transactions.sort_values(by="Сумма платежа", ascending=False).head(5)

    top_transactions["Дата операции"] = pd.to_datetime(top_transactions["Дата операции"]).dt.strftime("%d.%m.%Y")

    top_transactions = top_transactions.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )

    return top_transactions[["date", "amount", "category", "description"]].to_dict(orient="records")


def get_currency_rates(path: str | Path, date_obj: datetime) -> list[dict]:
    """
    Возвращает название валют и их курс относительно рубля в формате словаря
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            user_settings = json.load(file)

        if not isinstance(user_settings, dict) or "user_currencies" not in user_settings:
            return []

        currencies_rates = []
        date_string = date_obj.strftime("%Y-%m-%d")

        for currency in user_settings["user_currencies"]:
            url = f"https://api.apilayer.com/exchangerates_data/{date_string}?symbols=RUB&base={currency}"
            headers = {"apikey": f"{API_KEY_EXCHANGE_RATES}"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                currency_data = response.json()
                currency_rate = currency_data["rates"].get("RUB")

                if currency_rate:
                    currencies_rates.append({"currency": currency, "rate": round(currency_rate, 2)})
                else:
                    print(f"Нет данных для {currency} на {date_string}")

            else:
                raise ValueError(f"Failed to get the currency rate. Status code: {response.reason}.")

        return currencies_rates

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error loading currency list: {e}")
        return []


def get_stock_prices(path: str | Path, date_obj: datetime) -> list[dict]:
    """
    Возвращает название акций и их стоимость в рублях
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            user_settings = json.load(file)

        if not isinstance(user_settings, dict) or "user_stocks" not in user_settings:
            return []

        currency_rates = get_currency_rates(path, date_obj)
        usd_to_rub_rate = next(curr_rate["rate"] for curr_rate in currency_rates if curr_rate["currency"] == "USD")

        stock_prices = []
        date_string = date_obj.strftime("%Y-%m-%d")

        for stock in user_settings["user_stocks"]:
            url = (
                f"https://financialmodelingprep.com/api/v3/historical-price-full/{stock}?"
                f"from={date_string}&to={date_string}&apikey={API_KEY_FINANCIAL_MODELING}"
            )
            response = requests.get(url)

            if response.status_code == 200:
                stock_data = response.json()
                historical_data = stock_data.get("historical", [])

                if historical_data and historical_data[0]["close"] is not None:
                    final_price = float(historical_data[0]["close"])
                    rub_stock_price = final_price * usd_to_rub_rate

                    stock_prices.append({"stock": stock, "price": round(rub_stock_price, 2)})
                else:
                    print(f"Нет данных для {stock} на {date_string}")

            else:
                raise ValueError(f"Failed to get the stock price. Status code: {response.reason}.")

        return stock_prices

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error loading stock list: {e}")
        return []


def main_page_fnc(date: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Принимает на вход строку с датой и временем и возвращает JSON-файл с определенными данными
    """
    date_obj = datetime.strptime(date, fmt)
    request_hour, request_minutes = date_obj.hour, date_obj.minute
    greeting_message = greeting(request_hour, request_minutes)

    operations_data = read_excel(PATH_TO_OPERATIONS)
    df_range_date = filter_transactions_date(operations_data, date_obj)

    cards_message = get_card_info(df_range_date)
    top_trans_message = get_top_transactions(df_range_date)
    currency_rate_message = get_currency_rates(PATH_TO_USER_SETTINGS, date_obj)
    stock_prices_message = get_stock_prices(PATH_TO_USER_SETTINGS, date_obj)

    user_info = {
        "greeting": greeting_message,
        "cards": cards_message,
        "top_transactions": top_trans_message,
        "currency_rates": currency_rate_message,
        "stock_prices": stock_prices_message,
    }
    return json.dumps(user_info, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    df_operations = read_excel(PATH_TO_OPERATIONS)
    print(main_page_fnc("2021-02-11 23:05:55"))
