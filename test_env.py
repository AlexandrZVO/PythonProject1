import os

from dotenv import load_dotenv

print(f"📁 Текущая папка: {os.getcwd()}")

load_dotenv()
key = os.getenv("APILAYER_API_KEY")

if key:
    print(f" Ключ успешно загружен! Длина: {len(key)} символов.")
else:
    print(" Ключ НЕ найден.")
    print("Проверь:")
    print("  1. Файл .env лежит именно в этой папке (рядом с src/).")
    print("  2. Внутри .env строка выглядит так: APILAYER_API_KEY=твой_ключ (без кавычек и пробелов вокруг знака =)")
