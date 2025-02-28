from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view() ),
    path('verify-otp/', VerifyOtp.as_view() ),
    path('login/', LoginView.as_view() ),
    path('profile/', profile.as_view()),
    path('change-password/', ChangePassword.as_view()),
    path('search/<username>', searchUser.as_view()),
    path('chat_profile/<userid>', chat_profile.as_view()),
]