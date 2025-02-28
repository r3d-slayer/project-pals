from django.contrib import admin
from .models import chatModel, ChatRequest,Recent_chat
# Register your models here.

admin.site.register(chatModel)
admin.site.register(ChatRequest)
admin.site.register(Recent_chat)