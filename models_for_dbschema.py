from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL
import datetime
from decimal import Decimal

# Skapar basklass för deklarativa modeller
# Base är grunden för alla våra databasmodeller.
Base = declarative_base()

# Länder-tabell
# Denna tabell lagrar information om länder.
class Country(Base):
    __tablename__ = 'countries' # Namnet på tabellen i databasen.
    id = Column(Integer, primary_key=True)  # Primärnyckel, unikt identifierar varje land.
    country_name = Column(String, unique=True, nullable=False)  # Unikt landsnamn, får inte vara null.
    country_code = Column(String(2), nullable=False)  # Ex: "SE", "US", landskod, får inte vara null.

    # Relationer till andra tabeller
    # Dessa relationer definierar hur Country-objekt är kopplade till andra objekt i databasen.
    # Data Quality: Upprätthåller referensintegritet. Om ett land tas bort, kan det påverka relaterade poster.
    municipalities = relationship("Municipality", back_populates="country")
    addresses = relationship("Address", back_populates="country")
    sent_transactions_as_country = relationship("Transaction", foreign_keys="[Transaction.sender_country_id]",
                                                back_populates="sender_country")
    received_transactions_as_country = relationship("Transaction", foreign_keys="[Transaction.receiver_country_id]",
                                                    back_populates="receiver_country")

# Kommun-tabell
# Denna tabell lagrar information om kommuner.
class Municipality(Base):
    __tablename__ = 'municipalities'
    id = Column(Integer, primary_key=True)
    municipality_name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)  # FK till land, säkerställer att kommunen tillhör ett befintligt land.
    country = relationship("Country", back_populates="municipalities")
    addresses = relationship("Address", back_populates="municipality")

    # Relationer till transaktioner
    # Data Quality: Spårbarhet av transaktioner baserat på kommun.
    sent_transactions_as_municipality = relationship("Transaction", foreign_keys="[Transaction.sender_municipality_id]",
                                                     back_populates="sender_municipality")
    received_transactions_as_municipality = relationship("Transaction",
                                                         foreign_keys="[Transaction.receiver_municipality_id]",
                                                         back_populates="receiver_municipality")

    # Säkerställer unik kombination av kommun och land
    # Data Quality (Unikhet): Förhindrar dubbletter av samma kommun i samma land.
    __table_args__ = (UniqueConstraint('municipality_name', 'country_id', name='_municipality_country_uc'),)


# Bank-tabell
# Denna tabell lagrar information om banker.
class Bank(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Bankens namn.
    bank_identifier = Column(String, unique=True, nullable=False)  # Unik identifierare, ex: BIC/SWIFT.
    # Data Quality (Unikhet): Säkerställer att varje bank har en unik identifierare.
    accounts = relationship("Account", back_populates="bank")  # Kopplade konton.
    staff = relationship("Staff", back_populates="bank")  # Kopplad personal.
# Adresser-tabell
# Denna tabell lagrar adressinformation.
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    street = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False) # Koppling till land.
    municipality_id = Column(Integer, ForeignKey('municipalities.id'), nullable=True) # Koppling till kommun (kan vara null).

    # Relationer till land och kommun
    country = relationship("Country", back_populates="addresses")
    municipality = relationship("Municipality", back_populates="addresses")

    # Relationer till kunder och personal
    customers = relationship("Customer", back_populates="address")
    staff_members = relationship("Staff", back_populates="address")

    # Unik adress (samma gata, postnummer etc. kan inte dupliceras inom samma kommun och land)
    # Data Quality (Unikhet): Förhindrar dubbletter av exakt samma adress.
    __table_args__ = (
    UniqueConstraint('street', 'zip_code', 'city', 'country_id', 'municipality_id', name='_unique_address_uc'),)


# Personal-tabell
# Denna tabell lagrar information om bankpersonal.
class Staff(Base):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False) # Unik e-postadress.
    # Data Quality (Unikhet): Säkerställer att varje personalmedlem har en unik e-post.
    position = Column(String, nullable=False)  # Tjänstetitel.
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False) # Koppling till banken de arbetar på.
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True) # Koppling till adress (kan vara null).

    # Relationer till bank och adress
    bank = relationship("Bank", back_populates="staff")
    address = relationship("Address", back_populates="staff_members")


