# coding=utf-8
import requests
import demjson
import MySQLdb
from urllib import quote
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
# 获取送餐员信息，get请求
FETCH_SHIPPER_URL = BASE_URL + "order/receive/processed/r/distribute/list"
# 获取收货人完整手机号，get请求
FETCH_RECIPIENT_URL = BASE_URL + "order/receive/processed/r/recipientPhone"
# 获取收货人距店铺的距离
FETCH_DISTANCE_URL = BASE_URL + "order/receive/processed/r/distribute/pathDistance"
# 获取退款信息，get请求
FETCH_BACK_URL = BASE_URL + "order/refund/list"
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
def c2t(c):
  t = time.localtime(c)
  return time.strftime("%Y-%m-%d %H:%M:%S", t)
def split_recipient_name(name):
  if name == None or name == "":
    return ("", "")
  elif name.find("(") == -1 or name.find(")") == -1:
    return (name, "")
  else:
    ng = name.split("(")
    return (ng[0], ng[1].split(")")[0])
def fetch_valid_order(sdate, edate, page):
  qparams = "getNewVo=1&wmOrderPayType=-2&wmOrderStatus=%s&sortField=1&startDate=%s&endDate=%s&pageNum=%s"
  qR = get(FETCH_ORDER_URL + "?%s"%(qparams%(8, sdate, edate, page))) 
  sparams = [{"wmOrderId": o["id"], "wmPoiId": o["wm_poi_id"], "logisticsStatus": o["logistics_status"], "logisticsCode": ("" if o["logistics_code"] == None or o["logistics_code"] == "" else int(o["logistics_code"]))} for o in qR["wmOrderList"]]
  sR = get(FETCH_SHIPPER_URL + "?orderInfos=%s"%(quote(demjson.encode(sparams))))
  dparams = [{"wmOrderId": o["id"], "wmPoiId": o["wm_poi_id"], "from_lat": o["poi_latitude"], "from_lng": o["poi_longitude"], "to_lat": o["address_latitude"], "to_lng": o["address_longitude"]} for o in qR["wmOrderList"]]
  dR = get(FETCH_DISTANCE_URL + "?orderLatAndLngS=%s"%(quote(demjson.encode(dparams))))
  insertDb(qR["wmOrderList"], sR["data"], dR["data"])
  return qR["pageCount"]
def fetch_invalid_order(sdate, edate, page):
  qparams = "getNewVo=1&wmOrderPayType=-2&wmOrderStatus=%s&sortField=1&startDate=%s&endDate=%s&pageNum=%s"
  qR = get(FETCH_ORDER_URL + "?%s"%(qparams%(9, sdate, edate, page)))
  sparams = [{"wmOrderId": o["id"], "wmPoiId": o["wm_poi_id"], "logisticsStatus": o["logistics_status"], "logisticsCode": ("" if o["logistics_code"] == None or o["logistics_code"] == "" else int(o["logistics_code"]))} for o in qR["wmOrderList"]]
  sR = get(FETCH_SHIPPER_URL + "?orderInfos=%s"%(quote(demjson.encode(sparams))))
  dparams = [{"wmOrderId": o["id"], "wmPoiId": o["wm_poi_id"], "from_lat": o["poi_latitude"], "from_lng": o["poi_longitude"], "to_lat": o["address_latitude"], "to_lng": o["address_longitude"]} for o in qR["wmOrderList"]]
  dR = get(FETCH_DISTANCE_URL + "?orderLatAndLngS=%s"%(quote(demjson.encode(dparams))))
  bparams = [{"wmOrderId": o["id"], "wmPoiId": o["wm_poi_id"]} for o in qR["wmOrderList"]]
  bR = get(FETCH_BACK_URL + "?orderInfos=%s"%(quote(demjson.encode(bparams))))
  insertDb(qR["wmOrderList"], sR["data"], dR["data"], bR["data"])
  return qR["pageCount"]
