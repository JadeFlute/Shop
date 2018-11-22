from django.db import models

# Create your models here.

class ManagerInfo(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=32)
    nickname = models.CharField(max_length=30,null=True)
    shop_name = models.CharField(max_length=50,null=True)
    shop_logo = models.ImageField(null=True,upload_to='media/uploads',default='')
    shop_address = models.CharField(max_length=100,null=True)
    role = models.ForeignKey('Roles',default=1)


#权限表
class Power(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    add_time = models.DateTimeField(auto_now=True)
    add_user = models.CharField(max_length=50)


#角色表
class Roles(models.Model):
    name = models.CharField(max_length=30)
    add_time = models.DateTimeField(auto_now=True)
    add_user = models.CharField(max_length=50)
    #标记删除
    disabled = models.BooleanField(default=False)


#权限和角色的关系表
class Power_Role(models.Model):
    #外键的默认值不能为 0
    power = models.ForeignKey('Power',default=1)
    role = models.ForeignKey('Roles',default=1)








