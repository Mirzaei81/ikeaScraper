"""
This is an Ikea Web scraper Module.
A scraper designed to automatically open a URL, navigate to a specific web page, 
extract multiple data types from different variables, and store the data in an 
organised manner in an external storage service.
"""


from dotenv import load_dotenv
import requests
import os
import json
import ftplib
import csv 
import io 
import time
import requests
import re

output = io.StringIO()
writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["sku","hesabfaCode","stock","name","status","description","currentPrice","offerPrice","ikeaPrice","tag"])
load_dotenv()

pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":1,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
pageCount =  int(pageResponse.headers["X-WP-Total"])

if os.getenv("Debug","False")=="True":
    proxy ={
        "http":"http://127.0.0.1:10809",
        "https":"http://127.0.0.1:10809"
    }
else:
    proxy = None

hesanfa_url = "https://api.hesabfa.com/v1/item/getByBarcode"
url = "https://zardaan.com/wp-json/mnswmc/v1/currency/9f8e7adfcdb7c395d33d08fcd968ade8"

headers = {
  'Cookie': 'pxcelPage_c01002=1'
}

putHeaders = {
    'Content-Type': 'application/json',
}

put_json_data = {
    "backorders": "no",
    "backorders_allowed": False,
    "stock_quantity":0,
    "stock_status":"outofstock"
}
updateHeader = {
    'Content-Type': 'application/json',
    'Cookie': 'pxcelPage_c01002=1'
}
stockHeader = {
    'X-Client-ID': 'ef382663-a2a5-40d4-8afe-f0634821c0ed',
}
response = requests.get(url, headers=headers)

prices = response.json()

