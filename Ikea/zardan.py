from datetime import datetime

import aiofiles
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
import resend

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


RESEND_API= os.getenv("RESEND_API")
assert RESEND_API is not None
resend.api_key = RESEND_API


url = "https://zardaan.com/wp-json/wc/v3/get_nav/"

auth = BasicAuth(KEY,password=SECRET_KEY)

offersPath = "offers.csv"
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
    await fPostId.truncate


    res =await client.post(
        'https://zardaan.com/wp-json/wc/v3/set_draft',
        json={"id":id},
        args={"id":id}
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

    response = await ClientSession().get(url, headers=headers,timeout=1000)

    currencies = await response.json()

async def init():
    global ferr,writer,client,fout,fPostId,postId
    fout = await aiofiles.open(offersPath,"a+", encoding="utf-8-sig")
    client = ClientSession("https://zardaan.com",cookies=coockie,headers=headers)
    ferr = await aiofiles.open('zarrdanProuct.txt',"w", encoding="utf-8-sig")
    fPostId = await aiofiles.open("post.id","w+")
    await fPostId.seek(0)
    postId = await fPostId.read()
    if len(postId)==0:
        postId="1000000"


    writer = AsyncWriter(fout,quoting=QUOTE_NONNUMERIC)
    await writer.writerow(["name","tag","sku","stock"])
    await getmnscwPrices()
    
async def getItems():
    global postId
    while (retry:=0)<5:
        try:
            response =await client.get(url,params={'id':postId})
            async for item in ijson.items_async(response.content,"response.item"):
                yield item
             #send email here and remove offersPath buffer
            await fPostId.seek(0)
            await fPostId.write("100000")
            await fPostId.truncate()
            await fout.flush()
            with open(offersPath,"rb") as f:
                body = f.read()
                params: resend.Emails.SendParams = {
                    "from": "ZardaanBot@namakiplus.ir",
                    "to": ["aam.mirzaei@gmail.com"],
                    "subject": "Update pricing Info",
                    "html": "<strong>it works!</strong>",
                    "attachments":[resend.Attachment(content=list(body),filename="zardaan-"+datetime.now().strftime("%m-%d,%H:%M:%S")+".csv")]
                }
                email = resend.Emails.send(params)
                root.info(email)
            break
        except Exception as e:
            root.critical("Failed getting items")
            retry+=1
rows =0 
async def updateItem(base_item:dict,price:str,stock:str,tag:str):
    global rows
    assert writer is not None
    assert ferr is not None
    url = "https://zardaan.com/wp-json/wc/v3/price/"
    curId = base_item["currency_id"]
    payload = {
        "id": base_item["post_id"],
        "price": round(price)*currencies[curId]["rate"]*100,
        "base":round(price) * 10,
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
            await writer.writerow([base_item["SKU"],stock,base_item["name"],"success",tag])
            await fPostId.seek(0)
            await fPostId.write(base_item['post_id'])
            await fPostId.truncate()
            rows+=1
            if rows%100==0:
                await fout.flush()
            break
        except Exception as e:
            print(e)
            retry+=1
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

async def dispose():
    if fout and fPostId and ferr and client:
        await fout.flush()
        await fPostId.flush()
        await ferr.flush()
        await client.close()