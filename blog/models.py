from turtle import Turtle
from django.db import models

#게시물에 대한 모델
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #author 추후 작성 에정

    def __str__(self):
        return f"[{self.pk}]{self.title}"

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'
# Create your models here.
