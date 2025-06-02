# Bankprojekt Anteckningar

## 1. GX-testning på transkations.CSV-filen (Före import till databas)
pip install great_expectations

### Mål: Säkerställa att den inkommande CSV-filen är tillräckligt "ren" för att kunna importeras till databasen.
### Antaganden Jag har skapat ett test med Great Expectations (GX) för att verifiera att CSV-filen följer rätt struktur och innehåller korrekt data. 
### Syftet är att automatiskt kontrollera datakvaliteten för transaktionsdata innan den migreras till databasen.
### Jag säkerställer att:
- Alla nödvändiga kolumner finns med.
- Viktiga fält inte innehåller null-värden.
- Datatyperna är korrekta (t.ex. amount är av typen float, transaction_id är en sträng).
- Vissa affärsregler följs, t.ex. att transaction_id är unikt och att currency innehåller endast godkända värden (t.ex. SEK, USD, EUR, GBP).

### Ej null-värden för viktiga kolumner
validator.expect_column_values_to_not_be_null("transaction_id")
validator.expect_column_values_to_not_be_null("timestamp")
validator.expect_column_values_to_not_be_null("amount")
validator.expect_column_values_to_not_be_null("currency")
validator.expect_column_values_to_not_be_null("sender_account")
validator.expect_column_values_to_not_be_null("receiver_account")
validator.expect_column_values_to_not_be_null("sender_country")
validator.expect_column_values_to_not_be_null("transaction_type")

### testa mot datatyper: object (str)
validator.expect_column_values_to_be_of_type("transaction_id", "object") # uuid som sträng
validator.expect_column_values_to_be_of_type("timestamp", "object") # Eller "datetime"
validator.expect_column_values_to_be_of_type("amount", "float64") # Kan vara float
validator.expect_column_values_to_be_of_type("currency", "object")
validator.expect_column_values_to_be_of_type("sender_account", "object")
validator.expect_column_values_to_be_of_type("receiver_account", "object")
validator.expect_column_values_to_be_of_type("sender_country", "object")
validator.expect_column_values_to_be_of_type("receiver_country", "object")
validator.expect_column_values_to_be_of_type("transaction_type", "object")
validator.expect_column_values_to_be_of_type("notes", "object")

### Specifika affärsregler/format
validator.expect_column_values_to_be_unique("transaction_id") # Transaktions-ID bör vara unikt
validator.expect_column_distinct_values_to_be_in_set("currency", ["SEK", "USD", "EUR", "GBP"]) # Kända valutor

### Jag använder GX för att skapa automatiserade kontroller (”förväntningar”) vilket möjliggör tidig upptäckt av fel och säkerställer hög datakvalitet genom hela processen.

### Tolkning Resultat: 

Great Expectations-valideringen av CSV-fil misslyckades. Av 22 definierade förväntningar var 20 framgångsrika, men två förväntningar misslyckades.
Specifika problem:

1.	Valutor (currency): jag förväntade mig att currency-kolumnen endast skulle innehålla "SEK", "USD", "EUR", "GBP". Men det innehåller andra valutor som "DKK", "JPY", "NOK", "RMB", "ZAR", "ZMW".
2.	Avsändarland (sender_country): att sender_country-kolumnen inte skulle innehålla några saknade (NULL) värden. Det finns 500 rader (0.5% av datan) där sender_country är NULL.

## 2. skapa class interest för att tillämpa växlingavgift för främmande valutor 

*Resultat genom app.py köras:*

> Test 1: Transaktion i SEK
Ursprungligt belopp: 1000.00 SEK
Justerat belopp: 1000.00 SEK
Test 2: Transaktion i USD
Applied exchange fee of 10.0 for currency USD
Ursprungligt belopp: 500.00 USD
Justerat belopp: 490.00 USD
Test 3: Transaktion i GBP
Applied exchange fee of 3.0 for currency GBP
Ursprungligt belopp: 150.00 GBP
Justerat belopp: 147.00 GBP

## 3. skapa class manager för att validera valutor som inte är kända valutor (t.ex. ["SEK", "USD", "EUR", "GBP"] )

*Resultat genom app.py köras:*

> Test 1: Valuta 'SEK'
Är 'SEK' godkänd? True
Test 2: Valuta 'USD'
Är 'USD' godkänd? True
Test 3: Valuta 'JPY'
[Manager Required] Godkännande behövs för valutan 'JPY'.
Är 'JPY' godkänd? False
Test 4: Valuta 'ZAR'
[Manager Required] Godkännande behövs för valutan 'ZAR'.
Är 'ZAR' godkänd? False
Test 5: Valuta 'eur' (små bokstäver)
[Manager Required] Godkännande behövs för valutan 'eur'.
Är 'eur' godkänd? False

## 4. Pydantic-validering i transaktionssystem

**Syfte** Använda Pydantic för att säkerställa att endast korrekta och Förhindrar att ogiltiga belopp eller felaktigt formaterade valutor bearbetas.

*pydantic_interest.py*

Använde @validate_call från Pydantic för att validera argumenten:
- amount måste vara av typen Decimal och vara större än 0.
- currency måste vara en sträng med exakt tre stora bokstäver (regex-validering).

> Tips! Decimal används i stället för float för att undvika avrundningsfel i finansiella beräkningar.

*pydantic_manager.py*

Använde @validate_call med Field(..., pattern=...) för att kontrollera att valutakoden är exakt tre stora bokstäver (t.ex. USD, EUR).

> Tydliga felrapporter: Vid ogiltig valuta (t.ex. "us", "EURO", "SE K"), visas detaljerade felmeddelanden direkt.