def insertDb(data, shippers, distances, backinfo = None):
  for i in data:
    cursor.execute("select count(*) from meituanorder where wm_order_id_view='%s'"%(i["wm_order_id_view_str"]))
    count = cursor.fetchone()
    if count[0] > 0:
      continue
    uR = get(FETCH_RECIPIENT_URL + "?wmPoiId=%s&wmOrderId=%s"%(i["wm_poi_id"], i["id"]))
    name, gender = split_recipient_name(i["recipient_name"])
    distance = [d["distance"] for d in distances if d["wm_order_id_view"] == i["wm_order_id_view_str"]][0]
    sql = """insert into meituanorder(order_id,wm_order_id_view,app_poi_code,wm_poi_name,wm_poi_address,wm_poi_phone,
      recipient_address,recipient_phone,recipient_name,recipient_gender,shipping_fee,total,original_price,caution,
      shipper_phone,status,city_id,has_invoiced,invoice_title,ctime,utime,delivery_time,is_third_shipping,latitude,
      longitude,order_send_time,order_receive_time,order_confirm_time,order_cancel_time,order_completed_time,logistics_status,
      logistics_id,logistics_name,logistics_send_time,logistics_confirm_time,logistics_cancel_time,logistics_fetch_time,
      logistics_completed_time,logistics_dispatcher_name,logistics_dispatcher_mobile,distance,num)values(%s,'%s',%s,'%s',NULL,
      NULL,'%s','%s','%s','%s',%s,%s,%s,'%s','%s',%s,%s,%s,'%s','%s',NULL,NULL,%s,'%s','%s','%s',NULL,NULL,NULL,'%s',%s,
      %s,'%s',NULL,NULL,NULL,NULL,'%s','%s','%s',%s,'%s')"""%(i["id"],i["wm_order_id_view_str"],i["wm_poi_id"],
      i["poi_name"],i["recipient_address"],uR["data"],name,gender,i["shipping_fee"],i["total_after"],
      i["total_before"],i["remark"],shippers[str(i["id"])]["dispatcher_phone"],i["status"],i["poi_city_id"],
      i["has_been_invoiced"],i["invoice_title"],i["order_time_fmt"],shippers[str(i["id"])]["is_third_part_shipping"],
      i["address_latitude"],i["address_longitude"],i["order_time_fmt"],c2t(shippers[str(i["id"])]["latest_delivery_time"]),
      i["logistics_status"],shippers[str(i["id"])]["logistics_id"],shippers[str(i["id"])]["logistics_name"],
      c2t(shippers[str(i["id"])]["latest_delivery_time"]),shippers[str(i["id"])]["dispatcher_name"],
      shippers[str(i["id"])]["dispatcher_phone"],distance,i["num"])
    cursor.execute(sql)
    for c in i["cartDetailVos"][0]["details"]:
      csql = """insert into meituanorderdetail(order_id,app_food_code,food_name,quantity,price,box_num,box_price,unit,origin_price)
      values(%s,NULL,'%s',%s,%s,%s,%s,'%s',%s)"""%(i["id"],c["food_name"],c["count"],c["food_price"],c["box_num"],c["box_price"],c["unit"],c["origin_food_price"])
      cursor.execute(csql)
    for e in i["discounts"]:
      esql = "insert into meituanorderextras(order_id,fee,remark,category)values(%s,%s,'%s',%s)"%(i["id"],e["info"][2:],e["type"],e["category"])
      cursor.execute(esql)
  if backinfo != None:
    for k in backinfo:
      for v in backinfo[k]:
        cursor.execute("select count(*) from meituanorderbackinfo where id=%s"%(v["id"]))
        count = cursor.fetchone()
        if count[0] > 0:
          continue
        bsql = "insert into meituanorderbackinfo values(%s,%s,%s,%s,'%s','%s',%s,'%s','%s')"%(v["id"],
          v["wm_order_id"],v["wm_poi_id"],v["apply_type"],v["apply_time_fmt"],v["apply_reason"],v["res_type"],v["res_time_fmt"],v["res_reason"])
        cursor.execute(bsql)
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
cursor.execute("select * from fetchtime where target='meituan'")
day = cursor.fetchone()[1]
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
