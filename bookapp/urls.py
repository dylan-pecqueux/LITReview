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
    path('ticket/<pk>/new_review/', views.new_review, name='new_review'),
    path('new_review/', views.new_ticket_and_review, name='new_ticket_and_review'),
    path('posts/', views.posts, name='posts'),
    path('review/<pk>/update', views.update_review, name='update_review'),
    path('review/<pk>/delete', views.delete_review, name='delete_review'),
    path('ticket/<pk>/update', views.update_ticket, name='update_ticket'),
    path('ticket/<pk>/delete', views.delete_ticket, name='delete_ticket'),
]