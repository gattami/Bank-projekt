# starta bank (banktjänsterna)
from account import Account
from bank import Bank
from customer import Customer
from interest import Interest
from manager import Manager
from db import Db

# this is just usage examples of how to use the various methods in the bank.
def main():
    # create a new bank
    bank = Bank().create("Tres Banko", "2345") # return bank object
    # create a new customer
    customer = Customer().create("Bonjamin", "8001092456") # return customer object
    print(f"Kundens konton: {customer.accounts}")
    # add the customer to the bank we created (and add a personal account, which every new customer gets)
    bank.add_customer(customer)
    personal_account = customer.accounts[0]
    print(f"before personal dep {personal_account.get_balance()}")
    # make a deposit
    personal_account.deposit(200)
    print(f"after personal dep {personal_account.get_balance()}")
    # withdraw too much, should not change balance
    personal_account.withdraw(300)
    print(f"after personal overdraw attempt  {personal_account.get_balance()}")
    # withdraw half
    personal_account.withdraw(100)
    print(f"after personal withdraw half {personal_account.get_balance()}")
    # withdraw the outstanding balance (effectively zeroing the account)
    balance = personal_account.get_balance()
    personal_account.withdraw(balance)
    print(f"after personal withdraw outstanding {personal_account.get_balance()}")


    # also add a savings account
    # nr = Account.generate_nr() # 8064047892
    savings_account = bank.add_account(customer, "Savings_account", "8064047892")
    print(f"before savings dep {savings_account.get_balance()}")
    # make a deposit
    savings_account.deposit(300)
    print(f"after savings dep {savings_account.get_balance()}")
    # withdraw too much, should not change balance
    savings_account.withdraw(400)
    print(f"after savings overdraw attempt  {savings_account.get_balance()}")
    # withdraw a third
    savings_account.withdraw(100)
    print(f"after savings withdraw half {savings_account.get_balance()}")
    # withdraw the outstanding balance (effectively zeroing the account)
    balance = savings_account.get_balance()
    savings_account.withdraw(balance)
    print(f"after savings withdraw outstanding {savings_account.get_balance()}")

   # Växlingavgift tillämpning
    # Testfall 1: Transaktion i SEK (ingen avgift ska dras)
    print("Test 1: Transaktion i SEK")
    amount = 1000.0
    currency = "SEK"
    justerat_belopp_sek = Interest.apply(amount, currency)
    print(f"Ursprungligt belopp: {amount:.2f} {currency}")
    print(f"Justerat belopp: {justerat_belopp_sek:.2f} {currency}")
    # Förväntat resultat: 1000.00 SEK (ingen ändring)

    # Testfall 2: Transaktion i USD (avgift ska dras)
    print("Test 2: Transaktion i USD")
    amount = 500.0
    currency = "USD"
    justerat_belopp_usd = Interest.apply(amount, currency)
    print(f"Ursprungligt belopp: {amount:.2f} {currency}")
    print(f"Justerat belopp: {justerat_belopp_usd:.2f} {currency}")
    # Förväntat resultat: 500.00 - (500.00 * 0.02) = 490.00 USD

    # Testfall 3: Transaktion i GBP (avgift ska dras)
    print("Test 3: Transaktion i GBP")
    amount = 150.0
    currency = "GBP"
    justerat_belopp_gbp = Interest.apply(amount, currency)
    print(f"Ursprungligt belopp: {amount:.2f} {currency}")
    print(f"Justerat belopp: {justerat_belopp_gbp:.2f} {currency}")
    # Förväntat resultat: 150.00 - (150.00 * 0.02) = 147.00 GBP

    # Manager.approve_transaction
    # Testfall 1: En valuta som är godkänd (SEK)
    print("Test 1: Valuta 'SEK'")
    is_approved_sek = Manager.approve_transaction("SEK")
    print(f"Är 'SEK' godkänd? {is_approved_sek}")  # Förväntat: True

    # Testfall 2: En annan valuta som är godkänd (USD)
    print("Test 2: Valuta 'USD'")
    is_approved_usd = Manager.approve_transaction("USD")
    print(f"Är 'USD' godkänd? {is_approved_usd}")  # Förväntat: True

    # Testfall 3: En valuta som INTE är godkänd (JPY)
    print("Test 3: Valuta 'JPY'")
    is_approved_jpy = Manager.approve_transaction("JPY")
    print(f"Är 'JPY' godkänd? {is_approved_jpy}")  # Förväntat: False och få ett varningsmeddelande

    # Testfall 4: En annan valuta som INTE är godkänd (ZAR)
    print("Test 4: Valuta 'ZAR'")
    is_approved_zar = Manager.approve_transaction("ZAR")
    print(f"Är 'ZAR' godkänd? {is_approved_zar}")  # Förväntat: False och få ett varningsmeddelande

    # Testfall 5: Valuta med olika skiftläge (små bokstäver)
    print("Test 5: Valuta 'eur' (små bokstäver)")
    is_approved_eur_lower = Manager.approve_transaction("eur")
    print(f"Är 'eur' godkänd? {is_approved_eur_lower}")  # Förväntat: False eftersom listan bara har stora bokstäver


if __name__ == '__main__':
    main()