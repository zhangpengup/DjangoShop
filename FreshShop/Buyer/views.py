from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from Store.models import *
from Store.views import set_password

from alipay import AliPay
# Create your views here.

def base(request):
    return render(request,"Buyer/base.html")

# 登录校验
def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_username = request.COOKIES.get("username")
        s_username = request.session.get("username")
        if c_username and s_username and c_username == s_username:
            user = Buyer.objects.filter(username=c_username).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Buyer/login/")
    return inner

def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        buyer = Buyer()
        buyer.username = username
        buyer.password = set_password(password)  # 保存加密后的密码
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect("/Buyer/login/")
    return render(request,"Buyer/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                if web_password == user.password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    # 校验登录
                    response.set_cookie("username",username)
                    request.session["username"] = username
                    # 方便其他功能查询
                    response.set_cookie("user_id",user.id)

                    return response
    return render(request,"Buyer/login.html")


# 首页显示全部商品类型和部分商品
@loginValid
def index(request):
    goods_type_list = GoodsType.objects.all()
    result_list = []  # 定义一个空列表用来存放结果
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4] # 查询前4条
        if goods_list:  # 如果类型中有值
            goodsType = {
                "id" : goods_type.id,
                "type_name" : goods_type.type_name,
                "type_description" : goods_type.type_description,
                "type_image" : goods_type.type_image,
                "goods_list" : goods_list
            } # 构建输出结果
            # 有数据的类型放入result_list
            result_list.append(goodsType)
    return  render(request,"Buyer/index.html",locals())

# 注销
def logout(request):
    response = HttpResponseRedirect("/Buyer/login/")
    # 清除所有cookies
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response



# 前端商品列表页
@loginValid
def goodslist(request):
    type_id = request.GET.get("type_id")
    goods_type = GoodsType.objects.filter(id=type_id).first()
    if goods_type:
        # 查询所有在售商品
        goodsList = goods_type.goods_set.filter(goods_state=1)

    return render(request,"Buyer/goods_list.html",locals())


# 商品详情页
def goods_detail(request):
    goods_id = request.GET.get("goods_id")
    goods = Goods.objects.filter(id=goods_id).first()
    return render(request,"Buyer/goods_detail.html",locals())


