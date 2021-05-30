"""Messaging.py"""
from django.core.mail import send_mail

def email_message(message_dict):
    """Send user credentials to new user"""
    contents = f"""
    Welcome! You have been created as a customer for NES Bank. Click the following link and insert your credentials in order to activate your account.
    http://127.0.0.1:8000/account/two_factor/setup/
    Make sure you have downloaded the Google Authenticator App. If you do not have it yet, then get it. 
   
    Your username: {message_dict['username']}
    Your password: {message_dict['password']}
   
    """
    print(message_dict)

# send_mail function is commented out due to ban from sendinblue.com
# and the function will therefore not send an actual email

#    send_mail(
#       'Activate your account',
#       contents,
#       'nata2653@stud.kea.dk',
#       [message_dict['email']],
#       fail_silently=False
#    )

def email_statement(message_dict):
    """Send account statement to user"""
    statements = []
    activities = message_dict['activities']
    for activity in activities:
        statements.append(str(activity))
    contents = """
        {}
    """.format("\n".join(statements))
    print(contents)

# send_mail function is commented out due to ban from sendinblue.com
# and the function will therefore not send an actual email

    # send_mail(
    #     'Bank statements',
    #     contents,
    #     'ewax0437@stud.kea.dk',
    #     [message_dict['user_email']],
    #     fail_silently=False
    # )
