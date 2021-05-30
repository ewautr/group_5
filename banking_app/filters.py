"""filters.py"""
import django_filters
from django_filters import DateFilter
from .models import Ledger

# Function filtering account transactions (Ledger) based on specified date-values from interface
class LedgerFilter(django_filters.FilterSet):
    """Filter account transactions by specified date-values"""
    start_date = DateFilter(field_name="timestamp", lookup_expr='gte')
    end_date = DateFilter(field_name="timestamp", lookup_expr='lte')
    class Meta:
        model = Ledger
        fields = '__all__'
        exclude = ['account','amount','text', 'timestamp', 'transaction_id']
        """Messaging.py"""
