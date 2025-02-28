from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('create-post/', create_post.as_view() ),
    path('show-post/', show_all_posts.as_view() ),
    path('connect/', connect.as_view() ),
    path('user-posts/', show_user_post.as_view()),
    path('search/<category>', searchPost.as_view()),
    path("any-user-post/<username>", show_any_user_post.as_view()),
]