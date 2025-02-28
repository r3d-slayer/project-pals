from .models import *
from .models import User,Profile
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ['email','username', 'password', 'password2','otp','first_name','last_name']
        extra_kwargs ={
            'password': {
                'write_only':True
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('passwords did not match')
        
        if not attrs.get('username'):
            raise serializers.ValidationError("field username is required")
        
        if not attrs.get('first_name'):
            raise serializers.ValidationError("field first name is required")
        
        if not attrs.get('last_name'):
            raise serializers.ValidationError("field last name is required")
        
        return attrs           

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    class Meta:
        model = User
        fields = ['email', 'password']

        
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style= {'input_type':'password'},write_only = True, validators=[validate_password])
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True, validators=[validate_password])
    class Meta:
        fields = ['password','password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError('passwords did not match')
        user.set_password(password)
        user.save()
        return attrs
    
class ChatProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Profile
        fields = ["username","full_name","image","online_status"]

class MyProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=False)
    rating = serializers.CharField(source='user.rating', read_only=False)
    credits = serializers.CharField(source='user.credits', read_only=False)
    user_id = serializers.CharField(source='user.id', read_only=True)
    class Meta:
        model = Profile
        fields = ["user_id", "username","full_name", "bio","verified","image", "rating", "credits","online_status"]

    def validate_username(self, value):
        # Check if the username already exists in the User model
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This username is already taken. Please choose another one.")
        return value
        
    def update(self, instance, validated_data):
        # Update the related User model's username
        user_data = validated_data.pop('user', {})
        username = user_data.get('username')
        credits = user_data.get('credits')
        rating = user_data.get('rating')
        if username:
            instance.user.username = username
            instance.user.save()
        if credits:
            instance.user.credits = credits
            instance.user.save()
        if rating:
            instance.user.rating = rating
            instance.user.save()

        # Update the Profile model's fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.image = validated_data.get('image', instance.image)
        instance.online_status = validated_data.get('online_status', instance.online_status)
        
        instance.save()
        return instance