import unittest
from bank import Bank

class TestBank(unittest.TestCase):
    def test_skapar_bank(self):
        bank = Bank()
        resultat = bank.create("Testbanken", "9999")
        self.assertEqual(resultat.name, "Testbanken")
        self.assertEqual(resultat.banknr, "9999")

if __name__ == "__main__":
    unittest.main()
