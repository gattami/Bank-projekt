import os
import pandas as pd

print("Текущая директория запуска:", os.getcwd())

# Загружаем CSV-файл
try:
    df = pd.read_csv("data/transactions.csv")
    print("✅ Файл загружен успешно!")
    print(df.head())
    print(f"\nФорма данных: {df.shape}")
except FileNotFoundError:
    print("❌ Файл не найден. Проверь путь: 'data/transactions.csv'")
except Exception as e:
    print(f"❌ Произошла ошибка: {e}")
