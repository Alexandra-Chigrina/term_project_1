from config import PATH_TO_OPERATIONS
from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import convert_excel_into_list, read_excel
from src.views import main_page_fnc

df_transactions = read_excel(PATH_TO_OPERATIONS)
transactions_list = convert_excel_into_list(PATH_TO_OPERATIONS)
print(main_page_fnc("2021-02-11 23:05:55"))
print(investment_bank("2021-02", transactions_list, 50))
print(spending_by_category(df_transactions, "Супермаркеты", "2021-02-11"))
