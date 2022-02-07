from re import template
from urllib import request
#from django.shortcuts import render
from .models import Post, Category
from django.views.generic import ListView, DetailView

## CBV 클래스 기반 view

class PostList(ListView):
    model = Post
    ordering = '-pk'
    #template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post


"""
#FBV(Fuction base view) 함수기반
def index(request):
    posts = Post.objects.all().order_by('-pk')
    return render(
        request,
        'blog/index.html',
        {
            'posts' : posts
        }
    )


def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/single_post_page.html',
        {
            'post' : post,
        }
    )
"""
# Create your views here.
