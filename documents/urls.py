from django.urls import path

from documents import views

app_name = 'documents'

urlpatterns = [
    path('library/', views.library, name='library'),
    path('library/upload/', views.upload, name='upload'),
    path('library/<int:pk>/', views.chat, name='chat'),
    path('library/<int:pk>/status/', views.document_status, name='status'),
    path('library/<int:pk>/ask/', views.ask, name='ask'),
    path('library/<int:pk>/delete/', views.delete_document, name='delete'),
]
