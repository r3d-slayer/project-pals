import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

def otp_mail(user):
    otp = random.randint(1000,9999)
    user.otp = otp
    user.save()
    subject = 'Your email needs to be verified'
    message = f'Your otp to verify your email is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)    
    return True