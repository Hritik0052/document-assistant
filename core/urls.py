from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('theme/', views.set_theme, name='set-theme'),
]
