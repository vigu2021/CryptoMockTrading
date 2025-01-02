from django.urls import path
from .views import landing_page,register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',landing_page,name='landing_page'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),  # Add the register URL
]