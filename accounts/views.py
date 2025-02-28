from django.shortcuts import render,get_object_or_404
from django.contrib.auth import authenticate,login
from rest_framework import status,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from .helpers import *
from .renderers import UserRenderer        
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request):
        serializer = UserSerializer(data= request.data)
        if serializer.is_valid():                       
            user = serializer.save()
            return Response({"status":200 , "msg": "otp sent to your email"},status=status.HTTP_201_CREATED)

        return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request):
        serializer = LoginSerializer(data = request.data)
        if  serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email = email, password= password)
            if user is not None:
                token = get_tokens_for_user(user)
                login(request,user)
                return Response({'msg':'login success',"your_id":request.user.id,"username":f"{request.user.username}",'token':token,'status': status.HTTP_200_OK})
        else:
           return Response({'errors': {'non_fields_errors': ['Email or password is incorrect']}},status=status.HTTP_404_NOT_FOUND)
        
        return Response({'errors': {'non_fields_errors': ['Email or password is incorrect']}},status=status.HTTP_404_NOT_FOUND)

class VerifyOtp(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request):
        try:
            data = request.data
            user = User.objects.get(email= data.get('email'))
            otp = data.get('otp')
            if user.otp == otp:
                user.is_email_verified = True
                user.save()
                return Response({'status':status.HTTP_200_OK, 'msg': 'email verified'})
            return Response({'status':status.HTTP_400_BAD_REQUEST, 'msg': 'invalid otp'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:        
            return Response({'status':status.HTTP_400_BAD_REQUEST, 'msg': 'something went wrong'},status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request): #to resend otp
        try:
            data = request.data
            user = User.objects.get(email= data.get('email'))
            otp_mail(user)
            return Response({"status":200,"msg": "new otp sent to your email"},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'status':403, 'error': 'something went wrong'})

class ChangePassword(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data = request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"status":200,"msg": "password changed successfully"},status=status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'msg': 'something went wrong'},status=status.HTTP_400_BAD_REQUEST)


class profile(generics.RetrieveUpdateAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = MyProfileSerializer
    def get_object(self):
        return self.request.user.profile
    
class searchUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    serializer_class = MyProfileSerializer
    
    def get(self, request, *args, **kwargs):
        username =self.kwargs['username']      
        user=User.objects.get(username=username)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        profile = Profile.objects.get(user=user)
        serializer = self.get_serializer(profile)
        return Response([serializer.data])
    
class chat_profile(generics.GenericAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatProfileSerializer
    
    def get(self, request, *args, **kwargs):
        userid =self.kwargs['userid']
        user=User.objects.get(id=userid)
        chat_profile = Profile.objects.get(user=user)
        serializer = self.get_serializer(chat_profile)
        return Response([serializer.data],status=status.HTTP_200_OK)

# class chat_profile(generics.GenericAPIView):
#     renderer_classes = [UserRenderer]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ChatProfileSerializer
    
#     def get(self, request, *args, **kwargs):
#         userid =self.kwargs['userid']
#         user=User.objects.get(id=userid)
#         chat_profile = Profile.objects.get(user=user)
#         serializer = ChatProfileSerializer(chat_profile,context={'request': request})
#         return Response({"payload": serializer.data},status=status.HTTP_200_OK)