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
