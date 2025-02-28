from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from rest_framework import status,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from .renderers import UserRenderer   
from .helpers import send_connect_mail   
import random 
from rest_framework import generics
from django.core.paginator import Paginator

@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
class create_post(APIView):
    def post(self, request):
        data = request.data
        user = request.user
        serializer = Post_serializer(data = data, context={'user':request.user,'username':request.user})
        if serializer.is_valid(raise_exception=True):
            # print(user,data)
            return Response({"status":200,"msg": "Post created successfully"},status=status.HTTP_200_OK)
        else:
            return Response({'status':status.HTTP_400_BAD_REQUEST, 'msg': 'something went wrong'},status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pass
    def put(self):
        pass
    def delete(self, request):
        id = request.data.get("id")
        print(id)
        try:
            post = Post.objects.get(id = id)
        except Post.DoesNotExist:
            return Response({"response": "No such post found"}, status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response({"response": "Post deleted successfully"}, status=status.HTTP_202_ACCEPTED)

# @renderer_classes([UserRenderer])
# @permission_classes([IsAuthenticated])
# class show_all_posts(APIView):
#     def get(self, request):
#         user = request.user
#         posts = list(Post.objects.exclude(username=user))
#         random.shuffle(posts)
#         random_posts = posts[:]
#         serializer = User_Post_serializer(random_posts, many=True)
#         return Response({'status': status.HTTP_200_OK, 'payload':serializer.data})


class show_all_posts(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # posts = Post.objects.all().order_by('?')
        user = request.user
        seed = request.GET.get('seed', str(random.randint(0, 1000000)))
        posts = list(Post.objects.exclude(username=user))
        random.seed(seed)  
        random.shuffle(posts)

        # Pagination
        paginator = Paginator(posts, 5)
        page_number = request.GET.get('page', 1)  
        page_obj = paginator.get_page(page_number)

        # Serialize the posts
        serializer = User_Post_serializer(page_obj, many=True)

        # Build the next and previous URLs
        next_page = f'http://localhost:8000/api/core/show-post/?page={page_obj.next_page_number()}&seed={seed}' if page_obj.has_next() else None
        previous_page = f'http://localhost:8000/api/core/show-post/?page={page_obj.previous_page_number()}&seed={seed}' if page_obj.has_previous() else None

        # Return paginated posts and navigation info
        return Response({
            'posts': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'next_page': next_page,
            'previous_page': previous_page,
        })

@renderer_classes([UserRenderer])
@permission_classes([IsAuthenticated])
class connect(APIView):
    def post(self, request):
        data = request.data
        initiater = User.objects.get(email = data.get('email'))
        if(send_connect_mail(initiater,request.user)):
            return Response({'status': status.HTTP_200_OK, "message": "mail sent successfully"})
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'msg': 'something went wrong'},status=status.HTTP_400_BAD_REQUEST)    


class show_user_post(generics.ListAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = User_Post_serializer
                    
    def get_queryset(self):
       return Post.objects.filter(user=self.request.user)
    

class show_any_user_post(generics.ListAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    # queryset
    serializer_class = User_Post_serializer
    def list(self, request, *args, **kwargs):
        username =self.kwargs['username']
        user=request.user
        try:
            user= User.objects.get(username=username)
            posts=list(Post.objects.filter(username=user.id))
            if posts:
                serializer = User_Post_serializer(posts, many = True)
                return Response({'status': status.HTTP_200_OK, 'payload':serializer.data})
            else:
                return Response({'status': status.HTTP_404_NOT_FOUND, 'message':"no posts found"})
        except:
            return Response({'status': status.HTTP_404_NOT_FOUND, "message":"no user found"})


class searchPost(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    serializer_class = User_Post_serializer
    queryset = Post.objects.all()

    def list(self, request, *args, **kwargs):
        category =self.kwargs['category']
        # if category != 'all':
        user=request.user
        print(category)
        posts= list(Post.objects.filter(category__contains=category).exclude(username=user))
        serializer= User_Post_serializer(posts, many=True)
        return Response({'status': status.HTTP_200_OK, 'payload':serializer.data})
        # else:
        #     posts2= list(Post.objects.all())
        #     serializer= User_Post_serializer(posts2, many=True)
        #     print(serializer.data)
        #     return Response({'status': status.HTTP_200_OK, 'payload':serializer.data})
