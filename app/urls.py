from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('resume/', resume, name='resume'),
    path('topshiriq/', topshiriq_dashboard, name='topshiriq'),
    path('topshiriq/api/orders/', topshiriq_add_order, name='topshiriq_add_order'),
]
