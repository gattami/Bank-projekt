from pydantic import validate_call, Field 
from decimal import Decimal 


class Interest:

    EXCHANGE_FEE = Decimal("0.02")  # t.ex. 2% växlingsavgift
    # TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'
    # Därför definiera EXCHANGE_FEE som en Decimal för att undvika TypeError

    @staticmethod
    @validate_call # Pydantic-dekoratör: Validerar argumenten innan metoden körs.
    def apply(amount: Decimal = Field(..., gt=0), # Beloppet måste vara Decimal och strikt större än 0.
              currency: str = Field(..., pattern=r"^[A-Z]{3}$")) -> Decimal: # Valutan måste vara en sträng med 3 stora bokstäver (t.ex. "USD", "SEK").
      
        if currency not in ["SEK"]:
            
            fee = amount * Interest.EXCHANGE_FEE
            
            print(f"Applied exchange fee of {fee} for currency {currency}")
            # Vi returnerar det ursprungliga beloppet minus avgiften
            return amount - fee  
        # Om valutan ÄR "SEK", så behöver vi inte dra av någon avgift
        # Då returnerar vi bara det ursprungliga beloppet
        return amount


if __name__ == "__main__":
    from pydantic import ValidationError # Importerar ValidationError för att fånga valideringsfel

    print("Exampel: Testar Interest.apply")

    # Giltig transaktion i SEK
    try:
        result_sek = Interest.apply(amount=Decimal("100.00"), currency="SEK")
        print(f"Resultat för SEK: {result_sek}")
    except ValidationError as e:
        print(f"Valideringsfel för SEK: {e}")

    # Giltig transaktion i USD med avgift
    try:
        result_usd = Interest.apply(amount=Decimal("200.00"), currency="USD")
        print(f"Resultat för USD: {result_usd}")
    except ValidationError as e:
        print(f"Valideringsfel för USD: {e}")

    # Försök med negativt belopp 
    try:
        result_negative = Interest.apply(amount=Decimal("-50.00"), currency="EUR")
        print(f"Resultat för negativt belopp: {result_negative}")
    except ValidationError as e:
        print(f"Valideringsfel för negativt belopp: {e}")

    # Försök med ogiltigt valutaformat 
    try:
        result_invalid_currency = Interest.apply(amount=Decimal("75.00"), currency="US")
        print(f"Resultat för ogiltig valuta: {e}")
    except ValidationError as e:
        print(f"Valideringsfel för ogiltig valuta: {e}")

    # Försök med nollbelopp 
    try:
        result_zero = Interest.apply(amount=Decimal("0.00"), currency="GBP")
        print(f"Resultat för nollbelopp: {result_zero}")
    except ValidationError as e:
        print(f"Valideringsfel för nollbelopp: {e}")
