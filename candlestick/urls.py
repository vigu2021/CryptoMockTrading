from django.urls import path
from .views import charts_page, chart_view

urlpatterns = [
    path('charts/', charts_page, name='charts_page'),  # Charts page
    path('charts/<str:symbol>/', chart_view, name='chart_view'),  # Dynamic chart page
]