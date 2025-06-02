# PYTHONPATH=python-bank-project-start-main pytest python-bank-project-start-main/tests/test_customer.py

import pytest
from customer import Customer
from account import Account
from unittest.mock import MagicMock, patch


def test_create_success(monkeypatch):
    customer = Customer()  # Skapar Customer-instans

    dummy_cursor = MagicMock()  # Mockar en cursor (databaspekare)
    dummy_conn = MagicMock()    # Mockar en databasanslutning

    # Gör så att vår mockade connection stödjer "with"-syntax (context manager)
    dummy_conn.__enter__.return_value = dummy_conn
    dummy_conn.__exit__.return_value = None

    dummy_conn.cursor.return_value = dummy_cursor  # När cursor() anropas returnera dummy_cursor

    # Mockar metoden get_conn så att den returnerar dummy_conn
    monkeypatch.setattr("db.Db.get_conn", lambda self=None: dummy_conn)

    # Mockar execute så att det inte händer någonting (simulerar lyckat SQL-anrop)
    dummy_cursor.execute.return_value = None

    # Mockar Customer.get så att den returnerar en dummy-kund
    monkeypatch.setattr(customer, "get", lambda ssn: type("DummyCustomer", (), {"name": "Ivan", "ssn": ssn})())

    # Anropar create-metoden
    result = customer.create("Ivan", "9001011234")

    # Verifierar att rätt data returneras
    assert result.name == "Ivan"
    assert result.ssn == "9001011234"

    # Kontrollerar att execute anropades med rätt SQL och parametrar
    dummy_cursor.execute.assert_called_with("INSERT INTO customers (name, ssn) VALUES (%s, %s)", ["Ivan", "9001011234"])


def test_create_existing(monkeypatch):
    customer = Customer()

    dummy_cursor = MagicMock()
    dummy_conn = MagicMock()

    dummy_conn.__enter__.return_value = dummy_conn
    dummy_conn.__exit__.return_value = None

    dummy_conn.cursor.return_value = dummy_cursor

    monkeypatch.setattr("db.Db.get_conn", lambda self=None: dummy_conn)

    # Simulerar att execute kastar undantag för duplicerat värde (duplicate key)
    def raise_duplicate(*args, **kwargs):
        raise Exception("duplicate key value violates unique constraint")
    dummy_cursor.execute.side_effect = raise_duplicate

    # Mockar get för att returnera dummy-kund vid fel
    monkeypatch.setattr(customer, "get", lambda ssn: type("DummyCustomer", (), {"name": "Ivan", "ssn": ssn})())

    # Anropar create som ska hantera dupliceringen
    result = customer.create("Ivan", "9001011234")

    # Verifierar dummy-resultatet
    assert result.name == "Ivan"
    assert result.ssn == "9001011234"


def test_get_customer_found(monkeypatch):
    customer = Customer()

    dummy_cursor = MagicMock()
    dummy_conn = MagicMock()

    dummy_conn.__enter__.return_value = dummy_conn
    dummy_conn.__exit__.return_value = None

    dummy_conn.cursor.return_value = dummy_cursor

    monkeypatch.setattr("db.Db.get_conn", lambda self=None: dummy_conn)

    # Mockar fetchone för att returnera kunddata (kund hittad)
    dummy_cursor.fetchone.return_value = (1, "Ivan", "9001011234")

    # Mockar get_accounts för att undvika riktig databasaccess
    monkeypatch.setattr(customer, "get_accounts", lambda: ["account1", "account2"])

    # Anropar get med ett giltigt ssn
    result = customer.get("9001011234")

    # Verifierar att samma instans returneras
    assert result is customer

    # Verifierar attributen
    assert customer.id == 1
    assert customer.name == "Ivan"
    assert customer.ssn == "9001011234"
    assert customer.accounts == ["account1", "account2"]

    # Kontrollera att rätt SQL anropades
    dummy_cursor.execute.assert_called_with("SELECT * FROM customers WHERE ssn = %s", ["9001011234"])


def test_get_customer_not_found(monkeypatch):
    customer = Customer()

    dummy_cursor = MagicMock()
    dummy_conn = MagicMock()

    dummy_conn.__enter__.return_value = dummy_conn
    dummy_conn.__exit__.return_value = None

    dummy_conn.cursor.return_value = dummy_cursor

    monkeypatch.setattr("db.Db.get_conn", lambda self=None: dummy_conn)

    # Mockar fetchone för att simulera att kund inte hittas (returnerar None)
    dummy_cursor.fetchone.return_value = None

    # Anropar get med ogiltigt ssn
    result = customer.get("unknown_ssn")

    # Verifierar att None returneras
    assert result is None

    # Kontrollera att SQL anropades korrekt
    dummy_cursor.execute.assert_called_with("SELECT * FROM customers WHERE ssn = %s", ["unknown_ssn"])


def test_get_accounts(monkeypatch):
    customer = Customer()
    customer.id = 1  # Sätter kundens id

    dummy_cursor = MagicMock()
    dummy_conn = MagicMock()

    dummy_conn.__enter__.return_value = dummy_conn
    dummy_conn.__exit__.return_value = None

    dummy_conn.cursor.return_value = dummy_cursor

    monkeypatch.setattr("db.Db.get_conn", lambda self=None: dummy_conn)

    # Mockar fetchall för att returnera två konton
    dummy_cursor.fetchall.return_value = [
        (1, customer.id, 1, "Personal_account", "1234567890", 0),
        (2, customer.id, 1, "Savings_account", "0987654321", 0)
    ]

    # Patchar Account.get så att den returnerar en textsträng med kontonummer
    with patch.object(Account, 'get', side_effect=lambda nr: f"Account: {nr}"):
        accounts = customer.get_accounts()

    # Verifierar att resultatet är en lista med två element
    assert isinstance(accounts, list)
    assert len(accounts) == 2

    # Verifierar att elementen har rätt format
    assert accounts[0] == "Account: 1234567890"
    assert accounts[1] == "Account: 0987654321"

    # Kontrollera att SQL anropades korrekt
    dummy_cursor.execute.assert_called_once_with("SELECT * FROM accounts WHERE customer = %s", [customer.id])
