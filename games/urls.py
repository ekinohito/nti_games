from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('login/', views.login_page, name='login'),
    path('auth/', views.auth_page, name='auth'),
    path('logout/', views.logout_page, name='logout'),
    path('user/', views.user_page, name='user_page'),
]
