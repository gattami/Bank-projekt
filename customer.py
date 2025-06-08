  has accounts             → Kunden har kopplade konton
# can apply for an account → Kunden kan registreras med personuppgifter
# can borrow               → Antas via konton (t.ex. Account().borrow())
# can ask for credit       → Antas via konton med kreditlogik
# can try update personal info → Implementerat med update_personal_info()

from account import Account
from db import Db

class Customer:
    accounts = []

    def __init__(self):
        # Skapar databasanslutning från Db-klassen
        self.conn = Db().get_conn()

    def create(self, first_name, last_name, ssn, phone, address_id):
        """
       kan ansöka om konto
        Skapar en ny kund i databasen.
        Fångar upp fel om t.ex. SSN redan finns (dubblett).
        """
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO customers (first_name, last_name, ssn, phone, address_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [first_name, last_name, ssn, phone, address_id]
                )
                self.conn.commit()
                print(f"Customer '{first_name} {last_name}' created successfully.")
        except Exception as e:
            print(f"[Warning] Kunde inte skapa {first_name} {last_name}: {e}")

        # Returnerar kundobjektet efter skapandet
        return self.get_by_ssn(ssn)

    def get_by_ssn(self, ssn):
        """
        Hämtar kundinformation från databasen baserat på SSN.
        has accounts → Laddar även tillhörande konton.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE ssn = %s", [ssn])
        customer = cursor.fetchone()

        if customer:
            print("Customer loaded.")
            # Sätter kundens attribut
            self.id = customer[0]
            self.first_name = customer[1]
            self.last_name = customer[2]
            self.ssn = customer[3]
            self.phone = customer[4]
            self.address_id = customer[5]
            self.accounts = self.get_accounts()  # Ladda konton
            return self
        else:
            print(f"[Warning] Hittade ingen kund med ssn {ssn}")
            return None

    def get_accounts(self):
        """
        Hämtar alla konton kopplade till kunden.
        Returnerar en lista med Account-objekt.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE customer_id = %s", [self.id])
        account_rows = cursor.fetchall()
        accounts = []
        for row in account_rows:
            account_id = row[0]
            account = Account().get(account_id)
            if account:
                accounts.append(account)
        return accounts

    def update_personal_info(self, phone=None, address_id=None):
        """
         kan uppdatera uppgifter
        Tillåter uppdatering av telefonnummer och/eller adress_id.
        """
        try:
            with self.conn:
                cursor = self.conn.cursor()
                if phone:
                    cursor.execute("UPDATE customers SET phone = %s WHERE id = %s", [phone, self.id])
                if address_id:
                    cursor.execute("UPDATE customers SET address_id = %s WHERE id = %s", [address_id, self.id])
                self.conn.commit()
                print("Kundinformation uppdaterad.")
        except Exception as e:
            print(f"[Fel] Kunde inte uppdatera information: {e}")

