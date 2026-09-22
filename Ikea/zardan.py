from datetime import datetime

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper 
from aiohttp import BasicAuth, ClientSession
import json
import os 
from aiocsv import AsyncWriter
from csv import QUOTE_NONNUMERIC
import queue
from logging.handlers import QueueHandler,QueueListener,RotatingFileHandler
import logging
import resend
import sys

log_queue     = queue.Queue()
queue_handler = QueueHandler(log_queue)  
root = logging.getLogger()
root.addHandler(queue_handler)

rot_handler     = None

offersPath = "offers.csv"
if sys.platform.startswith("win"):
   rot_handler =  rotHandler = RotatingFileHandler("./zardan.logger",mode="w")   # The blocking handler.
elif sys.platform.startswith("linux"):
   rot_handler = RotatingFileHandler("/app/zardan.logger",mode="w")   # The blocking handler.
   offersPath = "/app/offers.csv"

queue_listener = QueueListener(log_queue, 
                               rot_handler)
queue_listener.start()
coockie = {"pxcelPage_c01002":"1"}
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
        }
KEY,SECRET_KEY = os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")
assert KEY is not None
assert SECRET_KEY is not None
from pathlib import Path

RESEND_API= os.getenv("RESEND_API")
assert RESEND_API is not None
resend.api_key = RESEND_API


auth = BasicAuth(KEY,password=SECRET_KEY)

client:ClientSession|None = None
fout:AsyncTextIOWrapper|None = None 
ferr:AsyncTextIOWrapper|None = None
fPostId:AsyncTextIOWrapper|None = None
writer:AsyncWriter|None = None
postId = '100000000'

async def log_error(sku,stock,name,id,reason,tag=""):
    assert writer is not None
    await writer.writerow([sku,stock,name,reason,tag])
    await fPostId.seek(0)
    await fPostId.write(id)
    await fPostId.truncate()
    res =await client.post(
        'https://cors.io/?url=https://zardaan.com/wp-json/wc/v3/set_draft',
        json={"id":id},
        )
    root.warning(await res.text())
currencies = {"10347":{"name":"کالای کوچک","rate":150000},"23110":{"name":"کالای درشت","rate":160000},"43946":{"name":"خرید قدیم","rate":150000},"43947":{"name":"سفارش کالای کوچک","rate":150000},"43948":{"name":"سفارش کالای درشت","rate":160000},"44085":{"name":"قیمت درهم دبی","rate":40165},"44915":{"name":"دلار آمریکا","rate":145000},"51450":{"name":"لیر ترکیه","rate":12760},"51451":{"name":"کالای غیر ایکیا","rate":1},"52114":{"name":"کالای خیلی درشت","rate":165000},"54062":{"name":"کالای کوچک رقابتی","rate":150000},"54063":{"name":"کالای درشت رقابتی","rate":160000},"61923":{"name":"مسافری دبی","rate":150000}}

async def init():
    global ferr,writer,client,fout,fPostId,postId
    fout = await aiofiles.open(offersPath,"a+", encoding="utf-8-sig")
    client = ClientSession('https://cors.io/?url=https://zardaan.com',cookies=coockie,headers=headers)
    ferr = await aiofiles.open('zarrdanProuct.txt',"w", encoding="utf-8-sig")
    try:
        if sys.platform.startswith("linux"):
            post_id_path = "/app/post.id"
        else:
            post_id_path = Path(__file__).parent.parent / "post.id"
        fPostId = await aiofiles.open(post_id_path,"r+")
    except Exception as e:
        root.critical(e)
        print(e)
        raise e
    await fPostId.seek(0)
    postId = await fPostId.read()
    if len(postId)==0:
        postId="1000000"


    writer = AsyncWriter(fout,quoting=QUOTE_NONNUMERIC)
    await writer.writerow(["sku","name","rial","toman","stock","status"])
    
async def getItems():
    global postId
    while (retry:=0)<5:
        try:
            corsres = await client.get('https://cors.io/?url=https://zardaan.com/wp-json/wc/v3/get_nav/',params={'id':postId})
            response = await corsres.json()
            for item in json.loads(response['body'])['response']:
                yield item
             #send email here and remove offersPath buffer
            await fout.flush()
            with open(offersPath,"rb") as f:
                body = f.read()
                params: resend.Emails.SendParams = {
                    "from": "ZardaanBot@namakiplus.ir",
                    "to": ["aam.mirzaei@gmail.com",'Mobelikea@gmail.com'],
                    "subject": "با موفقیت بروز شد",
                    "html": "<strong>قیمت ها در فایل پیوست مشاهده شود</strong>",
                    "attachments":[resend.Attachment(content=list(body),filename="zardaan-"+datetime.now().strftime("%m-%d,%H:%M:%S")+".csv")]
                }
                email = resend.Emails.send(params)
                root.info(email)
                open(offersPath, "w").close()#truncate it for the new file
            break
        except Exception as e:
            root.critical("Failed getting items")
            retry+=1
async def updateItem(base_item:dict,price:str,stock:str,tag:str):
    assert writer is not None
    assert ferr is not None
    url = "https://cors.io/?url=https://zardaan.com/wp-json/wc/v3/price/"
    curId = base_item["currency_id"]
    tomanPrice = round(price)*currencies[curId]["rate"]*100
    basePrice = round(price) * 10
    payload = {
        "id": base_item["post_id"],
        "price": tomanPrice,
        "base": basePrice,
        "stock":stock,
    }
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic Y2tfNmM4MzBmNTQ0NGRlOTBkZGQxNmYwNzZjZjAwZTEwZTMzY2MzODYxMjpjc19lMzUzNzExYzFlNmZiNzUzOTA0OTY4NjRkZTFjNDBiOTQ5MjQ5YmZj',
    'Cookie': 'pxcelPage_c01002=1'
    }
    while (retry:=0)<5:
        try:
            response =await client.post(url, headers=headers,json=payload,timeout=1000*2**retry)
            rsText = await response.text()
            root.info(rsText)
            await writer.writerow([base_item["SKU"],base_item["name"],basePrice,tomanPrice,stock,"success"])
            await fPostId.seek(0)
            await fPostId.write(base_item['post_id'])
            await fPostId.truncate()
            break
        except Exception as e:
            print(e)
            retry+=1
async def dispose():
    if fout and fPostId and ferr and client:
        await fout.flush()
        await fPostId.flush()
        await ferr.flush()
        await client.close()
        await fout.close()
        await ferr.close()
        await fPostId.close()
