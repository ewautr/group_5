"""models.py"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import transaction


class Customer(models.Model):
    """Customer model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(null=True, max_length=200)

    class Rank(models.TextChoices):
        """Settings ranks"""
        BASIC = 'Basic'
        SILVER = 'Silver'
        GOLD = 'Gold'

    rank = models.CharField(choices=Rank.choices, default=Rank.BASIC, max_length=200)

    def __str__(self):
        return f"{self.user} - {self.phone} - {self.rank}"

    @property
    def can_make_loan(self):
        """Checking if user can make loan"""
        if self.rank == 'Basic':
            return False
        else:
            return True


class Account(models.Model):
    """Account model"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class AccountType(models.TextChoices):
        """Setting account types"""
        BANK_ACCOUNT = 'Bank Account'
        LOAN = 'Loan'
        FOREIGN_BANK = 'Foreign Bank'

    account_type = models.CharField(choices=AccountType.choices, default=AccountType.BANK_ACCOUNT, max_length=200)

    def __str__(self):
        return f"{self.customer} - {self.account_type}"

    @property
    def balance(self):
        """Checking balance"""
        summedBalance = Ledger.objects.filter(account=self.pk).aggregate(Sum('amount'))['amount__sum']
        return summedBalance

    @property
    def is_bank(self):
        """Checking banktype"""
        if self.account_type == 'FOREIGN_BANK':
            return True
        else:
            return False

class Ledger(models.Model):
    """Ledger model"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="fromAccount")
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    text = models.CharField(null=True, max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)

# every transaction is 2 rows

    def __str__(self):
        return f"{self.account} - {self.amount} {self.text} - {self.timestamp} - {self.transaction_id}"

    @classmethod
    @transaction.atomic
    def transaction(cls, amount, debit_account, credit_account, text):
        """Transaction model"""
        id = uuid.uuid4()

        # sender account
        sender_account = get_object_or_404(Account, pk=debit_account)
        ledger = Ledger()
        ledger = cls(account=sender_account, amount=-amount, text=text, transaction_id=id)
        ledger.save()
        # receiver account
        receiver_account = get_object_or_404(Account, pk=credit_account)
        ledger = Ledger()
        ledger = cls(account=receiver_account, amount=amount, text=text, transaction_id=id)
        ledger.save()
