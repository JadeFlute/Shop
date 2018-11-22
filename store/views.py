from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from user.models import users, Car, OrderInfo, OrderGoodsInfo, AddressInfo
from manager.models import ManagerInfo
from goods.models import GoodsInfo, GoodsType
from django.db.models import Q
import hashlib
import json
import random
# Create your views here.

# 店铺列表
def store_list(request):
    manager_list = ManagerInfo.objects.filter()

    return render(request, 'store/store_list.html',
                  {'manager_list': manager_list})

# 店铺详情
def store_details(request):
    mid = request.GET.get('mid', 0)
    tid = request.GET.get('tid', 0)

    # 过滤商品时，条件不固定，使用 Q 配合 if判断 来确定添加哪些条件
    q = Q()
    q.connector = 'and'
    q.children.append(('manager_id', mid))
    if tid != 0:
        q.children.append(('type_id', tid))

    type_list = GoodsType.objects.filter()
    goods_list = GoodsInfo.objects.filter(q)

    return render(request,
                  'store/store_details.html',
                  {'goods_list': goods_list,
                   'type_list': type_list,
                   'manager': mid})
