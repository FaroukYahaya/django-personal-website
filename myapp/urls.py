# myapp/urls.py - COMPLETE FILE - Replace your current urls.py with this

from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    # Existing URLs
    path('', views.home_view, name='home'),
    path('publications/', views.publications_list, name='list'),
    path('teaching/', views.teaching, name='teaching'),


    # New Posts URLs
    path('posts/', views.posts_list, name='posts'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
]