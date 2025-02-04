from src.services import investment_bank


def test_investment_bank(transactions_sample_3):
    expected_result = 98.79
    result = investment_bank("2018-02", transactions_sample_3, 50)
    assert result == expected_result


def test_investment_bank_sum_not_int(transactions_sample_4):
    expected_result = 73.79
    result = investment_bank("2018-02", transactions_sample_4, 50)
    assert result == expected_result


def test_investment_bank_invalid_dates(transactions_sample_5):
    expected_result = 49.4
    result = investment_bank("2018-02", transactions_sample_5, 50)
    assert result == expected_result


def test_investment_bank_invalid_amount(transactions_sample_6):
    expected_result = 98.4
    result = investment_bank("2018-02", transactions_sample_6, 50)
    assert result == expected_result
