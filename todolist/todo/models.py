from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Todo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    important = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created']

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
    
    @property
    def character_image(self):
        character_images = {
            'char1': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEisDy2OZcb2ys4Hd7eCNf2PW5-VhcyOPiVGgG29ftptAUc0j7VmahVZ4Ne7lzj9Ty79at-SDWxKHGNHHrtRNx02pRnyRscF6ZDvm2oFqEOBQiIMUfM8n4lu7dqTF2c6gi48Zxz2EWa40KLXQTCQ2OvMaetQipNuccyujXIdtk97R-rq1tnrlt3pNVHMOxSs/s320/char1.jpg",
            'char2': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg8mO5R62gO068Y3jcc5nXgEJ5fTes4l2dNW9Gfiz-w9Sd5kh2u4LKj22-6P_quOVoXs3C3YoxpmmU1K8D3THHkawSGKTkx1EitF13Qy-86W2qA_s1_H3uzHnV4sR8khnLVsqlC7fGD7izXzPJutdRL3uWHzj75jUW4B52OIWfD2f6iKDKnmxkGM62BSQwM/s320/Char2.jpg",
            'char3': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjuBWeWD6ybcYqdmgB7X7g88c2zQ1OrAB8bFFi3LQolQyKaYKLVnr-zdLrf0V8c4m6-ePpOdEkLGlZieXyEliqnkG-wICfApL5RTjQLHWzQtYZqDur39U6_fy_xFKAVPuiAzPmTAZNLUiW5dk6c0EzpD6NKnYUiJV0pAcIZ1A-OVkwJJANen2rSV2qfdcJC/s320/Char3.jpg",
        }
        return character_images.get(self.character)