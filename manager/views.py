from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import ManagerInfo, Roles, Power, Power_Role
from goods.models import GoodsInfo
from user.models import users, Car, OrderInfo, OrderGoodsInfo, AddressInfo, Comment
from django.db.models import Q
import datetime
from django.core.paginator import Paginator
import json
from QSHOP_2.power_check import power_check


# Create your views here.

# 登录
def login(request):
    return render(request, 'manager/login.html')

# 登录跳转


def do_login(request):
    username = request.POST['username']
    password = request.POST['password']

    manager_obj = ManagerInfo.objects.filter(
        username=username, password=password).first()
    # result是一个列表，里面有一个元素，为managerinfo对象
    if manager_obj is not None:
        request.session['username'] = username
        request.session['user_id'] = manager_obj.id

        power_list = []
        for relation in manager_obj.role.power_role_set.filter():
            power_list.append(relation.power.url)
        request.session['power_list'] = power_list
        if manager_obj.id == 4:
            return HttpResponseRedirect('/manager/member_list')
        return HttpResponseRedirect('/manager/main')
    else:
        return HttpResponse('用户名或密码错误')

# 注销后跳转至登录页面


def do_logout(request):
    request.session.clear()
    return HttpResponseRedirect('/manager/login')

# 主页面显示


def main(request):
    goods_count = GoodsInfo.objects.filter(
        manager_id=request.session.get('user_id')).count()

    return render(request, 'manager/main.html', {'goods_count': goods_count})

# 开店页面显示（卖家注册页面）


def openstore(request):
    return render(request, 'manager/openstore.html')


# 注册提交 跳转
def do_openstore(request):
    username = request.POST['username']
    shop_name = request.POST['shop_name']
    nickname = request.POST['nickname']
    shop_address = request.POST['shop_address']
    shop_logo = request.FILES.get('shop_logo')

    try:
        ManagerInfo.objects.create(username=username,
                                   password='000',
                                   shop_name=shop_name,
                                   nickname=nickname,
                                   shop_address=shop_address,
                                   shop_logo=shop_logo,
                                   )
        return HttpResponseRedirect('/manager/welcome')
    except BaseException:
        return HttpResponse('开店失败，请稍后重试！')

# 欢迎页面--显示


def welcome(request):
    return render(request, 'manager/welcome.html')


# 商家订单列表页
def manager_order_list(request):
    # 获取当前页数
    p = request.GET.get('p', 1)
    print(p)

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')
    # 获取每个下拉选框的值
    # 获取不到，给99，是避免与其它状态码重复
    order_code = request.GET.get('order_code', '')
    pay_status = request.GET.get('pay_status', '99')
    send_status = request.GET.get('send_status', '99')

    where = []
    view_where = {}
    # 实例化Q
    q = Q()
    # 添加条件
    q.connector = 'and'
    # 添加 manage_id = manager_id
    q.children.append(('manage_id', manager_id))

    # 判断：如果获取到了下拉选框的值，进行如下操作
    # 将 字段=值 添加进q：为了后面过滤需要的数据
    # 将值添加进where列表：为了后面拼接url：为了根据用户选择来显示不同的url（另外后面还拼接了页数）
    # 将值添加进view_where字典：根据用户选择过滤数据后，如果用户换页会导致选项初始化，
    # 这时需要在下拉表单中判断状态值，来保持选项状态(selected)
    if order_code != '':
        q.children.append(('order_code', order_code))
        where.append(order_code)
        view_where['order_code'] = order_code
    if pay_status != '99':
        q.children.append(('pay_status', pay_status))
        where.append(pay_status)
        view_where['pay_status'] = pay_status
    if send_status != '99':
        q.children.append(('send_status', send_status))
        where.append(send_status)
        view_where['send_status'] = send_status

    # 根据q的条件过滤出用户需要的数据；另外根据id排序，不然换页时，可能会数据错乱
    # 注意：这里获取的是所有数据的对象，分页后，需要回传的参数为当前页的数据对象
    order_list = OrderInfo.objects.filter(q).order_by('id')

    # 使用&拼接url
    url_where = '&'.join(where)

    # 实例化一个分页类的对象，
    # 参数1：需要分页的数据列表（之前根据条件过滤出来的数据）；参数2：每页2条数据
    page_obj = Paginator(order_list, 1)
    # 调用page函数,获取当前页的数据对象
    page_data = page_obj.page(p)

    return render(request, 'manager/manager_order_list.html',
                  {'url_where': url_where,
                   'view_where': view_where,
                   'order_list': page_data})


# 商家订单详情页
def order_info(request):
    order_id = request.GET.get('order_id', 0)
    if order_id == 0:
        return HttpResponse('请选择要查看的订单')

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    order_obj = OrderInfo.objects.filter(
        id=order_id, manage_id=manager_id).first()
    if order_obj is None:
        return HttpResponse('订单不存在')
    # print(order_id)
    # print(manager_id)
    # print(order_obj)
    return render(request, 'manager/order_info.html', {'order_obj': order_obj})


# 修改发货状态
def edit_send_status(request):
    order_id = request.POST.get('order_id', 0)
    print(order_id)
    if order_id == 0:
        return HttpResponse('请选择要发货的订单')

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    result = OrderInfo.objects.filter(
        id=order_id).update(
        send_status=1,
        send_time=datetime.datetime.now())
    if result:
        return HttpResponseRedirect(reverse('manager:manager_order_list'))
    else:
        return HttpResponse('修改失败')


# 未审核评论
def comment_checking(request):
    p = request.POST.get('p', 1)

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect(reverse('manager:login'))

    # 筛选代码流程：获取select标签的值（给其一个name=score）--> 判断是否获取到
    # 注意：从select获取的值为 字符类型，获取不到的返回值为  '0',写if判断时要注意。
    score = request.GET.get('score', '0')

    where = []
    view_where = {}
    q = Q()
    q.connector = 'and'
    q.children.append(('manager_id', manager_id))
    q.children.append(('check_status', 0))

    if score != '0':
        q.children.append(('score', score))
        where.append('score=' + score)
        view_where['score'] = score

    url_where = '&'.join(where)

    comment_list = Comment.objects.filter(q).order_by('id')
    # 打印上面语句的对应sql语句
    print(comment_list.query)

    page_obj = Paginator(comment_list, 1)
    data_list = page_obj.page(p)

    return render(request,
                  'manager/comment_checking.html',
                  {'comment_list': data_list,
                   'url_where': url_where,
                   'view_where': view_where})


# 已审核评论
def comment_checked(request):
    score = request.GET.get('score', '0')
    p = request.GET.get('p', 1)

    manager_id = request.session.get('user_id', 0)
    if manager_id == 0:
        return HttpResponseRedirect('/manager/login')

    where = []
    view_where = {}
    q = Q()
    q.connector = 'and'
    q.children.append(('manager_id', manager_id))

    if score != '0':
        q.children.append(('score', score))
        where.append('score=' + score)  # 分页连接 上保留检索条件
        view_where['score'] = score

    q.children.append(('check_status', 1))

    url_where = '&'.join(where)  # 拼接分页连接的参数

    comment_list = Comment.objects.filter(q)
    pageObj = Paginator(comment_list, 1)
    data = pageObj.page(p)

    return render(request,
                  'manager/comment_checked.html',
                  {'comment_list': data,
                   'url_where': url_where,
                   "view_where": view_where})


# 修改审核状态
def edit_check_status(request):
    comment_id = request.POST.get('comment_id', 0)
    data = {}
    if comment_id == 0:
        data['status'] = 1
        data['msg'] = '请选择要审核的评价'
        return HttpResponse(json.dumps(data))

    # 修改状态
    result = Comment.objects.filter(id=comment_id).update(check_status=1)

    if result:
        data['status'] = 1
        data['msg'] = '修改成功'
        return HttpResponse(json.dumps(data))
    else:
        data['status'] = 0
        data['msg'] = '修改失败'
        return HttpResponse(json.dumps(data))


# 显示修改库存页面
def edit_count(request):
    gid = request.GET.get('gid', 0)
    goods_obj = GoodsInfo.objects.filter(id=gid).first()
    return render(request, 'manager/edit_count.html', {'goods_obj': goods_obj})


# 修改库存操作
def do_edit_count(request):
    gid = request.POST.get('gid', 0)
    count = request.POST.get('count', 0)
    result = GoodsInfo.objects.filter(id=gid).update(goods_count=count)
    print(gid, count)

    data = {}
    if result:
        data['status'] = 1
        data['msg'] = '库存修改成功'
        # 第二种传输json输入的方法，需要导入JsonResponse
        return JsonResponse(data)
    else:
        data['status'] = 0
        data['msg'] = '库存修改失败'
        return JsonResponse(data)


# 超级管理员，用户列表

# @power_check
def member_list(request):
    # user_id = request.session.get('user_id',0)
    # if user_id == 0:
    #     return HttpResponseRedirect('/user/login')

    user_name = request.GET.get('user_name', '')
    shop_name = request.GET.get('shop_name', '')
    role_id = request.GET.get('role', '99')
    p = request.GET.get('p', 1)

    q = Q()
    q.connector = 'and'

    where = []
    view_where = {}

    if user_name != '':
        q.children.append(('username', user_name))
        where.append('username=' + user_name)  # 分页连接 上保留检索条件
        view_where['username'] = user_name

    if shop_name != '':
        q.children.append(('shop_name', shop_name))
        where.append('shop_name=' + shop_name)  # 分页连接 上保留检索条件
        view_where['shop_name'] = shop_name

    if role_id != '99':
        q.children.append(('role', role_id))
        where.append('role=' + role_id)  # 分页连接 上保留检索条件
        view_where['role_id'] = role_id

    # print(view_where)
    url_where = '&'.join(where)  # 拼接分页连接的参数

    data = ManagerInfo.objects.filter(q).order_by('id')
    # print(data.query)

    pageObj = Paginator(data, 2)
    list = pageObj.page(p)

    # 查询角色列表
    role_list = Roles.objects.filter(disabled=0)

    return render(request,
                  'manager/member_list.html',
                  {'list': list,
                   'url_where': url_where,
                   'view_where': view_where,
                   'role_list': role_list})


# 删除用户
# @power_check
def member_del(request):
    id = request.GET.get('id')
    result = ManagerInfo.objects.filter(id=id).delete()
    print(id)

    data = {}
    if result:
        data['status'] = 1
        data['msg'] = '删除成功'
    else:
        data['status'] = 0
        data['msg'] = '删除失败'

    return JsonResponse(data)


# 编辑用户信息页面
# @power_check
def member_edit(request):
    member_id = request.GET.get('member_id')
    member_info = ManagerInfo.objects.filter(id=member_id).first()

    role_list = Roles.objects.filter()

    return render(request, 'manager/member_edit.html',
                  {'member_info': member_info, 'role_list': role_list})


# 编辑用户信息操作
def do_member_edit(request):
    id = request.POST.get('id')
    username = request.POST.get('username')
    nickname = request.POST.get('nickname')
    shop_name = request.POST.get('shop_name')
    shop_address = request.POST.get('shop_address')
    role = request.POST.get('role')
    print(role)

    memberObj = ManagerInfo()
    memberObj.id = id
    memberObj.username = username
    memberObj.nickname = nickname
    memberObj.shop_name = shop_name
    memberObj.shop_address = shop_address
    memberObj.role_id = role
    memberObj.save()

    data = {}
    data['status'] = 1
    data['msg'] = '修改成功'
    return JsonResponse(data)