# Kund-tabell
# Denna tabell lagrar information om bankkunder.
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    ssn = Column(String, unique=True, nullable=False)  # Personnummer.
    # Data Quality (Unikhet): Säkerställer att varje kund har ett unikt personnummer.
    phone = Column(String, nullable=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True) # Koppling till adress (kan vara null).

    # Relationer till adress och konton
    address = relationship("Address", back_populates="customers")
    accounts = relationship("Account", back_populates="customer")

    __table_args__ = (UniqueConstraint('ssn', name='uq_ssn'),)  # Säkerställer unikt personnummer.


# Konton-tabell
# Denna tabell lagrar information om bankkonton.
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    account_number = Column(String, unique=True, nullable=False)  # IBAN eller kontonummer.
    # Data Quality (Unikhet): Varje konto har ett unikt nummer.
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False) # Koppling till kund.
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False) # Koppling till bank.

    customer = relationship("Customer", back_populates="accounts")
    bank = relationship("Bank", back_populates="accounts")

    account_type = Column(String, default="Okänd")  # Sparkonto, lönekonto etc.
    credit_limit = Column(DECIMAL(precision=10, scale=2), default=Decimal('0.00'))  # Kreditgräns.
    # Data Quality (Precision): Använder DECIMAL för exakta monetära värden.
    balance = Column(DECIMAL(precision=10, scale=2), default=Decimal('0.00'))  # Nuvarande saldo.
    # ACID (Atomicity, Consistency): Saldo måste vara korrekt efter varje transaktion. DECIMAL hjälper till med noggrannhet.
    approved = Column(Boolean, default=True)  # Godkänt konto?

    # Transaktioner där kontot är avsändare eller mottagare
    sent_transactions = relationship("Transaction", foreign_keys="[Transaction.sender_account_id]",
                                     back_populates="sender_account")
    received_transactions = relationship("Transaction", foreign_keys="[Transaction.receiver_account_id]",
                                         back_populates="receiver_account")

    # Beräknar summan av utgående och inkommande transaktioner
    # Data Quality (Noggrannhet): Säkerställer korrekta beräkningar av inkommande/utgående pengar.
    def calculate_debit_credit(self):
        total_incoming_sum = Decimal('0.00')
        # Initierar en variabel för att hålla summan av alla pengar som mottagits av kontot.
        # Vi använder Decimal('0.00') för att säkerställa exakt decimalaritmetik från början.

        for t in self.received_transactions:
            # Itererar genom alla transaktioner där detta konto är mottagaren.
            # self.received_transactions är en relation definierad i Account-klassen,
            # som länkar till Transaction-objekt där detta konto är mottagaren.
            total_incoming_sum += Decimal(str(t.amount))
            # För varje mottagen transaktion läggs dess belopp till total_incoming_sum.
            # Det konverteras till Decimal(str(t.amount)) för att garantera precision,
            # särskilt om t.amount hämtades från en databas som en sträng eller en annan numerisk typ.

        total_outgoing_sum = Decimal('0.00')
        # Initierar en variabel för att hålla summan av alla pengar som skickats från kontot.

        for t in self.sent_transactions:
            # Itererar genom alla transaktioner där detta konto är avsändaren.
            # self.sent_transactions är en annan relation som länkar till Transaction-objekt
            # där detta konto är avsändaren.
            total_outgoing_sum += Decimal(str(t.amount))
            # För varje skickad transaktion läggs dess belopp till total_outgoing_sum.
            # Återigen, konverteras till Decimal för precision.

        credit_limit_val = Decimal(str(self.credit_limit)) if self.credit_limit is not None else Decimal('0.00')
        # Denna rad hämtar kontots kreditgräns.
        # Den kontrollerar om self.credit_limit existerar (inte är None).
        # Om det gör det, konverteras det till en Decimal för beräkningar.
        # Om det är None (vilket betyder att ingen kreditgräns är satt), blir det standard Decimal('0.00').
        # Detta säkerställer att beräkningar som involverar kreditgränsen alltid är exakta och hanterar saknade värden på ett smidigt sätt.

        return total_outgoing_sum, total_incoming_sum
        # Returnerar två värden: det totala beloppet som debiterats (utgående) och det totala beloppet som krediterats (inkommande).
        # Kreditgränsen hanteras separat i update_balance, eftersom den påverkar det slutliga saldot, inte bara summan av transaktioner.

    # Uppdaterar saldot utifrån kredit och transaktioner
    # ACID (Atomicity, Consistency): Detta är en kritisk funktion som bör ingå i en transaktion för att säkerställa att saldot alltid är korrekt.
    # Data Quality (Noggrannhet): Uppdaterar kontosaldo med hög precision.
    def update_balance(self):
        debit, credit = self.calculate_debit_credit()
        self.balance = credit - debit + (
            Decimal(str(self.credit_limit)) if self.credit_limit is not None else Decimal('0.00'))


