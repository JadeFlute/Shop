from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import GoodsInfo, GoodsType
from manager.models import ManagerInfo, Power, Roles, Power_Role
import uuid
from django.conf import settings
from QSHOP_2.power_check import power_check

# Create your views here.

# 商品列表显示


def goods_list(request):
    # list = GoodsInfo.objects.all()
    # 获取用户id
    user_id = request.session.get('user_id', 0)
    # 获取用户自己的商品：外键manager_id=用户id  的商品
    list = GoodsInfo.objects.filter(manager_id=user_id)
    return render(request, 'goods/goods_list.html', {'list': list})

# 商品增加页面 显示
# @power_check


def goods_add(request):

    goods_type_list = GoodsType.objects.filter()
    print(goods_type_list)
    return render(request, 'goods/goods_add.html',
                  {'goods_type_list': goods_type_list})

# 商品增加完成后 提交跳转


def do_goods_add(request):
    # 从网页中获取元素的值
    goods_num = request.POST['goods_num']
    goods_name = request.POST['goods_name']
    goods_oprice = request.POST['goods_oprice']
    goods_xprice = request.POST['goods_xprice']
    goods_count = request.POST['goods_count']
    goods_method = request.POST['goods_method']
    goods_info = request.POST['goods_info']
    # 从网页中获取图片（文件）
    goods_pic = request.FILES.get('goods_pic')

    # 获取多个图片
    # goods_pic_list = request.FILES.getlist('goods_pic')

    goods_address = request.POST['goods_address']
    goods_content = request.POST['goods_content']

    # 从select下拉表单中获取选中项（选中种类）的 id
    type_id_now = request.POST['type_id_now']

    # for goods_pic in goods_pic_list:

    # 判断图片格式
    hix = ['image/png', 'image/jpeg', 'image/gif']
    if goods_pic.content_type not in hix:
        return HttpResponse('图片格式不正确')

    # 将用户上传的图片重命名
    file_suffix = goods_pic.name.split('.')[-1]
    new_file_name = str(uuid.uuid1()) + '.' + file_suffix

    # 保存图片
    # 数据库存储的相对路径
    save_path = '/media/uploads/' + new_file_name
    # 保存图片的绝对路径，settings.MEDIA_ROOT：从设置中取出设置好的根路径（即：static）
    file_path = settings.MEDIA_ROOT + save_path
    # 以二进制格式加载图片，准备写入
    with open(file_path, 'wb+') as f:
        # chunks：分块写入，防止图片过大，导致内存不足
        for file in goods_pic.chunks():
            f.write(file)

    # 登录验证
    user_id = request.session.get('user_id', 0)
    if user_id == 0:
        return HttpResponse('请先登录')

    try:
        GoodsInfo.objects.create(goods_num=goods_num,
                                 goods_name=goods_name,
                                 goods_oprice=goods_oprice,
                                 goods_xprice=goods_xprice,
                                 goods_count=goods_count,
                                 goods_method=goods_method,
                                 goods_info=goods_info,
                                 goods_pic=save_path,
                                 goods_address=goods_address,
                                 goods_content=goods_content,
                                 manager_id=user_id,
                                 type_id=type_id_now)

        return HttpResponseRedirect('/goods/goods_list')
    except BaseException:
        return HttpResponse('插入失败')

# 删除操作


def do_goods_delete(request, pk):
    try:
        user_id = request.session.get('user_id', 0)
        goods = GoodsInfo.objects.get(pk=pk)
        # 删除时，验证商品外键id与登录用户id是否相符
        if goods.manager_id != user_id:
            return HttpResponse('不是你的商品')
        else:
            goods.delete()
        return HttpResponseRedirect('/goods/goods_list')
    except BaseException:
        return HttpResponse('删除失败')

# 商品信息编辑页面显示


@power_check
def goods_modify(request, pk):
    gooods_type_list_2 = GoodsType.objects.all()

    # 获取用户id和商品对象
    user_id = request.session.get('user_id', 0)
    goods = GoodsInfo.objects.get(pk=pk, manager_id=user_id)

    return render(request, 'goods/goods_modify.html',
                  {'goods': goods, 'gooods_type_list_2': gooods_type_list_2})

# 商品信息修改完成后 提交跳转


def do_goods_modify(request):
    goods_id = request.POST['id']
    goods_num = request.POST['goods_num']
    goods_name = request.POST['goods_name']
    goods_oprice = request.POST['goods_oprice']
    goods_xprice = request.POST['goods_xprice']
    goods_count = request.POST['goods_count']
    goods_method = request.POST['goods_method']
    goods_info = request.POST['goods_info']
    goods_pic = request.FILES.get('goods_pic')
    goods_address = request.POST['goods_address']
    goods_content = request.POST['goods_content']

    # 提交时，验证商品外键id是否为登录用户的id
    user_id = request.session.get('user_id', 0)
    goods = GoodsInfo.objects.filter(id=goods_id, manager_id=user_id)
    if goods.manager_id != user_id:
        return HttpResponse('不是你的商品')

    result = goods.update(goods_num=goods_num,
                          goods_name=goods_name,
                          goods_oprice=goods_oprice,
                          goods_xprice=goods_xprice,
                          goods_count=goods_count,
                          goods_method=goods_method,
                          goods_info=goods_info,
                          goods_pic=goods_pic,
                          goods_address=goods_address,
                          goods_content=goods_content)
    if result:
        return HttpResponseRedirect('/goods/goods_list')
    else:
        return HttpResponse('更新失败')

# 主页


def index(request):

    goods_list = GoodsInfo.objects.all()  # 查询所有商品

    return render(request, 'goods/index.html', {'goods_list': goods_list})


def goods_type(request):
    # 获取用户点击的商品类型 的id
    tid = request.GET.get('tid', 0)
    if tid == 0:
        # 获取不到，显示全部商品
        goods_list = GoodsInfo.objects.filter()
    else:
        # 获取到，显示对应种类的商品
        goods_list = GoodsInfo.objects.filter(type_id=tid)

    # 所有商品种类
    goods_type_list = GoodsType.objects.filter()

    return render(request,
                  'goods/goods_type.html',
                  {'goods_type_list': goods_type_list,
                   'goods_list': goods_list})


def goods_details(request):
    # 获取用户点击的商品的 id
    gid = request.GET.get('gid', 0)
    if gid == 0:
        return HttpResponse('页面不存在')
    # 通过获取到的商品id，来获取此商品的对象
    goods = GoodsInfo.objects.filter(id=gid).first()

    # 在页面左侧显示其他商品，这里显示：外键相同的商品
    similar_goods_list = GoodsInfo.objects.filter(type_id=goods.type_id)
    return render(request, 'goods/goods_details.html',
                  {'goods': goods, 'similar_goods_list': similar_goods_list})
