# coding=utf-8
import requests
import demjson
import MySQLdb
from urllib import quote
import time, datetime

# 模拟浏览器header
BROWSER_HEADER = {"Cookie" : "shopCategory=food; device_uuid=YmRjYTkxOWItYzU4Ni00MmMwLTg0NGUtYmIxYjliMDUwYmYy; JSESSIONID=18gvdqg3aab410up0omyvjmag; wpush_server_url=wss://wpush.meituan.com"}
# 登录用户信息
LOGIN_ACCOUNT = {"userName": "tangjiang", "password": "tangjiang123", "imgVerifyValue": "", "service": ""}
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
def insertDb(data, shippers, distances, backinfo = None):
  for i in data:
    cursor.execute("select count(*) from meituanorder where wm_order_id_view='%s'"%(i["wm_order_id_view_str"]))
    count = cursor.fetchone()
    if count[0] > 0:
      continue
    #uR = get(FETCH_RECIPIENT_URL + "?wmPoiId=%s&wmOrderId=%s"%(i["wm_poi_id"], i["id"]))
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
      i["poi_name"],i["recipient_address"],'',name,gender,i["shipping_fee"],i["total_after"],
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
def fetch():
  # 1.登录
  lR = post(LOGIN_URL, LOGIN_ACCOUNT)
  # 2.登录成功后获取用户信息
  if lR["code"] == 0:
    # 3.获取用户手机号
    cursor.execute("select * from meituanorder where recipient_phone=''")
    for i in cursor.fetchall():
      uR = get(FETCH_RECIPIENT_URL + "?wmPoiId=%s&wmOrderId=%s"%(i[3], i[1]))
      cursor.execute("update meituanorder set recipient_phone='%s' where id=%s"%(uR["data"]["recipientPhone"], i[0]))
      db.commit()
      time.sleep(10)
    cursor.close()
    db.close()
# 启动抓取程序
fetch()
