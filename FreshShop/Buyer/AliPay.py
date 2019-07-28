# -*-coding: utf-8-*-
# @Time    : 2019/07/26 15:35
# @Author  : ZP
# @Project : FreshShop
# @FileName: AliPay.py
# @Software: PyCharm

from alipay import AliPay

alipay_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzKUekbExTdgaNbmFSDObIsTOh4CC9mE+W/UOUgu7g4fsrFxc7apBvGDfHy3Y5Zk40brrGlacc4bAYbHcSMjgPTwZCyiYo+q1uA3hSaVRpxD/TW+Qvw4sf17QS55WljvWepQS6Kncsxcy8lyOmTyhw5ArLsRsjh6H9dM7E26moFixiYXocT2JcA/TwyZCCh2U7igPFJ8rruFriXcjpXz28jjK0uLKJ3El/7iKzYIlXl22C51X/sjNAhd9FZid0RJjYedXH+Nn3yH/gPv8qLKquMVxPMab3XNI6nWVLfAib+iHyy3Ty/sYbc4eXq5LQ4RuKCdz7L1tOAS4HRshCJjD8QIDAQAB
-----END PUBLIC KEY-----"""

alipay_private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAzKUekbExTdgaNbmFSDObIsTOh4CC9mE+W/UOUgu7g4fsrFxc7apBvGDfHy3Y5Zk40brrGlacc4bAYbHcSMjgPTwZCyiYo+q1uA3hSaVRpxD/TW+Qvw4sf17QS55WljvWepQS6Kncsxcy8lyOmTyhw5ArLsRsjh6H9dM7E26moFixiYXocT2JcA/TwyZCCh2U7igPFJ8rruFriXcjpXz28jjK0uLKJ3El/7iKzYIlXl22C51X/sjNAhd9FZid0RJjYedXH+Nn3yH/gPv8qLKquMVxPMab3XNI6nWVLfAib+iHyy3Ty/sYbc4eXq5LQ4RuKCdz7L1tOAS4HRshCJjD8QIDAQABAoIBAAal4o1XFUPzHj7ajQLgcky52f+65AY++HiiSFnP+cJ3GvAqe/ZYjpQhDX6EzcP/q0Hc8aBEagayvPMvhPl0VRyIJEQhiHvitw6InOX4keN8gN6yHiCmxDlLCjc6qJNu1DPdNZQLWJkUytnmudcuig7BUzXMub4QLdiFiSjDcnRI/nNxK9ngUvnnbgXtoBpjvzXzXJ4GvEWUZFzUTOvQ9xFxmHBgxXoBxY75TRDAa7X0q6LP64UJnLOGG+cRySdc7WZNbJmgpgop8V2t/qyDFGsGIZEJOQJlZ5tKeOzrRb/PBI4mwaNJ6AQA5Ei+BMG7+nudn8G5bny/R0RQlV5HMSUCgYEA6jWVBYF3ySyv9DWiYldROGp9mgRYr6Rxd+OR4ovXtr2nA5vTrxvqnaCrvynhtfCJcDZJwyAl40m5qEOnMWjN/JF3EvInxzQol/sYBzvsSqQSnarDpNlliRvl1SRt1G+gKzvXXPRqKN36CMdbr9dbJRhfIJmCJVRfl95OClArIO8CgYEA369fPEW53VW5Gm3u4y8HVED7UDjgHu8P4i+dnmVK9hXylsKEXHwLVaioBqw5z7MLRgQI3rRqMGhOgk+iwcNIRymPiqKzXuq0rmRrT6rZvjg5jJss7Lh9k3ktuZ38ogrFnL//yyC6voNVjYTEx3YsYrj0DLMp8LDPVHrw9at+qR8CgYBvGVvHcNLRq1EMFyUgYSs2B83s8YLgTrFEnb7mKE/7b5t6KsEPn757Z2wRElzvYVrQz+/Nj8JpPt/C4dS9q2mLFbXWVuhnpmZbMdEEHXjJL2tlP0vvNvDjSUiNAurWitz/pTNT9N0m5aVl5Kupjg6+WgFGBYunCY8PC3UZj03mIQKBgESe3z91QHynFJ8IBJYLUltFiBNnL1IuEphX9Smnd2Sg/QfE6qgYob2IfOt3IFEYYyf6iuIPRNhO127gkVSR3PV/yXpFSXOf2wf45HbPOfdB9l2tKQ4B1vxL23wq/FqVpWPd/tHI26EgVzmP9nIeTaWHic7vk7kz9Ja9FHi5QKUPAoGAUevAgbXO9dwmy8sQmXOOCTosQ/Up4bPkm1Dj1Gx8ythJdXprI+SzpxXQvlknDaDZNRpSkT3u1MEvVFkrUnj0Qakdt8MBX7M6q6Jx4D0FmI/yoghrU876iDsXD7zsQnQ3RM4OfZjsiSYf/rNVI7iWaXg5Z0tr1lkLEeZZRGmENdg=
-----END RSA PRIVATE KEY-----"""

# 实例化支付应用
alipay = AliPay(
    appid = "2016101000652526",
    app_notify_url = None,
    app_private_key_string = alipay_private_key,
    alipay_public_key_string = alipay_public_key,
    sign_type = "RSA2"
)

# 发起支付请求
order_string = alipay.api_alipay_trade_page_pay(
    out_trade_no = "10033", # 订单号
    total_amount = str(1), # 支付金额
    subject = "python入门教程", #  交易主体
    return_url = None,
    notify_url = None
)

print("https://openapi.alipaydev.com/gateway.do?"+order_string)








