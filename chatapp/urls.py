from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('request/', Request.as_view(), name='send_chat_request'),
    path('request/<int:pk>/<str:action>', Request.as_view(), name='respond_chat_request'),
    path('chatHistory/<userid>', chatHistory.as_view() ),
    path('pendingRequest/', PendingRequestsView.as_view() ),
    path('RequestStatus/<int:id>/', ChatRequestStatus.as_view() ),
]