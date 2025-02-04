# **Term_project_#1 - Анализ финансовых транзакций**

## **Описание**:

Этот проект предоставляет набор инструментов для:

- Анализа финансовых транзакций
- Мониторинга курсов валют и акций
- Учета инвестиций в "Инвесткопилку"
- Генерации отчетов по тратам

Проект объединяет несколько сервисов, позволяя работать с транзакциями, 
проводить финансовый анализ и получать полезные отчеты.

## **Установка**:

1. Клонируйте репозиторий

```
git@github.com:Alexandra-Chigrina/term_project_1.git
```

2. В терминале инициализируйте Poetry и активируйте виртуальное окружение

```
poetry init
poetry shell
```

3. Установите зависимости

```
pip install -r requirements.txt
```

## **Использование**:

1. Запуск основного модуля.

   Запустите скрипты из модуля main.py в корне репозитория. 
   Модуль main.py связывает все функциональности проекта, вызывая ключевые функции.

```commandline
python main.py
```

2. Описание основных функций

* Функция `main_page_fnc` в модуле src/views.py формирует JSON-ответ с:
  - приветствием пользователя на основе времени суток;
  - информацией о картах и тратах;
  - топ-5 транзакциями за указанный период;
  - курсами валют;
  - ценами на акции.

* Функция `investment_bank` в модуле src/services.py рассчитывает сумму,
   отправляемую в "Инвесткопилку" с округлением платежей.


* Функция `spending_by_category` в модуле src/reports.py анализирует расходы 
   по заданной категории за последние 3 месяца.


## **Примеры работы**:

1. Пример вызова`main_page_fnc`:
```commandline
result_json = main_page_fnc("2021-02-11 08:30:00")
print(result_json)
```
`Результат
{
    "greeting": "Доброй ночи",
    "cards": [
        {
            "last_digits": "4556",
            "total_spent": 1199.6,
            "cashback": 12.0
        },
        {
            "last_digits": "7197",
            "total_spent": 6168.47,
            "cashback": 61.68
        }
    ],
    "top_transactions": [
        {
            "date": "10.02.2021",
            "amount": 85000.0,
            "category": "Переводы",
            "description": "Николай Н."
        },
        {
            "date": "02.02.2021",
            "amount": 700.0,
            "category": "Транспорт",
            "description": "Метро Санкт-Петербург"
        },
        {
            "date": "07.02.2021",
            "amount": 599.8,
            "category": "Ж/д билеты",
            "description": "РЖД"
        },
        {
            "date": "08.02.2021",
            "amount": 599.8,
            "category": "Ж/д билеты",
            "description": "РЖД"
        },
        {
            "date": "07.02.2021",
            "amount": 540.0,
            "category": "Супермаркеты",
            "description": "IP Gorskaya Vv"
        }
    ],
    "currency_rates": [
        {
            "currency": "USD",
            "rate": 73.67
        },
        {
            "currency": "EUR",
            "rate": 89.37
        }
    ],
    "stock_prices": [
        {
            "stock": "AAPL",
            "price": 9955.03
        },
        {
            "stock": "AMZN",
            "price": 12016.31
        },
        {
            "stock": "GOOGL",
            "price": 7694.09
        },
        {
            "stock": "MSFT",
            "price": 18011.58
        },
        {
            "stock": "TSLA",
            "price": 19931.42
        }
    ]
}
`
2. Пример вызова `investment_bank`:
```commandline
result = investment_bank("2022-06", transactions, 50)
print(result
```
`Результат:
3262.0
`

3. Пример вызова `spending_by_category`:
```commandline
result = spending_by_category(transactions_df, "Продукты", "2023-01-01")
print(result)
```
`Результат:
[
    {
        "Категория": "Переводы",
        "Сумма платежа": 259954.69
    }
]
`


## **Тестирование**

1. Установите pytest через Poetry

```
poetry add --group dev pytest
```

2. Запустить тестрование можно из модулей 'test_name', находящихся в папке 'tests' или в терминале

```
pytest
```

3. Для анализа покрытия кода тестами установите библиотеку 'pytest-cov'

```commandline
poetry add --group dev pytest-cov
```

4. Запустите тесты с оценкой покрытия

```commandline
pytest --cov=src --cov-report=term-missing tests/
```
5. Пример тестирования `investment_bank`:
```commandline
def test_investment_bank():
    transactions = [
        {"Дата операции": "2022-06-01", "Сумма платежа": -48.5, "Статус": "OK"},
        {"Дата операции": "2022-06-15", "Сумма платежа": -120.75, "Статус": "OK"},
    ]
    assert investment_bank("2022-06", transactions, 50) == 30.76
```

## **Структура проекта**

├── src/                    # Основной код
│   ├── views.py            # Основные функции
│   ├── services.py         # Функции реализации сервисов
│   ├── reports.py          # Функции реализации отчетов
│   ├── utils.py            # Утилиты (чтение файлов, фильтрация и т. д.)
│   ├── decorators.py       # Декоратор логирования
├── data/                   # Данные
│   ├── operations.xlsx     # Данные о финансовых операциях
├── tests/                  # Тесты
│   ├── test_views.py       # Тесты для views.py
│   ├── test_reports.py     # Тесты для reports.py
│   ├── test_decorators.py  # Тесты для decorators.py
│   ├── test_services.py    # Тесты для services.py
│   ├── test_utils.py       # Тесты для utils.py
├── logs/                   # Логи выполнения
│   ├── investment_results.log
│   ├── reports.log
│   ├── services.log
│   ├── views.log
├── main.py                 # Основная логика
├── user_settings.json      # Файл пользовательских настроек
├── .venv                   # Виртуальное окружение
├── .env                    # Файл переменных окружения
├── .env_template           # Шаблоны .env
├── .git/                   # Git-репозиторий
├── .gitignore              # Исключения файлов из Git
├── .config.py              # Файл конфигурации
├── .flake8                 # Настройки линтера Flake8
├── .coverage               # Отчеты покрытия кода тестами
├── .poetry.lock            # Фиксированные зависимости проекта
├── .pyproject.toml         # Основной конфигурационный файл проекта
├── README.md               # Документация
