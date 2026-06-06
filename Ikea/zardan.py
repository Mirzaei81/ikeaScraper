from posix import write
import aiofiles
from aiofiles.base import AiofilesContextManager
from aiofiles.threadpool.text import AsyncTextIOWrapper 
from aiohttp import BasicAuth, ClientSession
import aioftp
import ijson
import os 
from aiocsv import AsyncWriter
from csv import QUOTE_NONNUMERIC
import queue
from logging.handlers import QueueHandler,QueueListener,RotatingFileHandler
import logging
import json
log_queue     = queue.Queue()
queue_handler = QueueHandler(log_queue)  
root = logging.getLogger()
root.addHandler(queue_handler)
rot_handler    = RotatingFileHandler("zardan.logger",mode="w")   # The blocking handler.
queue_listener = QueueListener(log_queue, 
                               rot_handler)
queue_listener.start()
SECRET = os.getenv("SECRET")
assert SECRET is not None
coockie = {"pxcelPage_c01002":"1"}
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
        }
KEY,SECRET_KEY = os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")
assert KEY is not None
assert SECRET_KEY is not None
url = "https://zardaan.com/wp-json/wc/v3/get_nav/"

auth = BasicAuth(KEY,password=SECRET_KEY)


put_json_data = {
        "backorders": "no",
        "backorders_allowed": False,
        "stock_quantity":0,
        "stock_status":"outofstock"
        }
offersPath = "offers.csv"
client:ClientSession|None = None
fout:AsyncTextIOWrapper|None = None 
ferr:AsyncTextIOWrapper|None = None
writer:AsyncWriter|None = None
async def log_error(sku,stock,name,id,reason,tag=""):
    assert writer is not None
    await writer.writerow([sku,stock,name,reason,tag])


    res =await client.put(
        f'https://zardaan.com/wp-json/wc/v3/products/{id}',
        json=put_json_data,
        )
    root.warning(await res.text())
currencies = {}
async def getmnscwPrices():
    global currencies
    url = "https://zardaan.com/wp-json/mnswmc/v1/currency/9f8e7adfcdb7c395d33d08fcd968ade8"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'cookie': 'pxcelPage_c01002=1; wp-settings-2=libraryContent%3Dbrowse%26editor%3Dtinymce%26posts_list_mode%3Dlist%26advImgDetails%3Dhide; wp-settings-time-2=1779256642; d_user_session=3d6c016bd7bef3249359408a469a2850aa5fffc5e88a388b67d8fc68c0898972522466f4c5d446e6b92ba6b918b5cda9c5946eabbb392b3181f5ffb6983d4dc5',
    }

    response = await ClientSession().get(url, headers=headers)

    currencies = await response.json()

async def init():
    global ferr,writer,client
    f = await aiofiles.open(offersPath,"w", encoding="utf-8-sig")
    client = ClientSession("https://zardaan.com",cookies=coockie,headers=headers)
    ferr = await aiofiles.open('zarrdanProuct.txt',"w", encoding="utf-8-sig")
    writer = AsyncWriter(f,quoting=QUOTE_NONNUMERIC)
    await writer.writerow(["name","tag","sku","stock"])
    await getmnscwPrices()
    
async def getItems():
    item =None
    try:
        response =await  client.get(url)
        async for item in ijson.items_async(response.content,"response.item"):
            yield item
    except Exception as e:
        root.critical("Failed at parsing items",item,"error",e)
async def updateItem(base_item:dict,price:str,stock:str,tag:str):
    assert writer is not None
    assert ferr is not None
    url = "https://zardaan.com/wp-json/wc/v3/price4/"
    curId = base_item["currency_id"]
    payload = {
        "id": base_item["post_id"],
        "price": round(price)*currencies[curId]["rate"]*10,
        "base":round(price),
        "stock":stock,
    }
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic Y2tfNmM4MzBmNTQ0NGRlOTBkZGQxNmYwNzZjZjAwZTEwZTMzY2MzODYxMjpjc19lMzUzNzExYzFlNmZiNzUzOTA0OTY4NjRkZTFjNDBiOTQ5MjQ5YmZj',
    'Cookie': 'pxcelPage_c01002=1'
    }

    response =await client.post(url, headers=headers,json=payload)
    rsText = await response.text()
    root.info(rsText)
async def uploadResults():
    username=  os.getenv('FTP_USER')
    assert username is not None
    password =  os.getenv('FTP_PASS')
    assert password is not None
    assert fout is not None
    await fout.flush()
    await fout.close()
    async with aioftp.Client.context('ftp.zardaan.com',21,username,password) as ftp:
        try:
            filename = 'offers.csv'
            await ftp.upload(filename, offersPath)
            root.info("write file succesfuly")
        except aioftp.errors as e:
            root.error('FTP error:', e)

async def close():
    await client.close()
