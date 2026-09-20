transactions = [
    {
        "id": 939719570,
        "state": "EXECUTED",
        "date": "2018-06-30T02:08:58.425572",
        "operationAmount": {
            "amount": "9824.07",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод организации",
        "from": "Счет 75106830613657916952",
        "to": "Счет 11776614605963066702",
    },
    {
        "id": 142264268,
        "state": "EXECUTED",
        "date": "2019-04-04T23:20:05.206878",
        "operationAmount": {
            "amount": "79114.93",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод со счета на счет",
        "from": "Счет 19708645243227258542",
        "to": "Счет 75651667383060284188",
    },
    {
        "id": 873106923,
        "state": "EXECUTED",
        "date": "2019-03-23T01:09:46.296404",
        "operationAmount": {
            "amount": "43318.34",
            "currency": {"name": "руб.", "code": "RUB"},
        },
        "description": "Перевод со счета на счет",
        "from": "Счет 44812258784861134719",
        "to": "Счет 74489636417521191160",
    },
    {
        "id": 895315941,
        "state": "EXECUTED",
        "date": "2018-08-19T04:27:37.904916",
        "operationAmount": {
            "amount": "56883.54",
            "currency": {"name": "USD", "code": "USD"},
        },
        "description": "Перевод с карты на карту",
        "from": "Visa Classic 6831982476737658",
        "to": "Visa Platinum 8990922113665229",
    },
    {
        "id": 594226727,
        "state": "CANCELED",
        "date": "2018-09-12T21:27:25.241689",
        "operationAmount": {
            "amount": "67314.70",
            "currency": {"name": "руб.", "code": "RUB"},
        },
        "description": "Перевод организации",
        "from": "Visa Platinum 1246377376343588",
        "to": "Счет 14211924144426031657",
    },
]


def filter_by_currency(transactions, currency_code):
    for tx in transactions:
        if (
            "operationAmount" in tx
            and "currency" in tx["operationAmount"]
            and "code" in tx["operationAmount"]["currency"]
            and tx["operationAmount"]["currency"]["code"] == currency_code
        ):
            yield tx


# Создаём генератор
usd_transactions_gen = filter_by_currency(transactions, "USD")


# Используем генератор — просто берём первые два элемента
print(next(usd_transactions_gen))  # Первое описание
print(next(usd_transactions_gen))  # Второе описание
print(next(usd_transactions_gen))  # 3 описание


def transaction_descriptions(transactions):
    for transaction in transactions:
        yield f"{transaction['description']}"


descriptions = transaction_descriptions(transactions)

for _ in range(5):
    print(next(descriptions))


def card_number_generator(start: int, stop: int, mode: str = "sequential"):
    """
    Генератор номеров банковских карт.

    Args:
        start (int): Начальное значение диапазона (включительно).
        stop (int): Конечное значение диапазона (включительно).
        mode (str): Режим генерации:
            - "sequential": 1 → 0000 0000 0000 0001
            - "pattern": 9999 → 9999 9999 9999 9999

    Yields:
        str: Номер карты в формате 'XXXX XXXX XXXX XXXX'.

    Raises:
        ValueError: Если start > stop или mode указан неверно.
    """
    if start > stop:
        raise ValueError("Значение start должно быть меньше или равно значению stop")

    if mode not in ("sequential", "pattern"):
        raise ValueError("mode должен быть 'sequential' или 'pattern'")

    for number in range(start, stop + 1):
        if mode == "sequential":
            number_str = str(number).zfill(16)
            formatted_number = f"{number_str[0:4]} {number_str[4:8]} {number_str[8:12]} {number_str[12:16]}"
        else:  # mode == "pattern"
            block = str(number)[-4:].zfill(4)
            formatted_number = f"{block} {block} {block} {block}"

        yield formatted_number



if __name__ == "__main__":
    for card in card_number_generator(9999, 9999, mode="pattern"):
        print(card)
