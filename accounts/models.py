from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .manager import UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail  
from django.conf import settings
import random
from django.core.cache import cache

# Create your models here.

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50,default=None)
    last_name = models.CharField(max_length=50,default=None)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    email_token = models.CharField(max_length=200, null=True, blank=True)
    forget_password  = models.CharField(max_length=100, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    credits = models.IntegerField(default=100)
    rating = models.FloatField(default=0.0)
    # skills = models.CharField(max_length=100, blank=True )
    # about = models.CharField(max_length=250, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects = UserManager()

    def name(self):
        return self.username
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


@receiver(post_save, sender = User)
def send_mail_otp(sender, instance, created, **kwargs):
    if created:
        try:
            otp = random.randint(1000,9999)
            # cache.set(instance.email, otp, timeout=60)
            instance.otp = otp
            instance.save()
            subject = 'Your email needs to be verified'
            message = f'Your otp to verify your email is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [instance.email]
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(e)

def otp_mail(email, user):
    if cache.get(email):
        return False
    otp = random.randint(1000,9999)
    cache.set(email, otp, timeout=60)
    user.otp = otp
    user.save()
    subject = 'Your email needs to be verified'
    message = f'Your otp to verify your email is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)    
    return True

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name =models.CharField(default="" ,max_length=300)
    bio = models.CharField(max_length=500)
    image = models.ImageField(default="media/user_images/default.webp", upload_to="media/user_images/")
    verified = models.BooleanField(default=False)
    online_status= models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set default full_name to user's first_name if not provided
        if not self.full_name:
            self.full_name = f"{self.user.first_name} {self.user.last_name}"

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.full_name
    
@receiver(post_save, sender=User)    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user= instance)
        profile.save()

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#         profile = instance.profile
#         profile.save()


