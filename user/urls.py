from django.conf.urls import url
from . import views
# from django.urls import path


urlpatterns = [
    #注册页面
    url(r'^register/', views.register, name='register'),

    #登录页面
    # url(r'^login/',views.login,name='login'),

    url(r'^login/',views.Login.as_view()),

    #注册操作
    url(r'^do_register/',views.do_register,name='do_register'),

    #登录操作
    url(r'^do_login/',views.do_login,name='do_login'),

    #注销
    url(r'^do_logout/',views.do_logout,name='do_logout'),

    #ajax，验证用户名，密码
    # url(r'^check_user/', views.check_user, name='check_user'),
    # url(r'^check_password/', views.check_password, name='check_password'),

    #添加购物车
    url(r'^add_car/', views.add_car, name='add_car'),

    #购物车页面
    url(r'^car_list/', views.car_list, name='car_list'),

    #购物车页面，编辑商品数量edit_num
    url(r'^edit_num/', views.edit_num, name='edit_num'),

    #购物车商品删除
    url(r'^car_del/', views.car_del, name='car_del'),

    #清空购物车
    url(r'^car_clear/', views.car_clear, name='car_clear'),

    #订单详情页面（流程：点击提交订单--跳转到订单详情页--点击确认下单--跳转到付款页面）
    url(r'^order_details/', views.order_details, name='order_details'),

    #确认下单
    url(r'^do_place_order/', views.do_place_order, name='do_place_order'),

    #新增收货地址页面
    url(r'^add_address/', views.add_address, name='add_address'),

    #新增地址提交
    url(r'^do_add_address/', views.do_add_address, name='do_add_address'),

    #收货地址管理页面
    url(r'^receive_address/', views.receive_address, name='receive_address'),

    #用户订单管理页面
    url(r'^user_order_manage/', views.user_order_manage, name='user_order_manage'),

    #用户订单详情
    url(r'^user_order_details/', views.user_order_details, name='user_order_details'),

    #更改收货状态
    url(r'^edit_receive_status/', views.edit_receive_status, name='edit_receive_status'),

    #用户评论页
    url(r'^comments/', views.comments, name='comments'),

    #评论提交
    url(r'^do_comment/', views.do_comment, name='do_comment'),

    #修改密码页面
    url(r'^updatepass/', views.updatepass, name='updatepass'),

    #ajax；编辑密码
    url(r'^edit_pw/', views.edit_pw, name='edit_pw'),

    #验证码
    url(r'^create_code/', views.create_code, name='create_code'),

    #检查注册时的用户名，密码，验证码
    url(r'^check_code/', views.check_code, name='check_code'),

    #激活页面
    url(r'^activate/', views.activate, name='activate'),

    #发送邮件操作
    url(r'^send_msg/', views.send_msg, name='send_msg'),

    #激活操作（修改激活状态）
    url(r'^reg_activate/', views.reg_activate, name='reg_activate'),

    #支付成功跳转页面
    url(r'^pay_return_url/', views.pay_return_url, name='pay_return_url'),

]