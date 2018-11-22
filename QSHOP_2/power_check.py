from django.http import HttpResponse
from manager.models import ManagerInfo,Power,Roles,Power_Role


def power_check(func):
    def inner_func(request,*args):
        visit_url = request.resolver_match.url_name
        power_obj = Power.objects.filter(url=visit_url).first()
        if power_obj != None:
            #从session中取出power_list
            power_list = request.session.get('power_list')
            if visit_url not in power_list:
                return HttpResponse('权限不足')
        return func(request)
    return inner_func









