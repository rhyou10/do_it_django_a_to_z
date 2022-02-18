from re import template
from urllib import request, response
from django.shortcuts import redirect, render
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from django.utils.text import slugify #이 값을 name로 갖는 태그가 있다면 가져오고 없다면 새로만들게 한다.

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

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

def category_page(request, slug):
    if slug=='no_category':
        category='미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count(),
            'category' : category,
        }
    )
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'tag' : tag,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count(),
        }
    )

#포스트 생성 뷰
# LoginRequiredMixin 로그인이 필수로 들어가야한다.
# UserPassesTestMixin 로그인후 포스트 작성시 작성 권한 여부 확인
class PostCreate(LoginRequiredMixin, UserPassesTestMixin , CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self): #사용자 인증함수? 사용자가 주어진 테스트를 통과했는지 확인하는 기능
        return self.request.user.is_superuser or self.request.user.is_staff
    # author 채우기 
    def form_valid(self, form):
        current_user = self.request.user

        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser): # is_authenticated 사용자의 로그인 유무
            form.instance.author = current_user

            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']
    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

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
