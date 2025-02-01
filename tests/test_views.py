import json
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.views import (
    filter_transactions_date,
    get_card_info,
    get_currency_rates,
    get_stock_prices,
    get_top_transactions,
    main_page_fnc
)


def test_filter_transactions_date(transactions_sample_1):
    date_obj = datetime.strptime("2021-12-06 16:05:21", "%Y-%m-%d %H:%M:%S")
    final_data = pd.DataFrame(
        [
            {
                "Дата операции": "2021-12-05 01:23:42",
                "Дата платежа": "05.12.2021",
                "Номер карты": "*5091",
                "Статус": "OK",
                "Сумма операции": -564.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -564.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": None,
                "Категория": "Различные товары",
                "MCC": 5399.0,
                "Описание": "Ozon.ru",
                "Бонусы (включая кэшбэк)": 5,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 564.0,
            },
            {
                "Дата операции": "2021-12-01 22:22:03",
                "Дата платежа": "01.12.2021",
                "Номер карты": None,
                "Статус": "OK",
                "Сумма операции": -20000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -20000.0,
                "Валюта платежа": "RUB",
                "Кэшбэк": None,
                "Категория": "Переводы",
                "MCC": None,
                "Описание": "Константин Л.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 20000.0,
            },
        ]
    )
    final_data["Дата операции"] = pd.to_datetime(final_data["Дата операции"])
    result = filter_transactions_date(transactions_sample_1, date_obj)

    assert_frame_equal(result, final_data)


def test_get_card_info(transactions_sample_2):
    expected_result = [
        {"last_digits": "4556", "total_spent": 1620.27, "cashback": 16.2},
        {"last_digits": "5091", "total_spent": 564.0, "cashback": 5.64},
        {"last_digits": "7197", "total_spent": 343.01, "cashback": 3.43},
    ]
    result = get_card_info(transactions_sample_2)
    assert result == expected_result


def test_get_top_transactions(transactions_sample_2):
    expected_result = [
        {"date": "10.12.2021", "amount": 20000.0, "category": "Другое", "description": "Иван С."},
        {"date": "01.12.2021", "amount": 20000.0, "category": "Переводы", "description": "Константин Л."},
        {"date": "02.12.2021", "amount": 1620.27, "category": "Супермаркеты", "description": "Перекрёсток"},
        {"date": "05.12.2021", "amount": 564.0, "category": "Различные товары", "description": "Ozon.ru"},
        {"date": "31.12.2021", "amount": 160.89, "category": "Супермаркеты", "description": "Колхоз"},
    ]
    result = get_top_transactions(transactions_sample_2)
    assert result == expected_result


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates(mock_file, mock_get):
    mock_response_usd = Mock()
    mock_response_usd.status_code = 200
    mock_response_usd.json.return_value = {"rates": {"RUB": 95.0}}

    mock_response_eur = Mock()
    mock_response_eur.status_code = 200
    mock_response_eur.json.return_value = {"rates": {"RUB": 105.0}}

    mock_get.side_effect = [mock_response_usd, mock_response_eur]

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")

    result = get_currency_rates("test.json", date_obj)
    assert result == [{"currency": "USD", "rate": 95.0}, {"currency": "EUR", "rate": 105.0}]

    mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")
    mock_get.assert_called()


@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["USD", "EUR"]}')
def test_get_currency_rates_no_data(mock_file):
    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    result = get_currency_rates("test.json", date_obj)
    assert result == []


@patch("builtins.open", new_callable=mock_open, read_data='["USD", "EUR"]')
def test_get_currency_rates_not_dict(mock_file):
    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    result = get_currency_rates("test.json", date_obj)
    assert result == []


@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_currency_rates_not_found(mock_file):
    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    result = get_currency_rates("test.json", date_obj)
    assert result == []


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates_bad_request(mock_file, mock_get, capfd):
    mock_response = Mock()
    mock_response.status_code = 400

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    with pytest.raises(ValueError):
        get_currency_rates("test.json", date_obj)
        out, _ = capfd.readouterr()
        assert "Failed to get the currency rate. Status code: ValueError" in out


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates_no_rate(mock_file, mock_get, capfd):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {"RUB": None}}

    mock_get.return_value = mock_response

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")

    result = get_currency_rates("test.json", date_obj)
    assert result == []
    out, _ = capfd.readouterr()
    assert "Нет данных для USD на 2021-02-11" in out
    assert "Нет данных для EUR на 2021-02-11" in out


