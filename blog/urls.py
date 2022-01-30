from django.urls import URLPattern, path
from .import views

urlpatterns = [
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index), fbv
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),

]