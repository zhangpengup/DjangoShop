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
    result = {"content":""}  # 校验用信息
    response = render(request,"Store/login.html",locals())
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            # 校验登录的用户名是否存在
            user = Seller.objects.filter(username=username).first()
            if user:
                # 对前端输入的密码进行加密
                web_password = set_password(password)
                # 校验请求是否来源于登录页面
                cookies = request.COOKIES.get("login_from")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    # 校验是否登录
                    response.set_cookie("username",username)
                    request.session["username"] = username

                    # cookie提供用户id方便其他功能查询
                    response.set_cookie("user_id",user.id)

                    # 校验是否有店铺
                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie("has_store",store.id)
                    else:
                        response.set_cookie("has_store","")
                    return response
                else:
                    result["content"] = "密码不正确"
            else:
                result["content"] = "用户名不存在"
        else:
            result["content"] = "用户名或密码不能为空"
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
    # user_id = request.COOKIES.get("user_id")
    # if user_id:
    #     user_id = int(user_id)
    # else:
    #     user_id = 0
    # #  通过用户查询店铺是否存在(店铺和用户通过用户id关联)
    # store = Store.objects.filter(user_id=user_id).first()
    # if store:
    #     is_store = 1
    # else:
    #     is_store = 0
    return render(request,"Store/index.html",locals())

# 注销
def logout(request):
    response = HttpResponseRedirect("/Store/login/")
    # 清除所有cookies
    for key in request.COOKIES:  # 获取当前所有cookie
        response.delete_cookie(key)
    return response







# 店铺注册页
@LoginValid
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
        response = HttpResponseRedirect("/Store/index/")
        # 完成注册店铺后，改变COOKIE中has_store的值
        response.set_cookie("has_store",store.id)
        return response
    return render(request,"Store/register_store.html",locals())

# 添加商品
@LoginValid
def add_goods(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_type = request.POST.get("goods_type")
        # 注意：图片要用request.FILES
        goods_image = request.FILES.get("goods_image")
        # 使用cookie当中的店铺id
        goods_store = request.COOKIES.get("has_store")
        # 开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        # 保存外键（多对一关系）
        goods.goods_type = GoodsType.objects.get(id=int(goods_type))
        goods.save()
        # 保存多对多数据
        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        return HttpResponseRedirect("/Store/list_goods/up/")
    return render(request,"Store/add_goods.html",locals())

# 商品列表
@LoginValid
def list_goods(request,state):
    # 判断商品状态,1代表待售，0代表下架商品
    if state == "up":
        state_num = 1
    else:
        state_num = 0

    # 完成模糊查询
    keywords = request.GET.get("keywords","")  # 查询关键字
    page_num = int(request.GET.get("page_num",1))  # 当前页

    # 查询店铺,没有店铺时是不显示入口的所以用get不会报错
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id=int(store_id))

    # 如果有输入关键字，查询包含关键字的结果
    if keywords:
        # goods_list = Goods.objects.filter(goods_name__contains=keywords)
        # store表中没有多对多关系 用goods_set方法反查；
        goods_list = store.goods_set.filter(goods_name__contains=keywords,goods_state=state_num)
    # 如果没有搜索关键字，返回所有商品
    else:
        # goods_list = Goods.objects.all()
        goods_list = store.goods_set.filter(goods_state=state_num)


    # 完成分页查询
    paginator = Paginator(goods_list,3)  # 使用分页模块，每页显展示3条
    page = paginator.page(int(page_num)) # 当前页所展示的3条记录
    page_range = paginator.page_range

    total_num = goods_list.count()  # 总条数
    # 三元表达式 计算得到总页数
    total_page = total_num//3 if total_num%3==0 else total_num//3+1
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

# 商品详情页
@LoginValid
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    return render(request,"Store/goods.html",locals())

# 商品修改页
@LoginValid
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_image = request.FILES.get("goods_image")
        # 开始修改数据
        # 获取当前商品，goods_id作为参数是字符串形式
        goods = Goods.objects.get(id=int(goods_id))
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image: # 如果有上传的图片再发起修改
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/Store/goods/%s"%goods_id)
    return render(request,"Store/update_goods.html",locals())


# 上下架、销毁
def set_goods(request,state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id")
    referer = request.META.get("HTTP_REFERER")
    if id:
        goods = Goods.objects.filter(id=id).first()
        if state == "delete":  # 销毁商品
            goods.delete()
        else:
            goods.goods_state = state_num  # 修改状态
            goods.save()
    # 跳转到请求来源页
    return HttpResponseRedirect(referer)

# 添加与展示商品类型
def add_goods_type(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        goodstype = GoodsType()
        goodstype.type_name = name
        goodstype.type_description = description
        goodstype.type_image = image
        goodstype.save()
        return HttpResponseRedirect("/Store/agt/")

    return render(request,"Store/add_goods_type.html",locals())


















