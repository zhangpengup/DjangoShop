import hashlib

from django.shortcuts import render
from django.http import HttpResponseRedirect

from Store.models import *
# Create your views here.

# 密码加密功能
def set_password(password):
    result = hashlib.md5()
    result.update(password.encode())
    return result.hexdigest()

# 注册功能
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            selller = Seller()
            selller.username = username
            selller.password = set_password(password)
            selller.nickname = username
            selller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,"Store/register.html")

# 登录功能
def login(request):
    response = render(request,"Store/login.html")
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get("login_from")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username",username)
                    request.session["username"] = username
                    return response
    return response


# 装饰器
def LoginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Seller.objects.filter(username=c_user).first()
            if user :
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Store/login/")
    return inner

# 首页
@LoginValid
def index(request):
    return render(request,"Store/index.html")

# 注销
def logout(request):
    response = HttpResponseRedirect("/Store/login/")
    response.delete_cookie("username")
    return response


# 模板页
def base(requeset):
    return render(requeset,"Store/base.html")

# 404
def notfound(request):
    return render(request,"Store/404.html")

def blank(request):
    return render(request,"Store/blank.html")