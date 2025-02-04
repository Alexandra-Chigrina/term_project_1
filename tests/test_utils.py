from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import convert_excel_into_list, greeting, read_excel


@pytest.mark.parametrize(
    "my_hour, my_minute, expected",
    [
        (23, 5, "Доброй ночи"),
        (4, 22, "Доброй ночи"),
        (7, 43, "Доброе утро"),
        (14, 00, "Добрый день"),
        (19, 10, "Добрый вечер"),
    ],
)
def test_greeting(my_hour, my_minute, expected):
    assert greeting(my_hour, my_minute) == expected


def test_greeting_type_error():
    with pytest.raises(TypeError):
        greeting("10", 45)


def test_greeting_value_error_1():
    with pytest.raises(ValueError):
        greeting(25, 45)


def test_greeting_value_error_2():
    with pytest.raises(ValueError):
        greeting(20, -45)


@patch("pandas.read_excel")
def test_read_excel(mock_read_excel):
    mock_data = pd.DataFrame(
        {"Дата операции": ["31.12.2021 14:05:47", "20.04.2019 15:01:50"], "Сумма платежа": ["-160.89", "2100,00"]}
    )
    mock_read_excel.return_value = mock_data
    data = read_excel("test.xlsx")
    assert data.equals(mock_data)


@patch("pandas.read_excel", side_effect=FileNotFoundError)
def test_read_excel_no_file(mock_read_excel):
    mock_read_excel.return_value = pd.DataFrame()
    data = read_excel("test.xlsx")
    assert data.empty


@patch("pandas.read_excel", side_effect=ValueError)
def test_read_excel_error(mock_read_excel):
    mock_read_excel.return_value = pd.DataFrame()
    data = read_excel("test.xlsx")
    assert data.empty


@patch("pandas.read_excel")
def test_convert_excel_into_list(mock_read_excel):
    mock_data = pd.DataFrame(
        {"Дата операции": ["31.12.2021 14:05:47", "20.04.2019 15:01:50"], "Сумма платежа": [-160.89, 2100.00]}
    )
    mock_read_excel.return_value = mock_data

    data_dict = convert_excel_into_list("test.xlsx")
    assert data_dict == [
        {"Дата операции": "2021-12-31", "Сумма платежа": -160.89},
        {"Дата операции": "2019-04-20", "Сумма платежа": 2100.00},
    ]


@patch("pandas.read_excel", side_effect=FileNotFoundError)
def test_convert_excel_into_list_no_file(mock_read_excel):
    mock_read_excel.return_value.to_dict.return_value = []
    data_dict = convert_excel_into_list("test.xlsx")
    assert data_dict == []


@patch("pandas.read_excel", side_effect=ValueError)
def test_convert_excel_into_list_error(mock_read_excel):
    mock_read_excel.return_value.to_dict.return_value = []
    data_dict = convert_excel_into_list("test.xlsx")
    assert data_dict == []


@patch("pandas.read_excel")
def test_convert_excel_into_list_string_date(mock_read_excel):
    mock_data = pd.DataFrame({"Дата операции": ["2021-12-31", "2019-04-20"], "Сумма платежа": [-160.89, 2100.00]})
    mock_read_excel.return_value = mock_data
    data_dict = convert_excel_into_list("test.xlsx", False)
    assert data_dict == [
        {"Дата операции": "2021-12-31", "Сумма платежа": -160.89},
        {"Дата операции": "2019-04-20", "Сумма платежа": 2100.00},
    ]
