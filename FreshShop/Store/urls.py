from django.urls import path
from django.urls import re_path
from Store.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('logout/',logout),
    path('au/',ajax_user),
    path('rs/',register_store),
    path('ag/',add_goods),
    path('agt/',add_goods_type),


    re_path('^$',index),
    # 商品详情页
    re_path(r'^goods/(?P<goods_id>\d+)',goods),
    # 修改商品信息
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),
    # 商品列表页
    re_path(r'list_goods/(?P<state>\w+)',list_goods),
    # 设置商品状态
    re_path(r'set_goods/(?P<state>\w+)',set_goods),
]