from .models import Customer
from django.contrib.auth.models import User

def is_employee(userr) -> bool:
    return False if Customer.objects.filter(user=userr) else True