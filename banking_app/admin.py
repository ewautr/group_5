from django.contrib import admin
from .models import Customer, Ledger, Account


admin.site.register(Customer)
admin.site.register(Ledger)
admin.site.register(Account)