import os

from src.decorators import log_result_into_file


def test_log_result_into_file():
    @log_result_into_file("results.txt")
    def my_function(x, y):
        return x + y

    my_function(25, 14)

    with open(os.path.join("logs", "results.txt"), "r", encoding="utf-8") as file:
        data = file.read().split("\n")

    assert data[-2] == "Результат: 39"
