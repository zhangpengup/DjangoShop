import hashlib

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
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

# ajax校验用户名
def ajax_user(request):
    result = {"state":"error","content":""}
    username = request.GET.get("username")
    if username:
        user = Seller.objects.filter(username=username).first()
        if user:
            result["content"] = "用户名已存在~请换一个试试"
        else:
            result["state"] = "success"
    else:
        result["content"] = "用户名不能为空"
    return JsonResponse(result)

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
                    response.set_cookie("user_id",user.id)
                    request.session["username"] = username
                    return response
    return response


# 装饰器：判断用户是否进行登录了
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
    # 查询当前用户是谁
    user_id = request.COOKIES.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    #  通过用户查询店铺是否存在(店铺和用户通过用户id关联)
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request,"Store/index.html",locals())

# 注销
def logout(request):
    response = HttpResponseRedirect("/Store/login/")
    response.delete_cookie("username")
    return response




# 装饰器：判断用户是否注册过店铺
def HasStore(fun):
    def inner(request,*args,**kwargs,):
        user_id = request.COOKIES.get("user_id")
        has_store = Store.objects.filter(user_id=user_id).first()
        if has_store:
            return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Store/rs/")
    return inner

# 店铺注册页
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == "POST":
        post_data = request.POST
        store_name = post_data.get("store_name")
        store_address = post_data.get("store_address")
        store_description = post_data.get("store_description")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")

        store_logo = request.FILES.get("store_logo")
        type_lists = post_data.getlist("type")  # 通过request.post得到类型，但是是一个列表
        user_id = int(request.COOKIES.get("user_id"))

        # 保存非多对多数据
        store = Store()
        store.store_name = store_name
        store.store_address = store_address
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_logo = store_logo   # django1.8之后图片可以直接保存
        store.user_id = user_id
        store.save()   # 保存，生成数据库当中的一条数据
        # 在生成的数据当中添加多对多字段
        for i in type_lists:  # 循环type列表，得到类型id
            store_type = StoreType.objects.get(id=i)  # 查询数据类型
            store.type.add(store_type)  # 添加到类型字段，多对多的映射表
        store.save()
        return HttpResponseRedirect("/Store/index/")
    return render(request,"Store/register_store.html",locals())

# 添加商品
@HasStore
def add_goods(request):
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_store = request.POST.get("goods_store")
        # 注意：图片要用request.FILES
        goods_image = request.FILES.get("goods_image")
        # 开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_store = goods_store
        goods.goods_image = goods_image
        goods.save()
        # 保存多对多数据
        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        return HttpResponseRedirect("/Store/list_goods/")
    return render(request,"Store/add_goods.html")

# 商品列表
@HasStore
def list_goods(request):
    # url来源(上一个地址)
    # referer = request.META.get("HTTP_REFERER")

    # 完成模糊查询
    keywords = request.GET.get("keywords","")  # 查询关键字
    page_num = int(request.GET.get("page_num",1))  # 当前页

    # 如果有输入关键字，查询包含关键字的结果
    if keywords:
        goods_list = Goods.objects.filter(goods_name__contains=keywords)
    # 如果没有搜索关键字，返回所有商品
    else:
        goods_list = Goods.objects.all()

    # 完成分页查询，每页显示3条
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range

    total_num = goods_list.count()  # 总条数
    # 三元表达式 计算得到总页数
    total_page = total_num//3 if total_num/3==0 else total_num//3+1
    # 判断下一页是否是最后一页
    if page_num == total_page:
        next_page = 0
    else:
        next_page = page_num+1
    # 判断上一页是否是第一页
    if page_num == 1:
        pre_page = 0
    else:
        pre_page = page_num-1


    # return render(request,"Store/goods_list.html",{"page":page,"page_range":page_range,"keywords":keywords})
    return render(request,"Store/goods_list.html",locals())
















