from rest_framework import serializers
from banking_app.models import Account, Ledger

class AccountSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'customer', 'account_type',)
        model = Account

class LedgerSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = ('transaction_id', 'account', 'amount', 'text')
        model = Ledger