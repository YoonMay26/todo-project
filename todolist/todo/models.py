from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)  # 여기가 변경되어야 함
    deadline = models.DateTimeField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    important = models.IntegerField(default=0)

    def __str__(self):
        return self.title