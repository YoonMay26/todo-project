from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
<<<<<<< HEAD
    created = models.DateTimeField(auto_now_add=True)
=======
    created = models.DateTimeField(auto_now_add=True)  
>>>>>>> b8620c29d89f30200f4c9efdfd244a481ea31d57
    deadline = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    important = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True)
    character = models.CharField(max_length=20, choices=[
        ('char1', 'Character 1'),
        ('char2', 'Character 2'),
        ('char3', 'Character 3'),
    ])