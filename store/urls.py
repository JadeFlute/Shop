from django.conf.urls import url
from . import views

urlpatterns = [
    #店铺列表页面
    url(r'^store_list/', views.store_list, name='store_list'),

    #店铺详情页面
    url(r'^store_details/', views.store_details, name='store_details'),
]