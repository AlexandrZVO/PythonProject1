from typing import Dict, List


def filter_by_state(store: list, state: str = "EXECUTED") -> list:
    """Фильтрует список словарей, оставляя только те, у которых ключ 'state' равен значению `state`."""
    result = []
    for item in store:
        if item.get("state") == state:  # Используем get() для безопасности
            result.append(item)
    return result


print(
    filter_by_state(
        [
            {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
            },
            {
                "id": 594226727,
                "state": "CANCELED",
                "date": "2018-09-12T21:27:25.241689",
            },
            {
                "id": 615064591,
                "state": "CANCELED",
                "date": "2018-10-14T08:21:33.419441",
            },
        ]
    )
)


# from datetime import datetime
# from typing import Dict, List


def sort_by_date(data: List[Dict], reverse: bool = False) -> List[Dict]:
    """функцию, которая принимает список словарей и возвращать новый список, отсортированный по дате"""
    sorted_data = sorted(data, key=lambda x: x["date"], reverse=reverse)
    return sorted_data


print(
    [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]
)
