from django.urls import path
from django.urls import re_path
from Buyer.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('logout/',logout),
    path('goods_list/',goodslist),
    path('pay_order/',pay_order),
    path('pay_result/',pay_result),
    path('goods_detail/',goods_detail),
    path('agn/',ajax_goods_num),
]

urlpatterns += [
    path('base/',base),
]