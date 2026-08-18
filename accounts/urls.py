from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
