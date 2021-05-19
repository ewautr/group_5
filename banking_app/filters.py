import django_filters
from django_filters import DateFilter
from .models import Ledger

class LedgerFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="timestamp", lookup_expr='gte')
    end_date = DateFilter(field_name="timestamp", lookup_expr='lte')
    class Meta:
        model = Ledger
        fields = '__all__'
        exclude = ['account','amount','text', 'timestamp', 'transaction_id']