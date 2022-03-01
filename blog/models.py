from distutils.command.upload import upload
from hashlib import blake2b
from turtle import Turtle
from django.db import models
from django.contrib.auth.models import User
import os
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

## 게시물의 다대일 관계로 연결된 Category 모델
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    class Meta: ## 모델 이름변경 복수형으로 바꿀때
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"
        
## 게시물과 다대다 관계로 연결된 tag 모댈
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self) :
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


#게시물에 대한 모델
class Post(models.Model):
    title = models.CharField(max_length=30)
    #hook_text content 요약 자극적으로 적기
    hook_text = models.CharField(max_length=100, blank=True)
    #content = models.TextField()
    content = MarkdownxField()

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

    # Tag 다대다 연결
    # WARNINGS : blog.Post.tag: (fields.W340) null has no effect on ManyToManyField. 이기 떄문에 null=True 삭제
    tags = models.ManyToManyField(Tag, blank=True)


    def __str__(self):
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'
    
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1] 
    
    def get_content_markdown(self):
        return markdown(self.content)

## 댓글 모델

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.pk}"

# Create your models here.
