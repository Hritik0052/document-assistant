from django.urls import path

from myapp import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/', views.VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOtpView.as_view(), name='resend-otp'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('user/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]
