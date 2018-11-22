from django.http import JsonResponse
from rest_framework.views import APIView
from django.shortcuts import render, reverse, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from user.models import users, Car, OrderInfo, OrderGoodsInfo, AddressInfo, Comment
from goods.models import GoodsInfo
import datetime
import hashlib
import json
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.mail import send_mail
import time
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

# Create your views here.

# 注册页面


def register(request):
    return render(request, 'user/register.html')

# 注册跳转


def do_register(request):
    #     #md5加密，方法1
    #     # md = hashlib.md5()
    #     # md.update(password.encode('utf-8'))
    #     # password_md5 = md.hexdigest()
    #
    #     #方法2
    #     password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()

    username = request.POST.get('username')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    email = request.POST.get('email')
    code = request.POST.get('code').lower()
    code_local = request.session.get('code')

    data = {}
    if code != code_local:
        data['status'] = 0
        data['msg'] = '验证码错误'
        return HttpResponse(json.dumps(data))

    # 检查用户名
    if username == '':
        data['status'] = 1
        data['msg'] = '用户名不能为空'
        return HttpResponse(json.dumps(data))

    username_result = users.objects.filter(username=username).first()
    # 检查用户名是否存在
    if username_result:
        data['status'] = 2
        data['msg'] = '用户名已存在'
        return HttpResponse(json.dumps(data))

    # 检查密码
    if password == '' or password2 == '':
        data['status'] = 3
        data['msg'] = '密码不能为空'
        return HttpResponse(json.dumps(data))

    # data['status'] = 5
    # data['msg'] = '数据正确，注册成功'
    user_obj = users()
    user_obj.username = username
    user_obj.password = password_md5
    user_obj.email = email
    user_obj.save()
    uid = user_obj.id
    request.session['u_id'] = uid
    # return HttpResponse(json.dumps(data))
    return HttpResponseRedirect(reverse('user:activate'))


# 登录页面
# def login(request):
#     return render(request,'user/login.html')

# 登录跳转
def do_login(request):
    # 获取用户输入的用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')
    code = request.POST.get('code')
    code_local = request.session.get('code')
    if code != code_local:
        return HttpResponse('验证码错误')

    # 获取登录用户的对象
    info = users.objects.filter(username=username).first()

    # 将用户信息保存进session
    request.session['u_id'] = info.id
    request.session['u_name'] = username

    # 判断用户是否存在，对象不为None时，用户存在。
    if info is not None:
        # 用户存在，判断密码是否正确
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        if password_md5 == info.password:
            return HttpResponseRedirect('/goods/index')
        else:
            return HttpResponse('用户名不存在或密码错误')
    else:
        # 出于安全考虑，不能只提示用户名不存在
        return HttpResponse('用户名不存在或密码错误')


# 注销
def do_logout(request):
    request.session.clear()
    return HttpResponseRedirect('/user/login')

# 添加购物车操作


def add_car(request):
    # 获取购物车需要的数据（获取失败返回 0）
    goods_id = request.POST.get('goods_id', 0)
    user_id = request.session.get('u_id', 0)
    # 获取网页中的数值型，到这里会变成字符串类型
    count = request.POST.get('count', 0)

    # 验证获取到的数据
    if goods_id == 0:
        return HttpResponse('没有此商品')
    if user_id == 0:
        return HttpResponseRedirect('/user/login')
    if count == 0:
        return HttpResponse('数量错误')

    # 判断商品是否在购物车（是否可以获取该商品对象）
    goods = Car.objects.filter(goods_id=goods_id, user_id=user_id).first()
    carobj = Car()
    if goods is None:
        # 不在购物车，添加数据
        carobj.goods_id = goods_id
        carobj.user_id = user_id
        carobj.number = int(count)
        carobj.save()
    else:
        # 在购物车，只修改本商品的数量
        goods.number += int(count)
        goods.save()

    return HttpResponseRedirect('/user/car_list')

# 登录验证


def verify_login(func):
    def inner_func(request):
        user_id = request.session.get('u_id', 0)
        if user_id == 0:
            return HttpResponseRedirect(reverse('user:login'))
        else:
            return func(request)

    return inner_func


# 购物车页面
@verify_login
def car_list(request):
    user_id = request.session.get('u_id', 0)

    car_list = Car.objects.all()
    return render(request, 'user/cart_list.html', {'car_list': car_list})

