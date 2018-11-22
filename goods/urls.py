from django.conf.urls import url
from . import views

urlpatterns = [
    # 商品列表
    url(r'^goods_list/', views.goods_list, name='goods_list'),

    # 商品信息添加页面--商品信息提交
    url(r'^goods_add/', views.goods_add, name='goods_add'),
    url(r'^do_goods_add/', views.do_goods_add, name='do_goods_add'),

    # 商品删除
    url(r'^do_goods_delete/(?P<pk>\d+)',views.do_goods_delete,name='do_goods_delete'),

    # 商品信息修改界面--商品信息修改后提交
    url(r'^goods_modify/(?P<pk>\d+)', views.goods_modify, name='goods_modify'),
    url(r'^do_goods_modify/', views.do_goods_modify, name='do_goods_modify'),

    # 主页
    url(r'^index/', views.index, name='index'),
    # 商品类型
    url(r'^goods_type/', views.goods_type, name='goods_type'),
    # 商品详情
    url(r'^goods_details/', views.goods_details, name='goods_details'),

]
