from prefect import flow, task
import pandas as pd
from sqlalchemy import create_engine
import os

DB_URL = "postgresql://postgres:Pakistan33@localhost:5432/postgres"

CSV_TABLE_PAIRS = [
    ("data/sebank_customers_with_accounts.csv", "sebank_customers"),
    ("data/sebank_customers_with_accounts_original.csv", "sebank_customers_original"),
    ("data/transactions.csv", "transactions"),
    ("data/transactions_original.csv", "transactions_original"),
]

@task
def import_csv(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
        print(f"{csv_path}: {len(df)} rader importerade")
        return df
    except Exception as e:
        print(f"Fel vid läsning av {csv_path}: {e}")
        return pd.DataFrame()

@task
def write_to_postgres(df: pd.DataFrame, table_name: str, db_url: str):
    if df.empty:
        print(f"{table_name}: Tom eller ogiltig data – inget importerat")
        return
    try:
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, if_exists='replace', index=False, method='multi')
        print(f"{table_name}: Inläst till databas")
    except Exception as e:
        print(f"Fel vid skrivning till {table_name}: {e}")

@flow
def load_data_flow():
    for csv_path, table_name in CSV_TABLE_PAIRS:
        if os.path.exists(csv_path):
            df = import_csv(csv_path)
            write_to_postgres(df, table_name, DB_URL)
        else:
            print(f"{csv_path} hittades inte")

if __name__ == "__main__":
    load_data_flow()
