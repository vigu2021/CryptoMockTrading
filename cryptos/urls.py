from django.urls import path
from .views import home_page,get_updated_prices
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/',home_page,name='home_page'),
    path('api/get-updated-prices/', get_updated_prices, name='get_updated_prices'),
]