# 支付功能
def pay_order(request):
    money = request.GET.get("money") # 获取订单金额
    order_id = request.GET.get("order_id") # 获取订单id
    alipay_public_key = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzKUekbExTdgaNbmFSDObIsTOh4CC9mE+W/UOUgu7g4fsrFxc7apBvGDfHy3Y5Zk40brrGlacc4bAYbHcSMjgPTwZCyiYo+q1uA3hSaVRpxD/TW+Qvw4sf17QS55WljvWepQS6Kncsxcy8lyOmTyhw5ArLsRsjh6H9dM7E26moFixiYXocT2JcA/TwyZCCh2U7igPFJ8rruFriXcjpXz28jjK0uLKJ3El/7iKzYIlXl22C51X/sjNAhd9FZid0RJjYedXH+Nn3yH/gPv8qLKquMVxPMab3XNI6nWVLfAib+iHyy3Ty/sYbc4eXq5LQ4RuKCdz7L1tOAS4HRshCJjD8QIDAQAB
    -----END PUBLIC KEY-----"""
    app_private_key = """-----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEAzKUekbExTdgaNbmFSDObIsTOh4CC9mE+W/UOUgu7g4fsrFxc7apBvGDfHy3Y5Zk40brrGlacc4bAYbHcSMjgPTwZCyiYo+q1uA3hSaVRpxD/TW+Qvw4sf17QS55WljvWepQS6Kncsxcy8lyOmTyhw5ArLsRsjh6H9dM7E26moFixiYXocT2JcA/TwyZCCh2U7igPFJ8rruFriXcjpXz28jjK0uLKJ3El/7iKzYIlXl22C51X/sjNAhd9FZid0RJjYedXH+Nn3yH/gPv8qLKquMVxPMab3XNI6nWVLfAib+iHyy3Ty/sYbc4eXq5LQ4RuKCdz7L1tOAS4HRshCJjD8QIDAQABAoIBAAal4o1XFUPzHj7ajQLgcky52f+65AY++HiiSFnP+cJ3GvAqe/ZYjpQhDX6EzcP/q0Hc8aBEagayvPMvhPl0VRyIJEQhiHvitw6InOX4keN8gN6yHiCmxDlLCjc6qJNu1DPdNZQLWJkUytnmudcuig7BUzXMub4QLdiFiSjDcnRI/nNxK9ngUvnnbgXtoBpjvzXzXJ4GvEWUZFzUTOvQ9xFxmHBgxXoBxY75TRDAa7X0q6LP64UJnLOGG+cRySdc7WZNbJmgpgop8V2t/qyDFGsGIZEJOQJlZ5tKeOzrRb/PBI4mwaNJ6AQA5Ei+BMG7+nudn8G5bny/R0RQlV5HMSUCgYEA6jWVBYF3ySyv9DWiYldROGp9mgRYr6Rxd+OR4ovXtr2nA5vTrxvqnaCrvynhtfCJcDZJwyAl40m5qEOnMWjN/JF3EvInxzQol/sYBzvsSqQSnarDpNlliRvl1SRt1G+gKzvXXPRqKN36CMdbr9dbJRhfIJmCJVRfl95OClArIO8CgYEA369fPEW53VW5Gm3u4y8HVED7UDjgHu8P4i+dnmVK9hXylsKEXHwLVaioBqw5z7MLRgQI3rRqMGhOgk+iwcNIRymPiqKzXuq0rmRrT6rZvjg5jJss7Lh9k3ktuZ38ogrFnL//yyC6voNVjYTEx3YsYrj0DLMp8LDPVHrw9at+qR8CgYBvGVvHcNLRq1EMFyUgYSs2B83s8YLgTrFEnb7mKE/7b5t6KsEPn757Z2wRElzvYVrQz+/Nj8JpPt/C4dS9q2mLFbXWVuhnpmZbMdEEHXjJL2tlP0vvNvDjSUiNAurWitz/pTNT9N0m5aVl5Kupjg6+WgFGBYunCY8PC3UZj03mIQKBgESe3z91QHynFJ8IBJYLUltFiBNnL1IuEphX9Smnd2Sg/QfE6qgYob2IfOt3IFEYYyf6iuIPRNhO127gkVSR3PV/yXpFSXOf2wf45HbPOfdB9l2tKQ4B1vxL23wq/FqVpWPd/tHI26EgVzmP9nIeTaWHic7vk7kz9Ja9FHi5QKUPAoGAUevAgbXO9dwmy8sQmXOOCTosQ/Up4bPkm1Dj1Gx8ythJdXprI+SzpxXQvlknDaDZNRpSkT3u1MEvVFkrUnj0Qakdt8MBX7M6q6Jx4D0FmI/yoghrU876iDsXD7zsQnQ3RM4OfZjsiSYf/rNVI7iWaXg5Z0tr1lkLEeZZRGmENdg=
    -----END RSA PRIVATE KEY-----"""
    # 实例化支付应用
    alipay = AliPay(
        appid="2016101000652526",
        app_notify_url=None,
        app_private_key_string=app_private_key,
        alipay_public_key_string=alipay_public_key,
        sign_type="RSA2"  # 加密类型
    )

    #发起支付请求 选择网页版
    order_string = alipay.api_alipay_trade_page_pay(
        # 访问地址
        # https://openapi.alipaydev.com/gateway.do?app_id=2016101000652526&biz_content=%7B%22subject%22%3A%22python%5Cu5165%5Cu95e8%5Cu6559%5Cu7a0b%22%2C%22out_trade_no%22%3A%2210033%22%2C%22total_amount%22%3A%221%22%2C%22product_code%22%3A%22FAST_INSTANT_TRADE_PAY%22%7D&charset=utf-8&method=alipay.trade.page.pay&sign_type=RSA2&timestamp=2019-07-26+19%3A00%3A22&version=1.0&sign=IMoVv1a1NMkgzU1jhV5M5P8GvOeWcWDZWgVS7jdOCd2SuAWYKtVNtWitWI6lxP736FXkLcAj%2F5bjwWdJE0xFOgxTmTvgl21v%2FPn9HIaplIxcnbx62aHC6tM6W2oqDUYGmlY73ItVDEikaE8M%2BRRFB5C9wiQa3toy1nrAPGkgZ9WU00EVQEerNs4lWOiQswTJiuBO1hvDO3%2BUvxX5dwQyvYcjYikOnYJw1UeNel%2BLIUDQFJexIpmo3lBQ9Dsr0aVWqz3gq8pfHcY8dy9E91jHVqTcQoS0lht739gCgX6utb9Z5FkWJCXCaMG4R7fF50yLt2Ip11G1HWBeX6nzXB8yEQ%3D%3D

        out_trade_no = order_id,  # 订单号
        total_amount = str(money), # 支付金额
        subject = "饮食消费", # 交易主题
        return_url = "http://127.0.0.1:8000/Buyer/pay_result",  # 支付完成要跳转的本地路由
        notify_url = "http://127.0.0.1:8000/Buyer/pay_result"  # 支付完成要跳转的本地异步路由
    )
    # 跳转支付路由
    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?"+order_string)


# 接收支付结果
def pay_result(request):
    return render(request, "Buyer/pay_result.html", locals())

from django.http import JsonResponse
# 购物页面加减
def ajax_goods_num(request):
    result = {"total_num":"","total_money":""}
    # 获取当前页面上的商品数量
    current_num = int(request.GET.get("current_num"))
    goods_id = request.GET.get("goods_id")
    goods = Goods.objects.filter(id=int(goods_id)).first()
    goods_num = int(goods.goods_number)
    method = request.GET.get("method")
    if method == "add":    #  "+"按钮
        # 如果当前数量等于商品库存
        if current_num >= goods_num:
            result["total_num"] = goods_num
        else:
            result["total_num"] = current_num+1
    elif method == "minus":   #  "-"按钮
        if current_num <= 1:
            result["total_num"] = 1
        else:
            result["total_num"] = current_num - 1
    else:  # 输入框手动输入数量
        if current_num >= goods_num:
            result["total_num"] = goods_num
        elif current_num <= 1:
            result["total_num"] = 1
        else:
            result["total_num"] = current_num
    result["total_money"] = result["total_num"] * goods.goods_price
    return JsonResponse(result)












