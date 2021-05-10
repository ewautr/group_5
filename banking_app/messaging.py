from django.core.mail import send_mail

def email_message(message_dict):
   contents = f"""
   Welcome! You have been created as a customer for NES Bank. Click the following link and insert your credentials in order to activate your account.
   http://127.0.0.1:8000/account/two_factor/setup/
   Make sure you have downloaded the Google Authenticator App. If you do not have it yet, then get it. 
   """
   send_mail(
      'Activate your account',
      contents,
      'nata2653@stud.kea.dk',
      [message_dict['email']],
      fail_silently=False
   )