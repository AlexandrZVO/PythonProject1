from io import StringIO

from src.main import (filter_by_status, filter_currency, load_csv, safe_float,
                      search_operations, sort_transactions)


# --- Тесты чистых функций (дают быстрый прирост покрытия) ---
def test_safe_float_valid():
    assert safe_float(10) == 10.0
    assert safe_float("10,5") == 10.5
    assert safe_float("10.5") == 10.5


def test_safe_float_invalid():
    assert safe_float(None) == 0.0
    assert safe_float("") == 0.0
    assert safe_float("abc") == 0.0


def test_filter_by_status_valid():
    txs = [
        {"id": 1, "status": "EXECUTED"},
        {"id": 2, "state": "PENDING"},
        {"id": 3, "status": "UNKNOWN"},
    ]
    filtered = filter_by_status(txs, "EXECUTED")
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1


def test_filter_by_status_invalid():
    txs = [{"id": 1, "status": "EXECUTED"}]
    filtered = filter_by_status(txs, "INVALID")
    assert len(filtered) == 0


def test_filter_currency_valid():
    txs = [
        {
            "id": 1,
            "operationAmount": {"amount": 100, "currency": {"code": "RUB"}},
        },
        {
            "id": 2,
            "operationAmount": {"amount": 200, "currency": {"code": "USD"}},
        },
    ]
    filtered = filter_currency(txs, "RUB")
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1


def test_sort_transactions_ascending():
    txs = [
        {"id": 1, "date": "2024-03-01"},
        {"id": 2, "date": "2024-01-01"},
        {"id": 3, "date": "2024-02-01"},
    ]
    sorted_txs = sort_transactions(txs, ascending=True)
    dates = [t["date"] for t in sorted_txs]
    assert dates == ["2024-01-01", "2024-02-01", "2024-03-01"]


def test_sort_transactions_descending():
    txs = [
        {"id": 1, "date": "2024-03-01"},
        {"id": 2, "date": "2024-01-01"},
        {"id": 3, "date": "2024-02-01"},
    ]
    sorted_txs = sort_transactions(txs, ascending=False)
    dates = [t["date"] for t in sorted_txs]
    assert dates == ["2024-03-01", "2024-02-01", "2024-01-01"]


def test_search_operations_match():
    txs = [
        {"id": 1, "description": "Покупка продуктов"},
        {"id": 2, "description": "Перевод другу"},
    ]
    result = search_operations(txs, "покупка")
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_search_operations_no_match():
    txs = [
        {"id": 1, "description": "Оплата связи"},
        {"id": 2, "description": "Такси"},
    ]
    result = search_operations(txs, "продукты")
    assert len(result) == 0


def test_load_csv_empty():
    csv_data = StringIO("id;state;date;amount;currency_code;description\n")
    transactions = load_csv(csv_data)
    assert len(transactions) == 0
