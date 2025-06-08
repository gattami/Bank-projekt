from db import Db
from interest import Interest
from manager import Manager

# Godkända valutor i systemet
KNOWN_CURRENCIES = ["SEK", "USD", "EUR", "GBP"]

class Transaction:

    def __init__(self):
        self.conn = Db().get_conn()

    def create(self, amount, account, currency="SEK"):
    # Skapar en ny transaktion om valutan är godkänd eller godkänd av en manager,och tillämpar växlingsavgift om nödvändigt.
        
        if currency not in KNOWN_CURRENCIES:
            print(f"[Warning] Currency '{currency}' is not approved.")
            if not Manager.approve_transaction(currency):
                print("[Transaction Blocked] Manager did not approve the transaction.")
                return None

        # Tillämpa växlingsavgift
        amount = Interest.apply(amount, currency)

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO transactions (amount, account_nr, currency) VALUES (%s, %s, %s)",[amount, account.nr, currency])
                self.conn.commit()
                print(f"Transaction of {amount} {currency} created successfully.")
        except Exception as e:
            print(f"[Error] Transaction failed: {e}")
            return None

        return amount
