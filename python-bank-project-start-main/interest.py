
# Interest klass räknar ut en växlingsavgift.

class Interest:

    EXCHANGE_FEE = 0.02  # t.ex. 2% växlingsavgift

    @staticmethod
    def apply(amount, currency):
        # Vi kontrollerar om valutan INTE är "SEK".
        # Om valutan är något annat än SEK, då vill vi lägga på en avgift.
        if currency not in ["SEK"]:
            # Vi räknar ut avgiften. Vi tar det absoluta värdet av beloppet abs(amount)
            # för att se till att avgiften alltid räknas på ett positivt belopp,
            # oavsett om pengarna kommer in eller går ut.
            fee = abs(amount) * Interest.EXCHANGE_FEE
            # Vi skriver ut ett meddelande så vi vet att en avgift har dragits.
            print(f"Applied exchange fee of {fee} for currency {currency}")
            # Vi returnerar det ursprungliga beloppet minus avgiften.
            return amount - fee 
        # Om valutan ÄR "SEK", så behöver vi inte dra av någon avgift.
        # Då returnerar vi bara det ursprungliga beloppet som det är.
        return amount
