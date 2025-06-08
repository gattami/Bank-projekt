
# Manager klass fungerar som en chef som godkänner eller nekar transaktioner, t..ex. vilken valuta transaktionen använder.


class Manager:

    @staticmethod
    def approve_transaction(currency: str) -> bool:
        """
        Denna metod kontrollerar om en transaktion får fortsätta baserat på valutan.
        Parametrar: currency (str): Valutakoden för transaktionen (t.ex. "SEK", "USD", "JPY").

        Returnerar: bool: True om transaktionen godkänns (valutan är på den godkända listan).
                          False om transaktionen nekas (valutan är inte på den godkända listan).
        """
        # Här definierar vi vilka valutor som chef redan har godkänt.
        approved_currencies = ["SEK", "USD", "EUR", "GBP"]

        if currency not in approved_currencies:
            # Om valutan INTE finns i listan, betyder det att den är okänd för chefen.
            # Vi skriver ut ett meddelande för att informera om att godkännande behövs. som manuellt får godkänna eller neka.
            print(f"[Manager Required] Godkännande behövs för valutan '{currency}'.")
            # Vi returnerar False för att säga att transaktionen INTE är godkänd.
            return False

        # Om valutan FINNS i listan, betyder det att den är godkänd av chefen.
        # Vi returnerar True för att säga att transaktionen är godkänd.
        return True