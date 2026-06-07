from csv import writer
from typing import Dict
from aiohttp import ClientSession
import json
import os
from .zardan import root

from Ikea.zardan import log_error 
DEBUG = os.getenv("Debug","False")=="True"
if DEBUG:
    proxy ="http://127.0.0.1:10808"
else:
    proxy = None
IKEA_BODY = '{{"searchParameters":{{"input":{sku},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
cookie = {"__cf_bm":"7.cBQQE4uLG7c2878qGKbz0iOagY3yxv47aMjZ8aKWc-1779266745.1405406-1.0.1.1-bOyNkMlvspcGkaK77z2YvNP2u5iVCKK4PSwmuUma0QRJeOTJYJzuuXQ91mCyrGLnyRnbKA6EVKQSL9L9gvc.GfquOJ7N.oYKMIY4UyNVJKuo2_r_Gs2EH9AKKWR0lIRe"}
headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.6',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.ikea.com',
        'priority': 'u=1, i',
        'referer': 'https://www.ikea.com/',
        'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'session-id': '37b22e56-0c81-4897-88c0-a7297f554c31',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-client-id': 'ef382663-a2a5-40d4-8afe-f0634821c0ed',
        }
priceHeaders = {
        'content-type':  'application/json',
        }
priceSession:ClientSession|None = None
stockSession:ClientSession|None = None

async def init():
    global priceSession,stockSession
    priceSession = ClientSession('https://sik.search.blue.cdtapps.com',headers=headers,proxy=proxy)
    stockSession = ClientSession("https://api.salesitem.ingka.com",cookies=cookie,headers=headers,proxy=proxy)
async def getStock(sku:int):
    assert stockSession is not None
    path = "/availabilities/ru/om?itemNos={}&expand=StoresList".format(sku)
    res = await stockSession.get(path)
    data = await res.json()
    return data["availabilities"][0]['buyingOption']["cashCarry"]["availability"]["quantity"]
async def getPrice(sku:int):
    assert priceSession is not None
    if not sku:return None
    path = "/om/en/search"
    params = {
        'c': 'sr',
        'v': '20241114',
    }
    body = {
  "searchParameters": {
    "input": int(sku),
    "type": "QUERY"
  },
  "components": [
    {
      "component": "PRIMARY_AREA"
    }
  ]
}

    res = await priceSession.post(path, params=params, headers=priceHeaders, json=body)
    resText = await res.text()
    data =json.loads(resText)
    if len(data["results"])==0:
        return None,None
    return data["results"][0]["items"][0]["product"]["salesPrice"]["numeral"],data["results"][0]["items"][0]["product"]["tag"]
async def getProductDetail(item:Dict):
    try:
        sku =  item["SKU"]
        name = item["name"]
        id = item["post_id"]
        price,tag = await getPrice(sku)
        if not price:
            await log_error(sku,-1,name,id,tag)
            return None,None,None
        stock = await getStock(sku)
        return price,tag,stock
    except Exception as e:
        root.critical("Error in item detail"+str(item)+"Error:"+str(e))
        return None,None,None
