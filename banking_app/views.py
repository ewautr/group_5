from django.shortcuts import render, get_object_or_404, redirect
from .models import Ledger, Customer, Account
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from .utils import is_employee
from django_otp.decorators import otp_required
from django.contrib.auth import logout as dj_logout
import django_rq
from . messaging import email_message
from . messaging import email_statement
from django.core import serializers
from .filters import LedgerFilter
import requests
import uuid


# Customer and Employee view
@login_required
@otp_required
def index(request):
    # display the right index for emoloyee and customer
    if is_employee(request.user):
        customers = Customer.objects.all()
        accounts = Account.objects.all()
        context = {'customers': customers, 'accounts': accounts}
        return render(request, 'banking_app/employee.html', context)
    else:
        customer = get_object_or_404(Customer, user=request.user)
        accounts = Account.objects.filter(customer=customer.pk)
        context = {
            'customer': customer,
            'accounts': accounts
        }
    return render(request, 'banking_app/index.html', context)

def LogoutView(request):
   dj_logout(request)
   return redirect('two_factor:login')

# Customer view - account activity
@login_required
@otp_required
def activity(request, account_id):
    assert not is_employee(request.user)
    activities = Ledger.objects.filter(account=account_id).order_by('-timestamp')
    
    myFilter = LedgerFilter(request.GET, queryset=activities)
    activities = myFilter.qs

    context = {
        'activities': activities,
        'account_id': account_id,
        'myFilter': myFilter
    }
    return render(request, 'banking_app/activity.html', context)

@login_required
@otp_required
def send_statement(request, account_id):
    assert not is_employee(request.user)
    user_email = request.user.email
    activities = Ledger.objects.filter(account=account_id).order_by('-timestamp')

    context = {
        'user_email': user_email,
        'activities': activities,
        'account_id': account_id,
    }
    print(activities)

    django_rq.enqueue(email_statement, {
        'user_email': user_email,
        'activities': activities,
    })

    return render(request, 'banking_app/activity.html', context)

# Customer view - transfering money
@login_required
@otp_required
def transfers(request, account_id):
    assert not is_employee(request.user)
    currentAccount = get_object_or_404(Account, pk=account_id)
    available_balance = currentAccount.balance
    allAccounts = Account.objects.exclude(pk=account_id)
    context = {
        'currentAccount': currentAccount,
        'available_balance': available_balance,
        'allAccounts': allAccounts
    }
    if request.method == 'POST':
        # make an internal transfer 
        amount = request.POST['amount']
        debit_account = request.POST['fromAccount']
        credit_account = request.POST['toAccount']
        text = request.POST['text']
        available_balance = currentAccount.balance

        if available_balance >= int(amount):
            # go forward only if the user has sufficient funds
            Ledger.transaction(int(amount), debit_account, credit_account, text)
            return redirect('banking_app:index')
        else:
            # go back and display error
            context = {
                'currentAccount': currentAccount,
                'allAccounts': allAccounts,
                'error': 'insufficient funds'
            }

    return render(request, 'banking_app/transfers.html', context)

# Customer view - transfering money
@login_required
@otp_required
def external_transfer(request, account_id):
    assert not is_employee(request.user)

    currentAccount = get_object_or_404(Account, pk=account_id)
    allAccounts = Account.objects.exclude(pk=account_id)
    
    amount = request.POST['amount']
    debit_account = request.POST['fromAccount']
    bank_iban = request.POST['toBank']
    credit_account = request.POST['toAccount']
    text = request.POST['text']
    transaction_id = uuid.uuid1()
    available_balance = currentAccount.balance

        #proceed if the user has sufficient funds to make the transfer
    if available_balance >= int(amount):
        # authenticating the bank user
        response = requests.post('http://127.0.0.1:8003/api/v1/rest-auth/login/', data={'username': 'Bank 8000', 'password': 'pass1'})
        api_key = response.json()['key']

        # check if the recipient exists 
        response = requests.get(f'http://127.0.0.1:8003/api/v1/{credit_account}', headers={'Authorization': f'Token {api_key}'})
        if response.status_code == 404:
            context = {
                'currentAccount': currentAccount,
                'allAccounts': allAccounts,
                'error': 'account does not exist'
            }
            return render(request, 'banking_app/transfers.html', context)
        
        # http request with data for two new instances in the ledger table
        ledger_row_1 = {
            "transaction_id": transaction_id,
            "account": bank_iban,
            "amount": f'-{amount}',
            "text": text
        }
        ledger_row_2 = {
            "transaction_id": transaction_id,
            "account": credit_account,
            "amount": amount,
            "text": text
        }
        response = requests.post('http://127.0.0.1:8003/api/v1/ledger/', headers={'Authorization': f'Token {api_key}'}, data=ledger_row_1)
        response = requests.post('http://127.0.0.1:8003/api/v1/ledger/', headers={'Authorization': f'Token {api_key}'}, data=ledger_row_2)
        
        # if response is okay proceed with making a ledger instance in the current bank 
        if response.status_code == 201:
            Ledger.transaction(int(amount), debit_account, bank_iban, text)

        return redirect('banking_app:index')
    else:
        context = {
            'currentAccount': currentAccount,
            'allAccounts': allAccounts,
            'error': 'insufficient funds'
        }
    
    return render(request, 'banking_app/transfers.html', context)


