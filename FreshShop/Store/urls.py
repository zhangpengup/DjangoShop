from django.urls import path
from django.urls import re_path
from Store.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('logout/',logout),
    path('base/',base),
    path('nf/',notfound),
    path('blank/',blank),

    re_path('^$',index),
]