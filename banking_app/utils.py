"""utils.py"""
from django.contrib.auth.models import User
from .models import Customer

def is_employee(userr) -> bool:
    """Check if user is employee"""
    return False if Customer.objects.filter(user=userr) else True
