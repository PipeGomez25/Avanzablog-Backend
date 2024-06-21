from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_posts_view.as_view(), name='list-posts'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
]