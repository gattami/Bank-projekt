import unittest
from bank import Bank


class TestBank(unittest.TestCase):
   def test_skapa_bank(self):
       bank = Bank()
       resultat = bank.skapa("Testbanken", "9999")
       self.assertEqual(resultat.namn, "Testbanken")
       self.assertEqual(resultat.banknr, "9999")


if __name__ == "__main__":
   unittest.main()
