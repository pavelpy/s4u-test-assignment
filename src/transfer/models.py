from decimal import Decimal
from django.db import models, transaction
from django.db.models import F

from account.models import Account


class TransferBaseException(Exception):
    pass


class InsufficientBalance(TransferBaseException):
    pass


class InvalidAmount(TransferBaseException):
    pass


class Transfer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, models.CASCADE, related_name='transfers_in')
    to_account = models.ForeignKey(Account, models.CASCADE, related_name='transfers_out')
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    @staticmethod
    @transaction.atomic
    def do_transfer(from_account: Account, to_account: Account, amount: Decimal):
        if from_account.balance < amount:
            raise InsufficientBalance('Amount should be larger than zero.')

        if amount <= 0:
            raise InvalidAmount()
        # We should use PostgreSQL in production.
        Account.objects.select_for_update().filter(pk=from_account.pk)\
            .update(balance=F('balance') - amount)
        Account.objects.select_for_update().filter(pk=to_account.pk)\
            .update(balance=F('balance') + amount)

        return Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            amount=amount
        )
