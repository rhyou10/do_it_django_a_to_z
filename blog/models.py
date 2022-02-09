from distutils.command.upload import upload
from turtle import Turtle
from django.db import models
from django.contrib.auth.models import User
import os

#게시물에 대한 모델

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    class Meta: ## 모델 이름변경 복수형으로 바꿀때
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"
        
class Post(models.Model):
    title = models.CharField(max_length=30)
    #hook_text content 요약 자극적으로 적기
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #author foeignkey로 만들어지고  CASCADE는 User가 사라질때 model들도 같이 사라진다. 게시물도 같이 사라진다.
    # SET_NULL 의 경우 user가 사라져도 model은 나아있게된다. 대신 user 명이 null값이 된다.
    #author = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # blank =True 카테고리 비어있어도 오류 안나도록
    category = models.ForeignKey(Category, null=True, on_delete= models.SET_NULL, blank=True)


    def __str__(self):
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'
    
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1] 



# Create your models here.
