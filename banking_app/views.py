from django.shortcuts import render, get_object_or_404, redirect
from .models import Ledger, Customer, Account
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from .utils import is_employee


# Customer and Employee view
@login_required
def index(request):
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

# Customer view - account activity
@login_required
def activity(request, account_id):
    assert not is_employee(request.user)
    activities = Ledger.objects.filter(account=account_id)
    context = {
        'activities': activities,
    }
    return render(request, 'banking_app/activity.html', context)

# Customer view - transfering money
@login_required
def transfers(request, account_id):
    assert not is_employee(request.user)
    currentAccount = get_object_or_404(Account, pk=account_id)
    allAccounts = Account.objects.exclude(pk=account_id)
    context = {
        'currentAccount': currentAccount,
        'allAccounts': allAccounts
    }
    if request.method == 'POST':
        amount = request.POST['amount']
        debit_account = request.POST['fromAccount']
        credit_account = request.POST['toAccount']
        text = request.POST['text']
        available_balance = currentAccount.balance

        if available_balance >= int(amount):
            Ledger.transaction(int(amount), debit_account, credit_account, text)
            return redirect('banking_app:index')
        else:
            context = {
                'currentAccount': currentAccount,
                'allAccounts': allAccounts,
                'error': 'insufficient funds'
            }

    return render(request, 'banking_app/transfers.html', context)

# Customer view - transfering money
@login_required
def external_transfer(request, account_id):
    assert not is_employee(request.user)
    amount = request.POST['amount']
    debit_account = request.POST['fromAccount']
    bank_iban = request.POST['toBank']
    credit_account = request.POST['toAccount']
    text = request.POST['text']
    available_balance = currentAccount.balance

        #proceed if the user has sufficient funds to make the transfer
    if available_balance >= int(amount):
            # http request with data for two new instances in the ledger table
        response = request.get('https://www.somedomain.com/some/url/save')

            # make an instance in the ledger table of the current bank 
            # Ledger.transaction(int(amount), debit_account, bank_iban, text)
            # print(response)
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
def add_loan(request, customer_id):
    assert not is_employee(request.user)
    customer = get_object_or_404(Customer, pk=customer_id)
    customerAccounts = Account.objects.filter(customer=customer).filter(account_type='bank account')
    context = {
        'customer': customer,
        'customerAccounts': customerAccounts
    }
    if request.method == 'POST':
        # Create the account
        account = Account()
        account.customer = customer
        account.account_type = 'Loan'
        account.save()

        # Make a ledger where we take 500 from the loan account and add 500 to the chosen account
        amount = request.POST['amount']
        debit_account = account.pk
        credit_account = request.POST['toAccount']
        text = request.POST['text']
        Ledger.transaction(int(amount), debit_account, credit_account, text)

        return redirect('banking_app:index')

    return render(request, 'banking_app/add_loan.html', context)

# Customer view - paying off a loan
@login_required
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
            Ledger.transaction(int(amount), debit_account, credit_account, text)
            
            if account.balance == 0:
                account.delete()

            return redirect('banking_app:index')
        elif int(amount) > -account.balance:
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

    return render(request, 'banking_app/add_customer.html', context)

# Employee view - editing a customer
@login_required
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