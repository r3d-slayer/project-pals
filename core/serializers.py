from .models import *
from .models import Post
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.utils.timesince import timesince

class Post_serializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title','category','description'] 
    def validate(self, attrs):
        user = self.context.get('user')
        username= self.context.get('username')
        title = attrs.get('title')
        description = attrs.get('description')
        category = attrs.get('category')
        
        Post.objects.create(username=username, title = title, description = description, category = category, email= user.email)
        
        return attrs

class User_Post_serializer(serializers.ModelSerializer):
    username = serializers.CharField(source='username.username', read_only=True)
    userid = serializers.CharField(source='username.id', read_only=True)
    image = serializers.CharField(source='username.profile.image', read_only=True)
    
    time_since_posted = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','username', "image",'userid','title','category','description','posted_on', 'email','time_since_posted']
    
    def get_time_since_posted(self, obj):
        now = timezone.now()
        duration = now - obj.posted_on
        if duration.days >= 1:
                return f"{duration.days} days ago"
        hours = duration.seconds // 3600
        return f"{hours} hours ago"
        print(duration.days, duration.seconds)
        return timesince(obj.posted_on, now)