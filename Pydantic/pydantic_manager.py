from pydantic import validate_call, Field 

class Manager:

    # Här definierar vi vilka valutor som är "automatiskt godkända".
    APPROVED_CURRENCIES = ["SEK", "USD", "EUR", "GBP"]

    @staticmethod
    @validate_call # Pydantic-dekoratör: Validerar argumenten innan metoden körs.
    def approve_transaction(currency: str = Field(..., pattern=r"^[A-Z]{3}$")) -> bool:
        
    
        if currency.upper() not in Manager.APPROVED_CURRENCIES: # Använd .upper() för skiftlägesokänslig
            # Om valutan INTE finns i listan, betyder det att den är okänd för chefen.
            # Vi skriver ut ett meddelande för att informera om att godkännande behövs, som manuellt får godkänna eller neka.
            print(f"[Manager Required] Godkännande behövs för valutan '{currency}'.")
            # Vi returnerar False för att säga att transaktionen INTE är godkänd.
            return False

        # Om valutan FINNS i listan, betyder det att den är godkänd av chefen.
        # Vi returnerar True för att säga att transaktionen är godkänd.
        return True


if __name__ == "__main__":
    from pydantic import ValidationError # Importerar ValidationError för att fånga valideringsfel

    print("Exampel: Testar Manager.approve_transaction")

    # Giltig valuta SEK
    try:
        result_sek = Manager.approve_transaction(currency="SEK")
        print(f"Resultat för SEK: {result_sek}")
    except ValidationError as e:
        print(f"Valideringsfel för SEK: {e}")

    # Giltig valuta USD
    try:
        result_usd = Manager.approve_transaction(currency="USD")
        print(f"Resultat för USD: {result_usd}")
    except ValidationError as e:
        print(f"Valideringsfel för USD: {e}")

    # Valuta som inte är direkt godkänd JPY
    try:
        result_jpy = Manager.approve_transaction(currency="JPY")
        print(f"Resultat för JPY: {result_jpy}")
    except ValidationError as e:
        print(f"Valideringsfel för JPY: {e}")

    # Ogiltigt valutaformat för kort
    try:
        result_invalid_short = Manager.approve_transaction(currency="US")
        print(f"Resultat för ogiltig valuta (kort): {result_invalid_short}")
    except ValidationError as e:
        print(f"Valideringsfel för ogiltig valuta (kort): {e}")

    # Ogiltigt valutaformat för långt
    try:
        result_invalid_long = Manager.approve_transaction(currency="EURO")
        print(f"Resultat för ogiltig valuta (lång): {result_invalid_long}")
    except ValidationError as e:
        print(f"Valideringsfel för ogiltig valuta (lång): {e}")

    # Ogiltigt valutaformat för mellanslag
    try:
        result_invalid_char = Manager.approve_transaction(currency="SE K")
        print(f"Resultat för ogiltig valuta (specialtecken): {result_invalid_char}")
    except ValidationError as e:
        print(f"Valideringsfel för ogiltig valuta (specialtecken): {e}")
