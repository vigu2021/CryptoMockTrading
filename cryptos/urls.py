from django.urls import path
from .views import home_page,get_updated_prices,spot,market_order_form,limit_order_form,stop_limit_order_form
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/',home_page,name='home_page'),
    path('api/get-updated-prices/', get_updated_prices, name='get_updated_prices'),
    path('spot/', spot, name='spot'),
    path('orders/market/', market_order_form, name='market_order_form'),
    path('orders/limit/', limit_order_form, name='limit_order_form'),
    path('orders/stop-limit/', stop_limit_order_form, name='stop_limit_order_form'),]