# ajax，购物车页面商品数量变化 处理


def edit_num(request):
    # ajax函数会将必要的元素发送给django，django来验证并处理这些元素
    goods_id = request.POST.get('goods_id', 0)
    number = int(request.POST.get('number', 0))
    user_id = request.session.get('u_id', 0)
    alg = request.POST.get('alg', 0)

    # 每次商品数量发生变化，验证用户id，商品id，商品数量
    # 然后将验证结果以json的格式发送给ajax
    data = {}
    if goods_id == 0:
        # 获取失败,状态码为0，将响应消息赋值给msg
        data['status'] = 0
        data['msg'] = '商品获取失败'
        return HttpResponse(json.dumps(data))

    if number == 0:
        data['status'] = 0
        data['msg'] = '获取商品数量失败'
        return HttpResponse(json.dumps(data))

    if user_id == 0:
        data['status'] = 2
        data['msg'] = '请登录'
        data['login_url'] = '/user/login'
        return HttpResponse(json.dumps(data))

    # print(goods.__dict__)
    if alg == 'reduce':
        if number >= 2:
            number = number - 1
    elif alg == 'add':
        # 商品数量修改，验证库存
        car_obj = Car.objects.filter(goods_id=goods_id).first()
        goods_obj = GoodsInfo.objects.filter(id=goods_id).first()
        # print(car_obj.number)
        if car_obj.number >= goods_obj.goods_count:
            data['status'] = 3
            data['msg'] = '库存不足'
            return HttpResponse(json.dumps(data))
        number = number + 1

        # return message(goods_obj.goods_name + '库存不足,请重新选择。<a
        # href="%s">点击返回购物车</a>' % (reverse('user:car_list')))

    # 获取要修改商品的对象，然后根据用户操作来加减数量，并且存入数据库
    result = Car.objects.filter(
        goods_id=goods_id,
        user_id=user_id).update(
        number=number)
    # print(goods.number)

    if result:
        # 获取成功，状态码为1
        data['status'] = 1
        data['msg'] = '商品数量更改成功'
        data['numb'] = number
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '商品数量更改失败'
        return HttpResponse(json.dumps(data))


# ajax；购物车商品删除
def car_del(request):
    goods_id = request.POST.get('goods_id', 0)
    user_id = request.session.get('u_id', 0)

    data = {}
    if goods_id == 0:
        # 获取失败,状态码为0，将响应消息赋值给msg
        data['status'] = 0
        data['msg'] = '商品获取失败'
        return HttpResponse(json.dumps(data))

    if user_id == 0:
        data['status'] = 2
        data['msg'] = '请登录'
        data['login_url'] = '/user/login'
        return HttpResponse(json.dumps(data))

    result = Car.objects.filter(goods_id=goods_id).delete()
    if result:
        data['status'] = 1
        data['msg'] = '商品数量删除成功'
    else:
        data['status'] = 0
        data['msg'] = '商品数量删除失败'

    return HttpResponse(json.dumps(data))

# 清空购物车


def car_clear(request):
    user_id = request.session.get('u_id', 0)

    data = {}
    if user_id == 0:
        data['status'] = 2
        data['msg'] = '请登录'
        data['login_url'] = '/user/login'
        return HttpResponse(json.dumps(data))

    result = Car.objects.filter(user_id=user_id).delete()

    if result:
        data['status'] = 1
        data['msg'] = '商品数量删除成功'
    else:
        data['status'] = 0
        data['msg'] = '商品数量删除失败'

    return HttpResponse(json.dumps(data))

# 订单详情页


def order_details(request):
    # 获取用户id，并验证
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponseRedirect(reverse('user:login'))
    car_list = Car.objects.all()
    address_list = AddressInfo.objects.all()

    list = Car.objects.filter(user_id=user_id)
    total_money = 0
    for cart in list:
        total_money += cart.number * int(cart.goods.goods_xprice)

    return render(request,
                  'user/order_details.html',
                  {'car_list': car_list,
                   'address_list': address_list,
                   'total_money': total_money})

# 处理提交的订单详情，然后重定向到付款页


