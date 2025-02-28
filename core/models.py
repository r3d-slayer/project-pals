from django.db import models
from accounts.models import User
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    username=models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length= 10000)
    posted_on = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(default='')

    def __str__(self) -> str:
        return self.title
    
