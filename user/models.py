from django.db import models

# Create your models here.

class users(models.Model):
    username = models.CharField(max_length=30)
    #md5加密的密码是32位
    password = models.CharField(max_length=32)
    email = models.EmailField(default='')
    activate_status = models.BooleanField(default=False)

#购物车
class Car(models.Model):
    goods = models.ForeignKey('goods.GoodsInfo',default=1)
    user = models.ForeignKey('users',default=1)
    number = models.IntegerField()


#订单详情
class OrderInfo(models.Model):
    order_code = models.CharField(max_length=14,unique=True)
    money = models.DecimalField(max_digits=10,decimal_places=2)#最多10位，小数后保留两位
    add_time = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=150)

    user = models.ForeignKey('users',default=1)
    manage = models.ForeignKey('manager.ManagerInfo', default=1)

    contacts = models.CharField(max_length=30,default='')
    phone = models.CharField(max_length=20,default='')

    pay_status = models.BooleanField(default=False)
    pay_time = models.DateTimeField(null=True)

    send_status = models.BooleanField(default=False)
    send_time = models.DateTimeField(null=True)

    receive_status = models.BooleanField(default=False)
    receive_time = models.DateTimeField(null=True)

    comment_status = models.BooleanField(default=False)
    comment_time = models.DateTimeField(null=True)

#订单里的商品详情
class OrderGoodsInfo(models.Model):
    order = models.ForeignKey('OrderInfo',default=1)
    goods = models.ForeignKey('goods.GoodsInfo',default=1)
    number = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10,decimal_places=2)

#用户收货 信息
class AddressInfo(models.Model):
    address = models.CharField(max_length=100)
    user = models.ForeignKey('users',default=1)
    name = models.CharField(max_length=30,default='')
    phone = models.CharField(max_length=20,default='')


#用户评价表
class Comment(models.Model):
    goods = models.ForeignKey('goods.GoodsInfo',default=1)
    manager = models.ForeignKey('manager.ManagerInfo',default=1)
    user = models.ForeignKey('users',default=1)
    score = models.IntegerField(default=0)
    content = models.CharField(max_length=100,default='')
    add_time = models.DateTimeField(auto_now_add=True)
    #审核状态
    check_status = models.BooleanField(default=False)





