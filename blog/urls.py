from django.urls import URLPattern, path
from .import views

urlpatterns = [
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index), #fbv
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('create_post/', views.PostCreate.as_view()),
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('tag/<str:slug>/', views.tag_page),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('<int:pk>/new_comment/', views.new_comment),


]