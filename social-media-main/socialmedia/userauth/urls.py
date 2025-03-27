from django.contrib import admin
from django.urls import path, include
from socialmedia import settings
from userauth import views
from django.conf.urls.static import static
from .views import add_comment, PostDeleteView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home),
    path('loginn/', views.loginn),
    path('signup/', views.signup),
    path('logoutt/', views.logoutt),
    path('upload', views.upload),
    path('like-post/<str:id>', views.likes, name='like-post'),
    path('#<str:id>', views.home_post),
    path('explore', views.explore),
    path('profile/<str:id_user>', views.profile),
    path('delete/<str:id>', views.delete),
    path('search-results/', views.search_results, name='search_results'),
    path('follow', views.follow, name='follow'),
    path('add_comment/<str:post_id>/', add_comment, name='add_comment'),
    # path('profile/<str:id_user>/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),


]
