from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

def send_connect_mail(initiater, contributer,):
    subject = 'connect'
    message = f'''Dear {initiater.first_name},

We are writing to inform you that you have received a connection request. {contributer.first_name}, with the email address {contributer.email}, is interested in connecting with you.

Please log in to your account to view and respond to this request.

Best regards,
Team PartnurUp'''
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [initiater.email]
    send_mail(subject, message, email_from, recipient_list)
    return True