from rest_framework import generics

from banking_app.models import Account, Ledger
from .serializers import AccountSerialzer, LedgerSerialzer

class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerialzer

class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerialzer

class LedgerList(generics.ListCreateAPIView):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerialzer

class LedgerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerialzer