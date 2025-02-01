import json

from src.reports import spending_by_category


def test_spending_by_category(transactions_sample_2):
    expected_result = [{"Категория": "Супермаркеты", "Сумма платежа": 279.01}]
    result = spending_by_category(transactions_sample_2, "Супермаркеты", "2022-03-06")
    final_result = json.loads(result)
    assert final_result == expected_result


def test_spending_by_category_incorrect_date(transactions_sample_2):
    expected_result = "Неверный формат даты. Используйте YYYY-MM-DD"
    result = spending_by_category(transactions_sample_2, "Супермаркеты", "06-03-2022")
    assert result == expected_result


def test_spending_by_category_no_data(transactions_sample_2):
    expected_result = "Нет данных по категории 'Фастфуд' за указанный период"
    result = spending_by_category(transactions_sample_2, "Фастфуд", "2022-03-06")
    assert result == expected_result


def test_spending_by_category_no_date(transactions_sample_2):
    expected_result = "Нет данных по категории 'Супермаркеты' за указанный период"
    result = spending_by_category(transactions_sample_2, "Супермаркеты")
    assert result == expected_result
