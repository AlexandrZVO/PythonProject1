"""Точка входа."""

from external_api import convert_to_rub
from utils import load_transactions

if __name__ == "__main__":
    transactions = load_transactions("data/operations.json")

    if not transactions:
        print("️ Файл пуст или не найден.")
    else:
        print(f" Загружено транзакций: {len(transactions)}\n")
        for tx in transactions:
            # Поля могут называться по-разному в зависимости от формата файла
            # Адаптируй под свой operations.json
            amount = tx.get("operationAmount", {}).get("amount", 0)
            currency = tx.get("operationAmount", {}).get("currency", {}).get("code", "RUB")
            tx_id = tx.get("id", "?")
            description = tx.get("description", "Без описания")

            rub = convert_to_rub(float(amount), currency)
            if rub > 0:
                print(f" #{tx_id} {description}: {amount} {currency} → {rub} RUB")
            else:
                print(f" #{tx_id} {description}: не удалось конвертировать")