def updateProductSku(sku):

    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"sku":sku},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    p = response.json()[0]
    stock = p["stock_quantity"]
    ikeaStockData = {}
    ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=get_IKEA_Body(p["sku"]))
    apiKey = get_API_KEY()
    stockHeader["X-Client-ID"] = apiKey
    i=0
    while(i<5):
        try:
            ikeaStockResponse = requests.get('https://api.salesitem.ingka.com/availabilities/ru/ae', params={
                'itemNos': sku,
                'expand': 'StoresList,Restocks,SalesLocations,DisplayLocations,ChildItems',
            },proxies=proxy
            , headers=stockHeader)
            ikeaStockData = ikeaStockResponse.json()
            break
        except(e):
            time.sleep(1)
            i+=1
    else:
        return

    ikeaData  = ikeaResponse.json()

    
    hesabId =get_hesab_id(p["sku"])


    if("results"  not in ikeaData or len(ikeaData["results"])==0):
        log_error(p["sku"],hesabId,stock,p["name"],response.status_code,p["id"])
        return
    item = ikeaData["results"][0]["items"][0]["product"]
    tag = item["tag"] if "tag" in item  else ""
    if tag == "NONE":
        tag = "" 
    IKEA_NUMERIC = item["salesPrice"]["numeral"]
    isSellable =   item["onlineSellable"]
    if  not isSellable:
        log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Out of Stock : {isSellable}",-1,-1,-1,tag)
        return
    if not ikeaResponse.ok:
        log_error([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Disreturnd : {isSellable}",-1,-1,-1,tag])
        return

    if len(ikeaData["results"])==0:
        log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Disreturnd : {isSellable}",-1,-1,-1,tag)
        return
    offerPrice = round_up(IKEA_NUMERIC)
    if "previous" in item["salesPrice"]:
        number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
        itemPrice = float(number.replace(",","."))
    else:
        itemPrice = get_IU_PRICE(meta_data=p["meta_data"])

    if itemPrice==None:return 
    data = {
        "id": p["id"],
        "reqular_price":float(itemPrice) ,
        "sale_price": offerPrice if tag =="NEW_LOWER_PRICE" else 0 ,
    }
    if "availabilities" in ikeaStockData and len(ikeaStockData["availabilities"])>=2:
        if(ikeaStockData["availabilities"][1]["availableForCashCarry"]):
            if 'availability' in  ikeaStockData["availabilities"][1]['buyingOption']['cashCarry']:
                    data["stock"]=ikeaStockData["availabilities"][1]['buyingOption']['cashCarry']['availability']['quantity']
        else:
            log_error(p["sku"],hesabId,-1,p["name"],404,p["id"],f"Discontinued : {isSellable}",-1,-1,-1,tag)

    res = requests.post(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/cwc/v1/price",
                        headers=updateHeader
                        ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                        ,json=data)
def get_hesab_id(sku):
        payload = json.dumps({
            "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
            "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
            "barcode": sku
        })
        headers = {
        'Content-Type': 'application/json'
        }
        try:
            hesabfaRes = requests.post(hesanfa_url,payload,headers=headers)
            hesabfaKala =  hesabfaRes.json()
            return hesabfaKala["Result"]["Id"] 
        except Exception:
            return -1 
def log_error(sku,hesabId,stock,name,status,id,desc=f"NotFound / discontinued",currentPrice=-1,offerPrice=-1,ikeaPrice=-1,tag=""):
    writer.writerow([sku,hesabId,stock,name,status,desc,currentPrice,offerPrice,ikeaPrice,tag])
    requests.put(
        f'https://zardaan.com/wp-json/wc/v3/products/{id}',
        headers=putHeaders,
        json=put_json_data,
        auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
    )

def get_IKEA_Body(sku):
    return f'{{"searchParameters":{{"input":{sku},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'

def round_up(number):
 return round(number) if(number-int(number)>0.5) else number

def get_IU_PRICE(meta_data):
    for meta in meta_data:
        if meta["key"] =="_mnswmc_regular_price":
                return meta['value']

def get_API_KEY():
    pattern = r'ciaApiClientKey:"([^"]*)"'
    res = requests.get("https://www.ikea.com/ae/en/products/javascripts/pip-main.8a697bbcff8c691d0cc0.js",proxies=proxy)
    matches = re.findall(pattern,res.text)
    return matches[0]

def updateProductsPage(page):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        stock = p["stock_quantity"]
        ikeaStockData = {}
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=get_IKEA_Body(p["sku"]))
        apiKey = get_API_KEY()
        stockHeader["X-Client-ID"] = apiKey
        i=0
        while(i<5):
            try:
                ikeaStockResponse = requests.get('https://api.salesitem.ingka.com/availabilities/ru/ae', params={
                    'itemNos': p['sku'],
                    'expand': 'StoresList,Restocks,SalesLocations,DisplayLocations,ChildItems',
                },proxies=proxy
                , headers=stockHeader)
                ikeaStockData = ikeaStockResponse.json()
                break
            except(e):
                time.sleep(1)
                i+=1
        else:
            continue

        ikeaData  = ikeaResponse.json()

        time.sleep(0.5)
        
        hesabId =get_hesab_id(p["sku"])
        
        if("results"  not in ikeaData or len(ikeaData["results"])==0):
            log_error(p["sku"],hesabId,stock,p["name"],response.status_code,p["id"])
            continue
        item = ikeaData["results"][0]["items"][0]["product"]
        tag = item["tag"] if "tag" in item  else ""
        if tag == "NONE":
            tag = "" 
        IKEA_NUMERIC = item["salesPrice"]["numeral"]
        isSellable =   item["onlineSellable"]
        if  not isSellable:
            log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Out of Stock : {isSellable}",-1,-1,-1,tag)
            continue
        if not ikeaResponse.ok:
            log_error([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Discontinued : {isSellable}",-1,-1,-1,tag])
            continue

        if len(ikeaData["results"])==0:
            log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,p["id"],f"Discontinued : {isSellable}",-1,-1,-1,tag)
            continue
        offerPrice = round_up(IKEA_NUMERIC)
        if "previous" in item["salesPrice"]:
            number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
            itemPrice = float(number.replace(",","."))

        data = {
            "id": p["id"],
            "sale_price": offerPrice if tag =="NEW_LOWER_PRICE" else 0 ,
        }
        if(itemPrice!=None):
            data["reqular_price"] = float(itemPrice) 
        if "availabilities" in ikeaStockData and len(ikeaStockData["availabilities"])>=2:
            if(ikeaStockData["availabilities"][1]["availableForCashCarry"]):
                if 'availability' in  ikeaStockData["availabilities"][1]['buyingOption']['cashCarry']:
                        data["stock"]=ikeaStockData["availabilities"][1]['buyingOption']['cashCarry']['availability']['quantity']
            else:
                log_error(p["sku"],hesabId,-1,p["name"],404,p["id"],f"Discontinued : {isSellable}",-1,-1,-1,tag)

        res = requests.post(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/cwc/v1/price",
                            headers=updateHeader
                            ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                            ,json=data)
        if res.status_code == 500:
            breakpoint
        writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],res.status_code,f"Updated product {p['sku']}: قیمت {itemPrice} تخفیف: {offerPrice}",-1,offerPrice,IKEA_NUMERIC,tag])

if __name__ == '__main__':
    for i in range(1,pageCount+2):
        updateProductsPage(i)
    with ftplib.FTP('ftp.zardaan.com') as ftp:
        try:
            ftp.login(os.getenv('FTP_USER'), os.getenv('FTP_PASS'))
            filename = 'out.csv'
            with open('tmp.csv', 'wb') as fd:
                import codecs
                fd.write(codecs.BOM_UTF8)
                fd.write(output.getvalue().encode('utf-8'))
            with open('tmp.csv',"rb") as fd:
                res = ftp.storbinary("STOR " + filename, fd)
                if not res.startswith('226-File successfully transferred'):
                    print(f'Upload failed {res}')
                else:
                    print("write file succesfuly")
        except ftplib.all_errors as e:
            print('FTP error:', e)
    # updateProductSku("39552104") #۷۰۴۷۸۱۴۰properto