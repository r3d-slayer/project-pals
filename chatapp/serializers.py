from .models import *
from accounts.models import User,Profile
from rest_framework import serializers
from datetime import datetime
from django.utils import timezone
from django.conf import settings


class chatSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def get_date(self, obj):
        # Ensure the timestamp is in the correct timezone (IST)
        timestamp = timezone.localtime(obj.timestamp)
        # Convert to the desired date format: dd/mm/yy
        return timestamp.strftime("%d/%m/%y")

    def get_time(self, obj):
        # Ensure the timestamp is in the correct timezone (IST)
        timestamp = timezone.localtime(obj.timestamp)
        # Convert to the desired time format: %I:%M %p
        return timestamp.strftime("%I:%M %p")

    class Meta:
        model = chatModel
        fields = ['sender', 'Message', 'thread_name', 'date', 'time']


class ChatRequestSerializer(serializers.ModelSerializer):
    time=serializers.SerializerMethodField()
    from_user = serializers.CharField(source='from_user.username', read_only=True)
    to_user = serializers.CharField(source='to_user.username', read_only=True)
    class Meta:
        model= ChatRequest
        fields= ["id",'status', 'time','from_user','to_user']
    
    def get_time(self, obj):
        now = timezone.now()
        duration = now - obj.created_at
        if duration.days >= 1:
                return f"{duration.days} days ago"
        hours = duration.seconds // 3600
        return f"{hours} hours ago"

    
class RecentChatSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name.full_name', read_only=True)
    userid = serializers.CharField(source='name.user.id', read_only=True)
    last_updated=serializers.SerializerMethodField()
    online_status= serializers.BooleanField(source="name.online_status",read_only=True)
    image= serializers.SerializerMethodField()
    class Meta:
          model = Recent_chat
          fields= ["name","userid","last_message", "last_updated","online_status","image"]

    def get_image(self, obj):
        request = self.context.get('request', None)
        if obj.name.image:
            image_url = obj.name.image.url
            domain = "http://127.0.0.1:8000/" 
            return f"{domain}{image_url}"  
        return None

    def get_last_updated(self, obj):
        now = timezone.now()
        duration = now - obj.last_updated
        if duration.days >= 1:
                return f"{duration.days}d"
        else:
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            if hours > 0:
                return f"{hours}h"
            else:
                return f"{minutes}m" if minutes > 0 else "Just now"
        
