# has accounts
# has customers
# can lend (from its own accounts)
# can transfer (to/from other banks)

from account import Account
from db import Db

class Bank:
    customers = []
    accounts = []

    def __init__(self):
        self.conn = Db().get_conn()

    def create(self, name, banknr):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO banks (name, banknr) VALUES (%s, %s)", [name, banknr])
                self.conn.commit()
                print(f"Bank '{name}' created successfully. Getting data.")
        except:
            print(f"[Warning] Bank with name {name} already exists. Getting data.")
        return self.get(banknr)

    def get(self, banknr):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM banks WHERE banknr = %s", [banknr])
        bank = cursor.fetchone()
        if(bank[0]):
            print(f"Bank loaded.")
            self.id = bank[0]
            self.name = bank[1]
            self.banknr = bank[2]
            return self
        else:
            print(f"[Warning] Bank with banknr {banknr} not found.")
            return None

    def add_customer(self, customer):
        self.customers.append(customer)
        self.add_account(customer, "Personal_account", customer.ssn) # add a personal account
        return customer

    def add_account(self, customer, type, nr):
        new_account = Account().create(customer, self, type, nr)
        self.accounts.append(new_account)
        customer.accounts.append(new_account)  # ←
        return new_account


    def importera_transaktioner(self, csv_filväg):
        import csv

        giltiga_rader = []

        with open(csv_filväg, newline='', encoding='utf-8') as csvfil:
            läsare = csv.DictReader(csvfil)
            for rad in läsare:
                try:
                    belopp = float(rad["amount"])
                    if belopp < 0 or not rad["account_id"] or not rad["date"]:
                        continue
                    giltiga_rader.append((
                        rad["account_id"],
                        rad["amount"],
                        rad["date"],
                        rad.get("description", "")
                    ))
                except:
                    continue

        try:
            with self.conn:
                cursor = self.conn.cursor()
                for rad in giltiga_rader:
                    cursor.execute(
                        """
                        INSERT INTO transactions (account_id, amount, date, description)
                        VALUES (%s, %s, %s, %s)
                        """,
                        rad
                    )
            print(f"✅ {len(giltiga_rader)} transaktioner har importerats korrekt.")
        except Exception as fel:
            self.conn.rollback()
            print("❌ Ett fel uppstod vid import. Rollback har körts.")
            print(fel)


if __name__ == "__main__":
    bank = Bank()
    bank = bank.create("Tres Banko", "2345")
    bank.importera_transaktioner("python-bank-project-start-main/data/transactions.csv")
