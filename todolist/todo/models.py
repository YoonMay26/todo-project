from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)  # 새로운 필드
    complete = models.BooleanField(default=False)
    important = models.IntegerField(default=0)  # Boolean에서 IntegerField로 변경 (0-5 값)

    def __str__(self):
        return self.title