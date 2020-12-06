from decimal import Decimal

from django.test import TestCase

from account.models import Account
from customer.models import Customer
from transfer.models import Transfer
from transfer.models import InsufficientBalance
from transfer.models import InvalidAmount


class TransferTest(TestCase):
    fixtures = [
        '0001_customer.json',
        '0001_account.json',
    ]

    def setUp(self):
        super(TransferTest, self).setUp()

        self.account1 = Account.objects.get(pk=1)
        self.account2 = Account.objects.get(pk=2)

    def test_basic_transfer(self):
        Transfer.do_transfer(self.account1, self.account2, Decimal(100))

        self.account1.refresh_from_db()
        self.account2.refresh_from_db()

        self.assertEqual(self.account1.balance, 900)
        self.assertEqual(self.account2.balance, 1100)
        self.assertTrue(Transfer.objects.filter(
            from_account=self.account1,
            to_account=self.account2,
            amount=100,
        ).exists())

    def test__do_transfer__insufficient_balance__exception(self):
        with self.assertRaises(InsufficientBalance):
            Transfer.do_transfer(self.account1, self.account2, Decimal(1000.1))

    def test__do_transfer__less_or_equal_zero_amount__exception(self):
        with self.assertRaises(InvalidAmount):
            Transfer.do_transfer(self.account1, self.account2, Decimal(0))
        with self.assertRaises(InvalidAmount):
            Transfer.do_transfer(self.account1, self.account2, Decimal(-0.0001))
