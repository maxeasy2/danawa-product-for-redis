from urllib.request import urlopen
from urllib.request import Request
from urllib import parse
from bs4 import BeautifulSoup
import ssl
import sys
import redis
import os

args = sys.argv

if len(args) <= 1 :
    print('pcode is null')
    exit(1);

pcode = args[1]

ssl._create_default_https_context = ssl._create_unverified_context


def get_danawa_product_info(pcode):
    url = 'https://prod.danawa.com/info/?pcode=' + pcode
    headers = {'Content-Type': 'text/plain', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
    req = Request(url, None, headers)
    html = urlopen(req)

    bs = BeautifulSoup(html, "html.parser") 
    try:
        prd_nm = bs.find(class_="top_summary").find(class_="prod_tit").find(class_="title").string
        lowest_price = bs.find(class_="lowest_price").find(class_="prc_c").string + ' 원'
        
        obj = {}
        obj['prd_nm'] = prd_nm
        obj['lowest_price'] = lowest_price
        obj['url'] = url

        return obj
    except Exception as e:
        print(f"{pcode} error: {e}")
        return None


prd_obj = get_danawa_product_info(pcode)

if prd_obj is None:
    print('Product is without information')
    exit(2)

prd_nm = prd_obj['prd_nm']
lowest_price = prd_obj['lowest_price']
url = prd_obj['url']


redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT')
webhook_url = os.environ.get('WEBHOOK_URL')
chat_name = os.environ.get('CHAT_NAME') or 'none'
chat_id = os.environ.get('CHAT_ID') or '0'

r = redis.Redis(host=redis_host, port=redis_port, db=0)

low_price_list_key = 'low_price_list_' + chat_name + '_' + chat_id + '_' + pcode

length = r.llen(low_price_list_key)

if length == 0:
    r.lpush(low_price_list_key, lowest_price)
    reqUrl = webhook_url + parse.quote('상품명 : ' + prd_nm + '\n최저가 : ' + lowest_price + '\nURL : ' + url)
    urlopen(reqUrl)
else:
    recent_low_price = r.lindex(low_price_list_key, 0)
    if recent_low_price.decode() != lowest_price:
        r.lpush(low_price_list_key, lowest_price)
        length = r.llen(low_price_list_key)
        if length > 3:
            r.rpop(low_price_list_key)

        low_price_list = r.lrange(low_price_list_key, 0, 2)
        low_price_list.reverse()
        
        result_low_price_str = b' > '.join(low_price_list).decode()
        
        reqUrl = webhook_url + parse.quote('상품명 : ' + prd_nm + '\n최저가 : ' + result_low_price_str + '\nURL : ' + url)
        urlopen(reqUrl)