def do_place_order(request):
    # 获取用户id，并验证
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponseRedirect(reverse('user:login'))

    # 获取用户选择的地址的id，并验证
    address_id = request.POST.get('address_id', 0)
    if address_id == 0:
        return HttpResponse('收货地址无效')

    # 通过地址id和用户id（防止获取地址时，用户不在线，所以加上用户id），
    # 获取地址信息的对象，并验证
    addressinfoobj = AddressInfo.objects.filter(id=address_id).first()
    if addressinfoobj is None:
        return HttpResponse('地址无效')

    orderinfoobj = OrderInfo()
    order_code = '20181010' + str(random.randint(100000, 999999))
    orderinfoobj.order_code = order_code
    total_money = 0
    manager_id = 0
    goods_name_all = ''
    # 循环获取该用户购物车商品的对象
    for carobj in Car.objects.filter(user_id=user_id):
        # 计算总的钱
        s_goods_money = carobj.number * int(carobj.goods.goods_xprice)
        total_money += s_goods_money

        goods_name_all += carobj.goods.goods_name

        # 获取商家id，由于在循环里面，所以获取的是最后一个商家的eid
        manager_id = carobj.goods.manager_id
        # 获取每个商品对象，来判断用户购买数量是否大于库存
        goods_obj = GoodsInfo.objects.filter(id=carobj.goods_id).first()
        # print(carobj.number)
        if carobj.number > goods_obj.goods_count:
            return message(
                goods_obj.goods_name +
                '库存不足,请重新选择。<a href="%s">点击返回购物车</a>' %
                (reverse('user:car_list')))

    orderinfoobj.money = total_money
    orderinfoobj.manage_id = manager_id
    orderinfoobj.user_id = user_id
    orderinfoobj.address = addressinfoobj.address
    orderinfoobj.save()

    ordergoodsobj = OrderGoodsInfo()
    for carobj2 in Car.objects.filter(user_id=user_id):
        # 循环次数等于商品种类，所以，
        # 每循环一次，就在订单商品信息表里面添加一条数据
        s_goods_money = carobj2.number * int(carobj2.goods.goods_xprice)
        ordergoodsobj.order_id = orderinfoobj.id
        ordergoodsobj.goods_id = carobj2.goods_id
        ordergoodsobj.number = carobj2.number
        ordergoodsobj.price = s_goods_money
        ordergoodsobj.save()

    # 信息确认并保存完成后，清空购物车
    Car.objects.filter(user_id=user_id).delete()

    """
     设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
     """
    # 修改配置文件的参数
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'
    alipay_client_config.app_id = '2016092100561552'
    alipay_client_config.app_private_key = 'MIIEpAIBAAKCAQEAqfV9wGAatzwNFHpoeTb3QZssVEzZd1+EVhMxHxIO9+pR0X/fiELSfOjD53GwIoLssxjj7Eq8+jgRZ9zscNKEobTlH1lVOR+y7m1I5Sz6Jjcs5Fvw1s/RppUa3Qh7bfQaCJU4cMndksibgTSM7S1xkDILWJNtaSjJTpIpHhQtWAoa1FYWPmZQWanbETBBHvxTJiJlxXbBcfFweVl86PCSNPD6uUHcZHNNiR0Dh3siedJVv77GQurp6fs54C0FvVV3ocCU76xoOXYIxS/ruoLLjCpEDUcOcG5QGl3MPlsfJ6NBZ0QgBoXQtiUXLB/5rxLo1uwuxpT3B7il3O7s7X18rwIDAQABAoIBAF+KciN3ou0IY+30FdC2Nm559YR6IvF5D2J3rXBi7WkuHspfUOA/eCXhj2cGwNXVtYvEXTQSm4Mpi5dQWNXfcdGZaAekZ0USbbqcUpMKIqDi+WhxysRm1NsJDK3eO8yGoS/b+ntk7xq5jLkoOmSF3EYL69biIWoxFGEHxvdyrj7DnJNI5zdws8LG2e7vGrrHFtXfWS3qH63kSuxiFgG5rKJyxgSOhYapKxMKP6jpFtn9ZFbvWWuJvmEq/RbD8ytlUQ55gqzvQx874BvvE+mYu1jRpU0fcBzj1GsTcXG1j4aUZsO/B8uomnYKrwL8C6vps3TtetEkp/IXh348QeANlOkCgYEA2+mApvDC6U1zWi3kpn6q23qnPhLZ6rYRdfBLHMcePp1TcVft7gU/OYB+KL36iWiyEGFfUp1QZ2ryRxUlLtKbDHGHCSwAPWaKQODL87dtBFCTr1ZyRF2fkb2Qw9CCmdJp+s6lbd7SgMzNYAxqpecfiVyu6VOARtjp19PCUgm3uTUCgYEAxdl1XUomi6L7uAOXzoG0AsOLHbXiJ9xcVA8K3uERcJax/2AIGTlHdAskBCUokoqcIXR/+8RvJJrcvQ2ND93gZAE5646gP+5Mmk1yo4Rj89G7BPy7FYyAgVFwzFP5tqlMKsd4Uix6ei0rLiNOsHF9ykMRBCsaIOTQXT6wQ0cBPtMCgYEAuDnW8wNC5ZtihStpHymCDLeln1S/hebcncadxg/xAFdf7dXRltKCcrN3/L2aQr6YXSyVZGoxT1HCgVXvflgkV7pLe52G3ekm7M7lTNhe1XyDHCH5O9iKstbxjXkBz8b7zYaMA4zlH81yR4JfXXhPbQ1d4k13auKQk6PsaDmH1fkCgYEAjeZ1gr9X/fabS1NoYbgs/354HIsC9Uva/H79cPVDqNisOVkK9exbDyOeZUqxWskHSgdgc5ZjkIFxqDY74hFkitVGUWguDyw+zLyXaCff+FOIKv+Ivt/Smu1qVWI1S4kJE/WUmntELLSQr7qrCWmcqqCHZ9HyH3185CO+D8KxZfkCgYAuweBzWLR2al7DWZtFdWR3XDw+MepoWS2OmCyH2Ek11zeUC0crZMHpxoWlB5f3ABrN3URzbUGSsdslZtjBdDqN6s6Dl+7Iu7wgdV60JDBrS6gqnNYRXRdresckQ2goqbACX9AXSHAM57bRJKkYy1mlwAwlJBywlsmlKq3Tqbcw4w=='
    alipay_client_config.alipay_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArw4+bgGlsoU52PjJmzVdjSw+r1ApgbPL8cJnEfnkBMZ6BaKFQYioZk1+XufCBJcDN0acIyNI1RYs0zMxbmP+0nFVqoXVFt0kjjIBYnlBVJ9imL/krb0/DaM7uLAoIWdKGlKCuj+3QqlrFI6S8MUBN059eEXsKuscWojbBSUJsuMeJ0UyBZZK74J1quFYfESdjdamti+CaFgOfzzqFyTcvyBqamSTpajy+BK836kaDia76/hNBPlHlwB8CAiZ9kK/XahmE1boCP0ay5s66T7BOstD3CZFzD8JvmtKyOYV/nNa82sQBK1VDxLcaO2g761hIcqa68AM3uANMs1mj4dq6wIDAQAB'

    """
    得到客户端对象。
    注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
    logger参数用于打印日志，不传则不打印，建议传递。
    """
    # 根据配置文件生成 客户端对象
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)

    """
    页面接口示例：alipay.trade.page.pay
    """
    # 对照接口文档，构造请求对象
    model = AlipayTradePagePayModel()
    model.out_trade_no = orderinfoobj.order_code
    model.total_amount = total_money
    model.subject = "支付测试"
    model.body = goods_name_all
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    request = AlipayTradePagePayRequest(biz_model=model)
    request.return_url = 'http://47.93.191.192/user/pay_return_url/'
    # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
    response = client.page_execute(request, http_method="GET")
    print("alipay.trade.page.pay response:" + response)

    # 第二种重定向方法，应用名：页面名（找的是路由，更改路径不影响页面跳转）
    return HttpResponseRedirect(response)


# 支付宝回调页面
def pay_return_url(request):
    print(request.POST)
    print(request.GET)
    order_code = request.GET.get('out_trade_no')
    bool = OrderInfo.objects.filter(
        order_code=order_code).update(
        pay_status=1,
        pay_time=datetime.datetime.now())
    # return HttpResponse('回来了')
    return message("支付成功！<a href='%s'>继续购物</a>" % (reverse('goods:index')))


# 新增收货地址页
def add_address(request):
    return render(request, 'user/add_address.html')

# 新增地址提交，然后重定向


def do_add_address(request):
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponseRedirect(reverse('user:login'))
    name = request.POST.get('name', '')
    address = request.POST.get('address', '')
    phone = request.POST.get('phone', '')
    # print(name,address,phone)
    # print(user_id)
    if name == '' or address == '' or phone == '':
        return HttpResponse('姓名，地址，手机号不能为空')
    addressinfo_obj = AddressInfo()
    addressinfo_obj.user_id = user_id
    addressinfo_obj.name = name
    addressinfo_obj.address = address
    addressinfo_obj.phone = phone
    addressinfo_obj.save()

    return HttpResponseRedirect(reverse('user:order_details'))


# 用户订单管理
@verify_login
def user_order_manage(request):
    # 获取用户id，并验证
    user_id = request.session.get('u_id', 0)

    order_list = OrderInfo.objects.filter(user_id=user_id)

    return render(request,
                  'user/user_order_manage.html',
                  {'order_list': order_list})

