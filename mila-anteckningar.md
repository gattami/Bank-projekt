
Affärslogistik: Kund och Transaktionshantering
────────────────────────────────────────────────────
Customer-Logik (fil: customer.py)

•	Fält som sparas: first_name, last_name, ssn, phone, address_id
•	Kopplad till tabellen customers.

- Kunden kan registrera sig i systemet med namn, personnummer (SSN), telefonnummer och adress.
- Varje kund kopplas till en eller flera konton (via accounts-tabellen).
- SSN används som unikt ID – dubbelregistrering förhindras.
- Kunden kan uppdatera sin information, t.ex. telefonnummer och adress.

 Affärsregler 
• has accounts              - En kund kan ha flera konton
• can apply for an account  - Kunden kan registreras och kopplas till ett konto
• can borrow               
• can ask for credit        - Antas via kontons kreditlogik
• can try update personal info - Kunden kan uppdatera telefonnummer eller adress


────────────────────────────────────────────────────
TRANSACTION-LOGIK (fil: transaction.py)

- Transaktioner skapas bara om valutan är godkänd.
- Om valutan är okänd → kräver manuell godkännande från Manager.
- En växlingsavgift tillämpas för utländska valutor via Interest.apply().
- Transaktionen loggas i databasen (tabellen transactions) med belopp, valuta och kontonummer.

Affärsregler som implementeras:
• Endast vissa valutor tillåts (SEK, USD, EUR, GBP)
• Alla andra valutor kräver godkännande från en Manager
• Växlingsavgift tillämpas om valutan  SEK
• Alla transaktioner bokförs i databasen via SQL

────────────────────────────────────────────────────

Datamodellen kopplar ihop:
• customers  → har adresser och konton
• accounts   → kopplade till customers
• transactions → kopplade till konton