from django.urls import path

from . import views

app_name = 'bookapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('new_ticket/', views.new_ticket, name='new_ticket'),
    path('feed/', views.feed, name='feed'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subsciptions/<pk>/delete/', views.delete_sub, name='delete_sub'),
]