# 用户订单详情


def user_order_details(request):
    order_id = request.GET.get('order_id', 0)
    order_goods_list = OrderGoodsInfo.objects.filter(order_id=order_id)

    return render(request, 'user/user_order_details.html',
                  {'order_goods_list': order_goods_list})


# 更改收货状态
def edit_receive_status(request):
    data = {}
    # 获取用户id，并验证
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        data['status'] = 0
        data['msg'] = '请重新登录'
        data['login_url'] = '/user/login'
        return HttpResponse(json.dumps(data))

    order_id = request.POST.get('order_id', 0)
    if order_id == 0:
        data['status'] = 0
        data['msg'] = '订单错误'
        return HttpResponse(json.dumps(data))

    result = OrderInfo.objects.filter(
        user_id=user_id,
        id=order_id).update(
        receive_status='1')

    if result:
        data['status'] = 1
        data['msg'] = '收货成功'
        data['order_url'] = '/user/user_order_manage'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '收货失败'
        return HttpResponse(json.dumps(data))


# 用户评论
def comments(request):
    order_id = request.GET.get('order_id', 0)
    if order_id == 0:
        return HttpResponse('获取订单信息失败')
    order_goods_list = OrderGoodsInfo.objects.filter(order_id=order_id)

    return render(request, 'user/comments.html',
                  {'order_goods_list': order_goods_list})


# 评论提交操作
def do_comment(request):
    goods_id_list = request.POST.getlist('goods_id', '0')
    order_id = request.POST.get('order_id', 0)
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponse('请登录')

    for goods_id in goods_id_list:
        comment = Comment()
        comment.goods_id = goods_id
        good_info_obj = GoodsInfo.objects.filter(id=goods_id).first()
        print(good_info_obj.manager_id)
        comment.manager_id = good_info_obj.manager_id
        comment.user_id = user_id
        comment.score = request.POST.get('score' + goods_id)
        comment.content = request.POST.get('comment_content' + goods_id)
        comment.add_time = datetime.datetime.now()
        comment.save()

    result = OrderInfo.objects.filter(
        id=order_id).update(
        comment_status=1,
        comment_time=datetime.datetime.now())
    if result:
        return HttpResponseRedirect(reverse('user:user_order_manage'))
    else:
        return HttpResponse('评论失败')


# 显示修改密码页面
def updatepass(request):
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponse('登录错误，请重新登录')
    return render(request, 'user/updatepass.html')

# ajax；修改密码


def edit_pw(request):
    user_id = request.session.get('u_id', 0)
    if user_id == 0:
        return HttpResponse('登录错误，请重新登录')

    userpass = request.POST.get('userpass')
    userpass_md5 = hashlib.md5(userpass.encode('utf-8')).hexdigest()
    usernewpass = request.POST.get('usernewpass')
    usernewpass_md5 = hashlib.md5(usernewpass.encode('utf-8')).hexdigest()
    useragainpass = request.POST.get('useragainpass')
    data = {}
    user_obj = users.objects.filter(id=user_id).first()
    # 验证原始密码
    if userpass_md5 != user_obj.password:
        data['status'] = 0
        data['msg'] = '原密码错误'
        return HttpResponse(json.dumps(data))

    # 验证两次输入的密码是否一样
    if usernewpass != useragainpass:
        data['status'] = 1
        data['msg'] = '两次输入的密码不同'
        return HttpResponse(json.dumps(data))
    else:
        result = users.objects.filter(
            id=user_id).update(
            password=usernewpass_md5)
        if result:
            data['status'] = 2
            data['msg'] = '修改成功'
            return HttpResponse(json.dumps(data))
        else:
            data['status'] = 3
            data['msg'] = '修改失败'
            return HttpResponse(json.dumps(data))


