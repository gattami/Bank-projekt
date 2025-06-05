from prefect import flow, task
import pandas as pd
from sqlalchemy import create_engine, text
import os
import re

# Anslutningssträng till databasen
DB_URL = "postgresql://postgres:varpinge93@localhost:4455/postgres"

# Sökvägar till CSV-filerna
CUSTOMERS_CSV = "data/sebank_customers_with_accounts_original.csv"
TRANSACTIONS_CSV = "data/transactions_original.csv"

# Standardisera telefonnummer

def clean_phone_number(phone: str) -> str | None:
    if pd.isna(phone):
        return None
    phone = re.sub(r"[^\d+]", "", phone)
    phone = re.sub(r"^00", "+", phone)
    if phone.startswith("0"):
        phone = "+46" + phone[1:]
    if phone.startswith("46") and not phone.startswith("+"):
        phone = "+" + phone
    if not re.fullmatch(r"\+\d{9,}", phone):
        return None
    return phone

# Läs in kunddata från CSV
@task
def import_csv(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path, dtype=str)
        print(f"{csv_path}: {len(df)} rader importerade")
        return df
    except Exception as e:
        print(f"Fel vid läsning av {csv_path}: {e}")
        return pd.DataFrame()

# Läs in och förbered transaktionsdata
@task
def import_transactions(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path, dtype=str)
        df["amount"] = df["amount"].replace(",", ".", regex=True).astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["transaction_id", "timestamp", "amount"])
        print(f"{csv_path}: {len(df)} transaktioner importerade")
        return df
    except Exception as e:
        print(f"Fel vid import av transaktioner: {e}")
        return pd.DataFrame()

# Rensa och normalisera kunddata
@task
def clean_and_normalize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = df.rename(columns={
        "Customer": "name",
        "Address": "street_raw",
        "Phone": "phone_raw",
        "Personnummer": "ssn_raw",
        "BankAccount": "bank_account"
    })
    df = df.drop_duplicates().dropna(subset=["name", "ssn_raw"])

    for col in ["name", "street_raw", "phone_raw", "ssn_raw", "bank_account"]:
        df[col] = df[col].astype(str).str.strip()

    df["first_name"] = df["name"].str.split().str[0]
    df["last_name"] = df["name"].str.split().str[1:].str.join(" ")

    df["ssn_digits"] = df["ssn_raw"].str.replace(r"\D", "", regex=True)
    df["yy"] = df["ssn_digits"].str.slice(0, 2).astype(int)
    current_two_digit = pd.Timestamp.now().year % 100

    def expand_ssn(row):
        prefix = "19" if row["yy"] > current_two_digit else "20"
        return prefix + row["ssn_digits"]

    df["ssn"] = df.apply(expand_ssn, axis=1)
    df = df.drop(columns=["ssn_raw", "ssn_digits", "yy", "name"])

    df["phone"] = df["phone_raw"].apply(clean_phone_number)
    df = df.drop(columns=["phone_raw"])

    df[["street", "zip_city"]] = df["street_raw"].str.split(",", n=1, expand=True)
    df["zip_code"] = df["zip_city"].str.extract(r"(\d{5})")
    df["city"] = df["zip_city"].str.replace(r"\d{5}", "", regex=True).str.strip()
    df = df.drop(columns=["street_raw", "zip_city"])

    addresses_df = df[["street", "zip_code", "city"]].drop_duplicates().reset_index(drop=True)
    addresses_df["id"] = addresses_df.index + 1
    addresses_df = addresses_df[["id", "street", "zip_code", "city"]]

    df = df.merge(addresses_df, on=["street", "zip_code", "city"], how="left")
    df = df.rename(columns={"id": "address_id"})

    customers_df = df[["first_name", "last_name", "ssn", "phone", "address_id"]].drop_duplicates(subset=["ssn"]).reset_index(drop=True)
    customers_df["id"] = customers_df.index + 1
    customers_df = customers_df[["id", "first_name", "last_name", "ssn", "phone", "address_id"]]

    accounts_temp = df[["ssn", "bank_account"]].drop_duplicates().reset_index(drop=True)
    accounts_df = accounts_temp.merge(customers_df[["id", "ssn"]].rename(columns={"id": "customer_id"}), on="ssn", how="left")
    accounts_df["id"] = accounts_df.index + 1
    accounts_df = accounts_df[["id", "customer_id", "bank_account"]]

    return customers_df, addresses_df, accounts_df

# Skapa tabellen transactions om den inte finns
@task
def create_transactions_table():
    ddl = """
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        transaction_id UUID UNIQUE,
        timestamp TIMESTAMP,
        amount NUMERIC(15, 2),
        currency TEXT,
        sender_account TEXT,
        receiver_account TEXT,
        sender_country TEXT,
        sender_municipality TEXT,
        receiver_country TEXT,
        receiver_municipality TEXT,
        transaction_type TEXT,
        notes TEXT
    );
    """
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text(ddl))
            print(" Tabell 'transactions' skapad (eller fanns redan).")
    except Exception as e:
        print(f" Fel vid skapande av tabell 'transactions': {e}")

# Ladda upp DataFrame till databasen
@task
def write_to_postgres(df: pd.DataFrame, table_name: str, db_url: str):
    if df.empty:
        print(f"{table_name}: Ingen data att ladda upp")
        return
    try:
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"{table_name}: {len(df)} rader laddades upp ✅")
    except Exception as e:
        print(f"Fel vid uppladdning till {table_name}: {e}")

# Själva flödet (ETL-processen)
@flow
def load_data_flow():
    if os.path.exists(CUSTOMERS_CSV):
        df = import_csv(CUSTOMERS_CSV)
        customers_df, addresses_df, accounts_df = clean_and_normalize(df)
        write_to_postgres(addresses_df, "addresses", DB_URL)
        write_to_postgres(customers_df, "customers", DB_URL)
        write_to_postgres(accounts_df, "accounts", DB_URL)
    else:
        print(f"{CUSTOMERS_CSV} hittades inte")

    create_transactions_table()

    if os.path.exists(TRANSACTIONS_CSV):
        transactions_df = import_transactions(TRANSACTIONS_CSV)
        write_to_postgres(transactions_df, "transactions", DB_URL)
    else:
        print(f"{TRANSACTIONS_CSV} hittades inte")





if __name__ == "__main__":
    load_data_flow()
