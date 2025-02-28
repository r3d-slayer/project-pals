from django.shortcuts import render,get_object_or_404
from django.contrib.auth import authenticate,login
from rest_framework import status,permissions
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .renderers import UserRenderer        
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser     
from .models import *
from .serializers import chatSerializer,ChatRequestSerializer
from rest_framework import generics

        
# class Request(APIView):
#     permission_classes = [IsAuthenticated]
#     renderer_classes = [UserRenderer]

#     def post(self, request):
#         # Create a chat request
#         from_user = request.user
#         to_user = User.objects.get(username=request.data['to_user'])
#         # Check if there's already a request
#         existing_request = ChatRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').first() or ChatRequest.objects.filter(from_user=from_user, to_user=to_user, status='accepted').first()
#         if existing_request:
#             return Response({'detail':existing_request.status},)

#         # If no request exists, create a new one
#         ChatRequest.objects.create(from_user=from_user, to_user=to_user)
#         return Response({'detail': 'Pending'}, status=status.HTTP_201_CREATED)

    
#     def get(self, request, pk,action):
#         # Accept or decline the request
#         print(pk,action)
#         chat_request = ChatRequest.objects.get(id=pk, to_user=request.user)
#         if chat_request:
#             if action == 'accept':
#                 chat_request.status = 'accepted'
#                 chat_request.save()
#                 print(chat_request.from_user.id)
#                 return Response({'detail': 'Accepted.','from_user':f'{chat_request.from_user.id}'}, status=status.HTTP_200_OK)
#             elif action == 'decline':
#                 chat_request.status = 'declined'
#                 chat_request.save()
#                 return Response({'detail': 'Declined.'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

class Request(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        from_user = request.user
        to_user = User.objects.get(username=request.data['to_user'])

        existing_request = ChatRequest.objects.filter(
            from_user=from_user, to_user=to_user, status__in=['pending', 'accepted']
        ).first() or ChatRequest.objects.filter(
            from_user=to_user, to_user=from_user, status__in=['pending', 'accepted']
        ).first()

        if existing_request:
            return Response({'detail': existing_request.status})

        new_req= ChatRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'detail': new_req.status,'id':new_req.id}, status=status.HTTP_201_CREATED)

    def get(self, request, pk, action):
        chat_request = ChatRequest.objects.get(id=pk)
        
        if chat_request.to_user == request.user or chat_request.from_user == request.user:
            if action == 'accept':
                chat_request.status = 'accepted'
                chat_request.save()
                return Response({'detail': 'Accepted.', 'from_user': f'{chat_request.from_user.id}'}, status=status.HTTP_200_OK)
            elif action == 'decline':
                chat_request.status = 'declined'
                chat_request.save()
                return Response({'detail': 'Declined.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

class ChatRequestStatus(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    queryset = ChatRequest.objects.all()
    serializer_class = ChatRequestSerializer
    def get_object(self,):
        from_user = self.request.user
        to_user= self.kwargs.get('id')
        try:
            # return ChatRequest.objects.get(from_user=from_user, to_user=to_user)
            return ChatRequest.objects.filter(from_user=from_user, to_user=to_user).first() or ChatRequest.objects.filter(from_user=to_user, to_user=from_user).first()
        except ChatRequest.DoesNotExist:
            return Response({'detail': 'not found.'}, status=status.HTTP_400_BAD_REQUEST)

  

class PendingRequestsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        pending_requests = ChatRequest.objects.filter(to_user=request.user, status='pending')
        serializer = ChatRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)





class chatHistory(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    def list(self, request, *args, **kwargs):
        userid0= int(request.user.id)
        userid1 =int(self.kwargs['userid'])
        thread_name= sorted([int(userid0),int(userid1)])
        thread_name= f"chat_{thread_name[0]}--{thread_name[1]}"
        print(thread_name)
        chats= list(chatModel.objects.filter(thread_name = thread_name))
        serializer=chatSerializer(chats, many = True)
        return Response([serializer.data])