# Customer view - taking a loan
@login_required
@otp_required
def add_loan(request, customer_id):
    assert not is_employee(request.user)
    customer = get_object_or_404(Customer, pk=customer_id)
    customerAccounts = Account.objects.filter(customer=customer).filter(account_type='bank account')
    context = {
        'customer': customer,
        'customerAccounts': customerAccounts
    }

    # customer is taking a loan
    if request.method == 'POST':
        # Create the account
        account = Account()
        account.customer = customer
        account.account_type = 'Loan'
        account.save()

        # Make a ledger where we take amount from the loan account and add it to the chosen account
        amount = request.POST['amount']
        debit_account = account.pk
        credit_account = request.POST['toAccount']
        text = request.POST['text']
        Ledger.transaction(int(amount), debit_account, credit_account, text)

        return redirect('banking_app:index')

    return render(request, 'banking_app/add_loan.html', context)

# Customer view - paying off a loan
@login_required
@otp_required
def pay_loan(request, customer_id, account_id):
    assert not is_employee(request.user)
    customer = get_object_or_404(Customer, pk=customer_id)
    account = get_object_or_404(Account, pk=account_id)
    customerAccounts = Account.objects.filter(customer=customer).filter(account_type='bank account')
    context = {
        'customer': customer,
        'customerAccounts': customerAccounts,
        'account': account
    }
    if request.method == 'POST':
        amount = request.POST['amount']
        debit_account = request.POST['fromAccount']
        credit_account = account.pk
        text = 'paying off my loan'

        selectedAccount = get_object_or_404(Account, pk=debit_account)
        available_balance = selectedAccount.balance

        if available_balance >= int(amount) and int(amount) <= -account.balance:
            # make a transaction from customer's account to the loan account
            Ledger.transaction(int(amount), debit_account, credit_account, text)
            
            # if the loan is payed off fully - delete it
            if account.balance == 0:
                account.delete()

            return redirect('banking_app:index')
        elif int(amount) > -account.balance:
        # check if the user is not paying too much for the loan
            context = {
                'customer': customer,
                'customerAccounts': customerAccounts,
                'account': account,
                'error': 'your loan in smaller than the amount you are sending'
            }
        else:
            context = {
                'customer': customer,
                'customerAccounts': customerAccounts,
                'account': account,
                'error': 'insufficient funds'
            }

    return render(request, 'banking_app/pay_loan.html', context)

# Employee view - adding a new customer
@login_required
@otp_required
def add_customer(request): 
    assert is_employee(request.user)
    context = {}

    if request.method == 'POST':
        user_name = request.POST['user_name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        rank = request.POST['rank']

        if password != confirmPassword:
            context = {
                'error': 'Passwords did not match. Please try again.'
            }
            return render(request, 'banking_app/add_customer.html', context)

        new_user = User.objects.create_user(user_name, email, password)

        customer = Customer()
        customer.user = new_user
        customer.phone = phone
        customer.rank = rank
        customer.save()

        django_rq.enqueue(email_message, {
            'email' : customer.user.email,
            'username': customer.user.username,
            'password': password,
        })

    return render(request, 'banking_app/add_customer.html', context)

# Employee view - editing a customer
@login_required
@otp_required
def edit_customer(request, customer_id):
    assert is_employee(request.user)
    customer = get_object_or_404(Customer, pk=customer_id)
    context = { 'customer': customer }

    if request.method == 'POST':
        user = customer.user
        user.user_name = request.POST['user_name']
        customer.phone = request.POST['phone']
        customer.rank = request.POST['rank']
        customer.save()
        user.save()
        return redirect('banking_app:index')

    return render(request, 'banking_app/edit_customer.html', context)

# Employee view - adding a new account
@login_required
@otp_required
def add_account(request):
    assert is_employee(request.user)
    customers = Customer.objects.all()
    context = {'customers': customers}

    if request.method == 'POST':
        customerPK = request.POST['customer']
        account_type = request.POST['account_type']
        customer = get_object_or_404(Customer, pk=customerPK)

        account = Account()
        account.customer = customer
        account.account_type = account_type
        account.save()

        return redirect('banking_app:index')

    return render(request, 'banking_app/add_account.html', context)