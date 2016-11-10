# coding=utf-8
import requests
import demjson
import MySQLdb
import time, datetime

# 模拟浏览器header
BROWSER_HEADER = {"Cookie" : "shopCategory=food; device_uuid=YmRjYTkxOWItYzU4Ni00MmMwLTg0NGUtYmIxYjliMDUwYmYy; JSESSIONID=18gvdqg3aab410up0omyvjmag; wpush_server_url=wss://wpush.meituan.com"}
# 登录用户信息
LOGIN_ACCOUNT = [
  {"userName": "tangjiang", "password": "tangjiang123", "imgVerifyValue": "", "service": ""}
]
# 请求基地址
BASE_URL = "http://e.waimai.meituan.com/v2/"
# 登录地址，post请求
LOGIN_URL = BASE_URL + "logon/pass/step1/logon"
# 获取已完成的订单，get请求
FETCH_ORDER_URL = BASE_URL + "order/history/r/query"
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
def fetch_valid_order(sdate, edate, page):
  qparams = "getNewVo=1&wmOrderPayType=-2&wmOrderStatus=%s&sortField=1&startDate=%s&endDate=%s&pageNum=%s"
  qR = get(FETCH_ORDER_URL + "?%s"%(qparams%(8, sdate, edate, page))) 
  updateDb(qR["wmOrderList"])
  return qR["pageCount"]
def fetch_invalid_order(sdate, edate, page):
  qparams = "getNewVo=1&wmOrderPayType=-2&wmOrderStatus=%s&sortField=1&startDate=%s&endDate=%s&pageNum=%s"
  qR = get(FETCH_ORDER_URL + "?%s"%(qparams%(9, sdate, edate, page)))
  updateDb(qR["wmOrderList"])
  return qR["pageCount"]
def updateDb(data):
  for i in data:
    sql = "update meituanorder set num='%s' where wm_order_id_view='%s'"%(i["num"],i["wm_order_id_view_str"])
    cursor.execute(sql)
def fetch(sdate, edate, user):
  # 1.登录
  lR = post(LOGIN_URL, user)
  # 2.登录成功后获取订单
  if lR["code"] == 0:
    # 3.获取完成的订单
    count = fetch_valid_order(sdate, edate, 1)
    for i in range(2, count + 1):
      fetch_valid_order(sdate, edate, i)
    # 4.获取无效的订单
    count = fetch_invalid_order(sdate, edate, 1)
    for i in range(2, count + 1):
      fetch_invalid_order(sdate, edate, i)
# 启动抓取程序
day = datetime.date(2016, 10, 8)
today = datetime.date.today()
days = (today - day).days
for ds in range(days / 7):
  sdate = day + datetime.timedelta(days = 7 * ds)
  edate = sdate + datetime.timedelta(days = 6)
  for user in LOGIN_ACCOUNT:
    fetch(sdate, edate, user)
sdate = day + datetime.timedelta(days = 7 * (days / 7))
edate = today
for user in LOGIN_ACCOUNT:
  fetch(sdate, edate, user)
cursor.execute("update fetchtime set next_time='%s' where target='meituan'"%(today))
cursor.close()
db.commit()
db.close()