@patch("requests.get")
@patch("src.views.get_currency_rates")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AMZN", "GOOGL"]}')
def test_get_stock_prices(mock_file, mock_get_currency_rates, mock_get):
    mock_response_amzn = Mock()
    mock_response_amzn.status_code = 200
    mock_response_amzn.json.return_value = {"historical": [{"close": 255.63}]}

    mock_response_googl = Mock()
    mock_response_googl.status_code = 200
    mock_response_googl.json.return_value = {"historical": [{"close": 572.85}]}

    mock_get.side_effect = [mock_response_amzn, mock_response_googl]

    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 95.0}]

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")

    result = get_stock_prices("test.json", date_obj)
    assert result == [{"stock": "AMZN", "price": 24284.85}, {"stock": "GOOGL", "price": 54420.75}]

    mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")
    mock_get.assert_called()


@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["AMZN", "GOOGL"]}')
def test_get_stock_prices_no_data(mock_file):
    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    result = get_stock_prices("test.json", date_obj)
    assert result == []


@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_stock_prices_not_found(mock_file):
    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    result = get_stock_prices("test.json", date_obj)
    assert result == []


@patch("requests.get")
@patch("src.views.get_currency_rates")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AMZN", "GOOGL"]}')
def test_get_stock_prices_bad_request(mock_file, mock_get_currency_rates, mock_get, capfd):
    mock_response = Mock()
    mock_response.status_code = 400

    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 95.0}]

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")
    with pytest.raises(ValueError):
        get_stock_prices("test.json", date_obj)
        out, _ = capfd.readouterr()
        assert "Failed to get the stock price. Status code: ValueError" in out


@patch("requests.get")
@patch("src.views.get_currency_rates")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AMZN", "GOOGL"]}')
def test_get_stock_prices_no_stock(mock_file, mock_get_currency_rates, mock_get, capfd):
    mock_response_amzn = Mock()
    mock_response_amzn.status_code = 200
    mock_response_amzn.json.return_value = {"historical": [{"close": None}]}

    mock_response_googl = Mock()
    mock_response_googl.status_code = 200
    mock_response_googl.json.return_value = {"historical": [{"close": None}]}

    mock_get.side_effect = [mock_response_amzn, mock_response_googl]

    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 95.0}]

    date_obj = datetime.strptime("2021-02-11 23:05:55", "%Y-%m-%d %H:%M:%S")

    result = get_stock_prices("test.json", date_obj)
    assert result == []
    out, _ = capfd.readouterr()
    assert "Нет данных для AMZN на 2021-02-11" in out
    assert "Нет данных для GOOGL на 2021-02-11" in out


@patch(
    "src.views.get_currency_rates",
    return_value=[{"currency": "USD", "rate": 95.0}, {"currency": "EUR", "rate": 105.0}],
)
@patch(
    "src.views.get_stock_prices",
    return_value=[{"stock": "AMZN", "price": 24284.85}, {"stock": "GOOGL", "price": 54420.75}],
)
@patch(
    "src.views.get_top_transactions",
    return_value=[{"date": "01.12.2021", "amount": 20000.0, "category": "Переводы", "description": "Константин Л."}],
)
@patch("src.views.get_card_info", return_value=[{"last_digits": "4556", "total_spent": 1620.27, "cashback": 16.2}])
@patch("src.views.filter_transactions_date")
@patch("src.views.read_excel")
@patch("src.views.greeting", return_value="Доброе утро")
def test_main_page_fnc(
    mock_greeting,
    mock_read_excel,
    mock_filter_transactions,
    mock_get_card_info,
    mock_get_top_trans,
    mock_get_currency_rates,
    mock_get_stock_prices,
):
    mock_read_excel.return_value = Mock()
    mock_filter_transactions.return_value = Mock()

    date_string = "2021-02-11 08:30:00"
    expected_output = {
        "greeting": "Доброе утро",
        "cards": [{"last_digits": "4556", "total_spent": 1620.27, "cashback": 16.2}],
        "top_transactions": [
            {"date": "01.12.2021", "amount": 20000.0, "category": "Переводы", "description": "Константин Л."}
        ],
        "currency_rates": [{"currency": "USD", "rate": 95.0}, {"currency": "EUR", "rate": 105.0}],
        "stock_prices": [{"stock": "AMZN", "price": 24284.85}, {"stock": "GOOGL", "price": 54420.75}],
    }

    result_json = main_page_fnc(date_string)
    result_data = json.loads(result_json)
    assert result_data == expected_output
