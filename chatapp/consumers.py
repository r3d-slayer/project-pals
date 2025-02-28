import json
from channels.generic.websocket import AsyncWebsocketConsumer
from jwt.exceptions import InvalidTokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from accounts.models import User,Profile
from .models import chatModel,Recent_chat
# from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from .models import chatModel, Recent_chat
from django.utils import timezone
from .serializers import RecentChatSerializer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer

class testConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token_key = self.scope['query_string'].decode().split("=")[1]
        user0 = await self.get_user(token_key)
        if not user0:
            await self.close()
        else:
            self.user0 = user0
            user1 = self.scope["url_route"]["kwargs"]["userId"]
            self.receiver=user1
            user_ids=sorted([int(user0.id),int(user1)])
            self.room_group_name = f"chat_{user_ids[0]}--{user_ids[1]}"
            # print(self.room_group_name)
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json['username']
        thread_name=self.room_group_name
        #Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, 'username':username}
        )
        await self.save_message(username, message, thread_name)



    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,'username':username}))

    # @sync_to_async
    # def get_last_msg(self, thread_name):
    #     return chatModel.objects.filter(thread_name=thread_name).first()

    @database_sync_to_async
    def save_message(self, username,message,thread_name):
        chatModel.objects.create(sender=username, Message=message, thread_name=thread_name)
        user=User.objects.get(username=username)
        user1=User.objects.get(id=self.receiver)
        profile=Profile.objects.get(user=user)
        profile1=Profile.objects.get(user=user1)
        thread= f'chat_{user.id}--{user1.id}'
        # Recent_chat.objects.get_or_create(thread_name=thread_name,sender=profile.user, last_message=message,last_updated=timezone.now())
        if Recent_chat.objects.filter(thread_name=thread).exists():
            recentchat = Recent_chat.objects.get(thread_name=thread)
            recentchat.name = profile1
            recentchat.sender = profile
            recentchat.last_message = message
            recentchat.last_updated = timezone.now()
            recentchat.save()
        else:
            Recent_chat.objects.create(name = profile1,thread_name=thread,sender=profile, last_message=message,last_updated=timezone.now())

        user=User.objects.get(id=self.receiver)
        user1=User.objects.get(username=username)
        profile=Profile.objects.get(user=user)
        profile1=Profile.objects.get(user=user1)
        thread= f'chat_{user.id}--{user1.id}'
        # Recent_chat.objects.get_or_create(thread_name=thread_name,sender=profile.user, last_message=message,last_updated=timezone.now())
        if Recent_chat.objects.filter(thread_name=thread).exists():
            recentchat = Recent_chat.objects.get(thread_name=thread)
            recentchat.name = profile1
            recentchat.sender = profile
            recentchat.last_message = message
            recentchat.last_updated = timezone.now()
            recentchat.save()
        else:
            Recent_chat.objects.create(name = profile1,thread_name=thread,sender=profile, last_message=message,last_updated=timezone.now())

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            access_token = AccessToken(token_key)
            userId = access_token.payload.get('user_id')
            user = User.objects.get(id=userId)
            self.username = user.username
            # print(user.username)
            return user
        except (InvalidTokenError, KeyError):
            return AnonymousUser()


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name='user'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        data=json.loads(text_data)
        username=data['username']
        online_status=data['online_status']
        await self.ChangeOnlineStatus(username,online_status)

    async def disconnect(self,message):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def ChangeOnlineStatus(self, username, online_status):
        # print("in change online status",username,online_status)
        user = User.objects.get(username=username)
        user=Profile.objects.get(user=user)
        
        if online_status == True:
            user.online_status = True
            user.save()
        else:
            user.online_status=False
            user.save()


class RecentChat(AsyncWebsocketConsumer):
    async def connect(self):
        self.user= self.scope["url_route"]["kwargs"]["userid"]
        # print(self.user)
        self.room_group_name = f'recent_chats_{self.user}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        recent_chats = await self.get_recent_chats()
        await self.send_recent_chats(recent_chats)
        # print(self.room_group_name)
        # serialized_data = serializer.data
        # await self.send_recent_chats(serialized_data)


    async def disconnect(self, close_code):
        if self.user:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        recent_chats = await self.get_recent_chats()
        await self.send_recent_chats(recent_chats)
        await self.channel_layer.group_send(
                    self.room_group_name, {'recent_chats': recent_chats}
                )

    async def send_recent_chats(self, recent_chats):
        await self.send(text_data=json.dumps({
            'recent_chats': recent_chats
        }))

    @database_sync_to_async
    def get_recent_chats(self):
        obj = list(Recent_chat.objects.filter(thread_name__startswith= f'chat_{self.user}' ).order_by('-last_updated'))
        serializer = RecentChatSerializer(obj, many=True)
        return serializer.data
    
    async def send_recent_chats_update(self, event):
        recent_chats = await self.get_recent_chats()  
        await self.send_recent_chats(recent_chats) 

    

@receiver(post_save, sender=Recent_chat)
def chat_saved(sender, instance, created, **kwargs):
    # print(f'recent_chats_{instance.sender.user.id}')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'recent_chats_{instance.sender.user.id}',
        {
            'type': 'send_recent_chats_update', 
        }
    )