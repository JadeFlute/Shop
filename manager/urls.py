from django.conf.urls import url
from . import views

urlpatterns = [
    #登录页面和登录提交
    url(r'^login/',views.login,name='login'),
    url(r'^do_login/',views.do_login,name='do_login'),

    #注销
    url(r'^do_logout/',views.do_logout,name='do_logout'),

    #管理的主界面
    url(r'^main/',views.main),

    #注册和注册提交
    url(r'^openstore/', views.openstore, name='openstore'),
    url(r'^do_openstore/', views.do_openstore, name='do_openstore'),

    #注册成功--欢迎页面
    url(r'^welcome/', views.welcome,name='welcom'),

    #商家订单列表
    url(r'^manager_order_list/', views.manager_order_list, name='manager_order_list'),

    #商家订单信息
    url(r'^order_info/', views.order_info, name='order_info'),

    #商家确认发货后，保存发货状态（发货时间，发货状态码改为1）
    url(r'^edit_send_status/', views.edit_send_status, name='edit_send_status'),

    #未审核评论页面
    url(r'^comment_checking/', views.comment_checking, name='comment_checking'),

    # 已审核评论页面
    url(r'^comment_checked/', views.comment_checked, name='comment_checked'),

    #ajax;修改审核状态
    url(r'^edit_check_status/', views.edit_check_status, name='edit_check_status'),

    #修改库存页面
    url(r'^edit_count/', views.edit_count, name='edit_count'),

    #修改库存操作
    url(r'^do_edit_count/', views.do_edit_count, name='do_edit_count'),

    #用户列表
    url(r'^member_list/', views.member_list, name='member_list'),

    #删除用户
    url(r'^member_del/', views.member_del, name='member_del'),

    #编辑用户信息
    url(r'^member_edit/', views.member_edit, name='member_edit'),

    #ajax；编辑用户信息操作
    url(r'^do_member_edit/', views.do_member_edit, name='do_member_edit'),

]