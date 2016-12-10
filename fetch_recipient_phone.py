# coding=utf-8
import requests
import demjson
import MySQLdb
from urllib import quote
import time, datetime

# 模拟浏览器header
BROWSER_HEADER = {"Cookie" : "shopCategory=food; device_uuid=YmRjYTkxOWItYzU4Ni00MmMwLTg0NGUtYmIxYjliMDUwYmYy; JSESSIONID=18gvdqg3aab410up0omyvjmag; wpush_server_url=wss://wpush.meituan.com"}
# 登录用户信息
LOGIN_ACCOUNT = {"userName": "", "password": "", "imgVerifyValue": "", "service": ""}
# 请求基地址
BASE_URL = "http://e.waimai.meituan.com/v2/"
# 登录地址，post请求
LOGIN_URL = BASE_URL + "logon/pass/step1/logon"
# 获取收货人完整手机号，get请求
FETCH_RECIPIENT_URL = BASE_URL + "order/receive/processed/r/recipientPhone"
# 初始化session，数据库连接
session = requests.session()
db = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "ordersync", charset = "utf8")
cursor = db.cursor()
cursor.execute("SET NAMES utf8mb4")

def get(url):
  res = session.get(url)
  return demjson.decode(res.text)
def post(url, forms):
  res = session.post(url, headers = BROWSER_HEADER, data = forms)
  return demjson.decode(res.text)
def fetch():
  # 1.登录
  lR = post(LOGIN_URL, LOGIN_ACCOUNT)
  # 2.登录成功后获取用户信息
  if lR["code"] == 0:
    # 3.获取用户手机号
    cursor.execute("select * from meituanorder where recipient_phone=''")
    for i in cursor.fetchall():
      try:
        uR = get(FETCH_RECIPIENT_URL + "?wmPoiId=%s&wmOrderId=%s"%(i[3], i[1]))
        cursor.execute("update meituanorder set recipient_phone='%s' where id=%s"%(uR["data"]["recipientPhone"], i[0]))
        db.commit()
        print uR["data"]["recipientPhone"]
      except:
        fetch()
      time.sleep(1)
    cursor.close()
    db.close()
# 启动抓取程序
fetch()
