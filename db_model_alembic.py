# Vi importerar nödvändiga moduler från SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import declarative_base

# Vi definierar en basklass för våra modeller – alla tabeller kommer att ärva från denna
Base = declarative_base()

# -------------------------------
# TABELL: banks
# -------------------------------
class Bank(Base):
    __tablename__ = "banks"  # Namn på tabellen i databasen

    id = Column(Integer, primary_key=True)  # Unik ID för varje bank (auto-increment)
    name = Column(Text, nullable=False)     # Bankens namn – får inte vara tomt
    banknr = Column(Text, nullable=False, unique=True)  # Bankens registreringsnummer – måste vara unikt

# -------------------------------
# TABELL: customers (kunder)
# -------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)  # Unik ID för varje kund
    name = Column(Text, nullable=False)     # Kundens namn – obligatoriskt
    ssn = Column(Text, nullable=False, unique=True)  # Personnummer – måste vara unikt
    approved = Column(Boolean, nullable=False, default=False)  # Om kunden är godkänd (true/false), standard = false

# -------------------------------
# TABELL: accounts (bankkonton)
# -------------------------------
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)  # Unik ID för kontot
    customer = Column(Integer, ForeignKey("customers.id"), nullable=False)  # Kundens ID – koppling till customers-tabellen
    bank = Column(Integer, ForeignKey("banks.id"), nullable=False)  # Bankens ID – koppling till banks-tabellen
    type = Column(Text, nullable=False)  # Kontotyp (ex. "spar", "lönekonto") – får inte vara tomt
    nr = Column(Text, nullable=False, unique=True)  # Kontonummer – måste vara unikt
    credit = Column(Integer, nullable=False, default=0)  # Kreditgräns eller saldo – standard är 0

# -------------------------------
# TABELL: transactions (transaktioner)
# -------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)  # Unik ID för transaktionen
    amount = Column(Integer, nullable=False, default=0)  # Belopp för transaktionen – måste anges
    account_nr = Column(Text, nullable=False)  # Vilket konto transaktionen gäller (kontonummer, ej ID)
    transaction_time = Column(TIMESTAMP, nullable=False)
  # Tidpunkt då transaktionen skapades

#📘 Tips
#nullable=False betyder att fältet är obligatoriskt
#unique=True betyder att värdet måste vara unikt
#ForeignKey(...) skapar relationer mellan tabeller (t.ex. varje konto tillhör en kund)