# 生成验证码
def create_code(request):
    # 创建画布
    background_color = (100, random.randint(200, 250), 100)
    background = Image.new('RGB', (80, 20), background_color)

    # 创建画笔
    draw = ImageDraw.Draw(background)
    codelist = 'AB0CD1EF2GH3IJ4KL5MN6OP7QR8ST9UVWXYZ'
    x = 5
    code = ''
    code_full = ''
    # 生成随机字符
    for i in range(0, 5):
        draw_color = (
            random.randint(
                0, 100), random.randint(
                0, 100), random.randint(
                0, 100))
        font = ImageFont.truetype('simfang.ttf', 22)
        code = codelist[random.randint(0, len(codelist) - 1)]
        code_full += code
        draw.text((x, 0), code, font=font, fill=draw_color)
        x += 15

    # 生成点
    for j in range(150):
        point_color = (
            random.randint(
                100, 250), random.randint(
                100, 250), random.randint(
                100, 250))
        draw.point(
            (random.randint(
                0, 80), random.randint(
                0, 20)), fill=point_color)

    # 生成线
    for k in range(3):
        line_color = (
            random.randint(
                100, 250), random.randint(
                100, 250), random.randint(
                100, 250))
        line_start = (random.randint(0, 10), random.randint(0, 20))
        line_end = (random.randint(70, 80), random.randint(0, 20))
        draw.line((line_start, line_end), fill=line_color, width=1)

    bio = BytesIO()
    background.save(bio, 'png')
    print(code_full)
    request.session['code'] = code_full.lower()
    return HttpResponse(bio.getvalue(), 'image/png')


# 检查登录时的验证码
def check_code(request):
    code = request.POST.get('code').lower()
    code_local = request.session.get('code')
    data = {}
    if code != code_local:
        data['status'] = 0
        data['msg'] = '验证码错误'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 1
        data['msg'] = '验证码正确'
        return HttpResponse(json.dumps(data))

# 激活页面


def activate(request):
    return render(request, 'user/activate.html')

# 注册后，向用户邮箱发送激活邮件


def send_msg(request):
    uid = request.session.get('u_id')
    user_obj = users.objects.filter(id=uid).first()
    host = 'http://127.0.0.1:8000'
    address = reverse('user:reg_activate')
    parameter = {}
    parameter['uid'] = uid
    parameter['t'] = int(time.time())

    url_list = []
    for key, val in parameter.items():
        url_list.append(str(key) + '=' + str(val))

    url_param = '&'.join(url_list)

    url = host + address + '?' + url_param

    token = hashlib.md5(url_param.encode('utf-8')).hexdigest()
    url += '&token=' + token
    request.session['activate_token'] = token

    num = send_mail('激活邮件', '点击下方链接激活账号',
                    'System<m18852950026@163.com>', [user_obj.email],
                    html_message='<a href="%s">验证邮箱</a>' % (url,))

    return message("验证成功！<a href='%s'>点击登录</a>" % (reverse('user:login')))


# 注册后，用户使用邮箱激活
def reg_activate(request):

    uid = request.GET.get('uid', '0')

    # users.objects.count(users.objects.contribute_to_class())

    t = request.GET.get('t')
    # token1 = request.GET.get('token')
    token = request.session.get('activate_token')

    now_time = time.time()

    str = 'uid=' + uid + '&t=' + t
    new_token = hashlib.md5(str.encode('utf-8')).hexdigest()
    print(token)
    print(new_token)

    if token != new_token:
        return HttpResponse('链接无效')

    if now_time - int(t) > 1800:
        return HttpResponse('链接已失效')

    result = users.objects.filter(id=uid).update(activate_status=1)
    if result:
        return message('邮箱验证成功')
    else:
        return HttpResponse('激活失败')

# 通用消息响应


def message(msg='操作成功'):
    return render_to_response('user/message.html', {'msg': msg})


# 收货地址页面
def receive_address(request):
    address_list = AddressInfo.objects.all()
    return render(request, 'user/receive_address.html',
                  {'address_list': address_list})


# from rest_framework.views import Response


class Login(APIView):
    def get(self, request, format=None):
        user_obj = users.objects.get(id=9)
        username = user_obj.username
        password = user_obj.password
        print(username, password)

        resp = {
            'username': username,
            'password': password,
        }
        return JsonResponse(resp)
