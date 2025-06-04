import os
import pandas as pd

print("Aktuell arbetskatalog:", os.getcwd())

# Läser in CSV-filen
try:
    df = pd.read_csv("data/transactions.csv")
    print("✅ Filen har lästs in framgångsrikt!")
    print(df.head())
    print(f"\nDatans form: {df.shape}")
except FileNotFoundError:
    print("❌ Filen hittades inte. Kontrollera sökvägen: 'data/transactions.csv'")
except Exception as e:
    print(f"❌ Ett fel har inträffat: {e}")