# Transaktioner-tabell
# Denna tabell lagrar information om banktransaktioner.
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)  # T.ex. UUID, unik identifierare för varje transaktion.
    # ACID (Atomicity): Varje transaktion måste vara atomär. En unik ID hjälper till med spårbarhet.
    # Data Quality (Unikhet, Spårbarhet): Varje transaktion är unikt identifierbar.
    timestamp = Column(DateTime, nullable=False) # När transaktionen skedde.
    # Data Quality (Tidskänslighet): Registrerar exakt tidpunkt för transaktionen.
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False) # Belopp.
    # Data Quality (Noggrannhet): Använder DECIMAL för exakta monetära värden.
    currency = Column(String(3), nullable=False)  # T.ex. "SEK", "USD".
    transaction_type = Column(String, nullable=True)  # Intern, extern, betalning etc.
    notes = Column(String, nullable=True)  # Eventuella kommentarer.

    # FK till konton
    sender_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True) # Avsändarkonto.
    receiver_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True) # Mottagarkonto.
    # ACID (Consistency): Säkerställer att konton existerar och att referenser är korrekta.
    # Data Quality (Referensintegritet): Säkerställer att transaktioner kopplas till giltiga konton.

    sender_account = relationship("Account", foreign_keys="[Transaction.sender_account_id]",
                                  back_populates="sent_transactions")
    receiver_account = relationship("Account", foreign_keys="[Transaction.receiver_account_id]",
                                    back_populates="received_transactions")

    sender_account_number_full = Column(String, nullable=True) # Fullständigt avsändarkonto-nummer (för loggning/spårbarhet).
    receiver_account_number_full = Column(String, nullable=True) # Fullständigt mottagarkonto-nummer.

    approved_by_manager = Column(Boolean, default=False)  # Har godkänts manuellt?
    # Data Quality (Validering): Indikerar om en transaktion har granskats och godkänts.
    exchange_fee_applied = Column(DECIMAL(precision=10, scale=2), nullable=True) # Eventuell växlingsavgift.

    # Länder och kommuner som avsändare/mottagare
    # Data Quality (Kompletthet, Kontext): Ger ytterligare kontext och spårbarhet för transaktionen.
    sender_country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    sender_municipality_id = Column(Integer, ForeignKey('municipalities.id'), nullable=True)
    receiver_country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    receiver_municipality_id = Column(Integer, ForeignKey('municipalities.id'), nullable=True)

    sender_country = relationship("Country", foreign_keys=[sender_country_id],
                                  back_populates="sent_transactions_as_country")
    sender_municipality = relationship("Municipality", foreign_keys=[sender_municipality_id],
                                       back_populates="sent_transactions_as_municipality")
    receiver_country = relationship("Country", foreign_keys=[receiver_country_id],
                                    back_populates="received_transactions_as_country")
    receiver_municipality = relationship("Municipality", foreign_keys=[receiver_municipality_id],
                                         back_populates="received_transactions_as_municipality")


# Ränte-tabell
# Denna tabell lagrar information om räntesatser.
class InterestRate(Base):
    __tablename__ = 'interest_rates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rate_type = Column(String, unique=True, nullable=False)  # T.ex. "sparkonto", "lån".
    # Data Quality (Unikhet): Säkerställer unika räntetyper.
    rate_value = Column(DECIMAL(precision=10, scale=2), nullable=False)  # Procentsats.
    # Data Quality (Noggrannhet): Använder DECIMAL för exakta räntesatser.
    currency = Column(String(3), nullable=True)
    effective_date = Column(DateTime, default=datetime.datetime.now)  # När den gäller från.
    # Data Quality (Tidskänslighet): Registrerar när räntan blir gällande, viktigt för historisk spårbarhet.

# Skapar databasen och alla tabeller om de inte finns
# DATABASE_URL: Anslutningssträngen till PostgreSQL-databasen.
DATABASE_URL = "postgresql://postgres:5432@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)