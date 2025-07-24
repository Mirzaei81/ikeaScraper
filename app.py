"""
This is an Ikea Web scraper Module.
A scraper designed to automatically open a URL, navigate to a specific web page, 
extract multiple data types from different variables, and store the data in an 
organised manner in an external storage service.
"""

from IKEA_TYPES import IKEA_PRODUCT
from dotenv import load_dotenv
import requests
import os
import json
import ftplib
import csv 
import io 
import time
import requests

output = io.StringIO()
writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["sku","hesabfaCode","stock","name","status","description","currentPrice","offerPrice","ikeaPrice","tag"])
load_dotenv()

pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":1,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
pageCount =  int(pageResponse.headers["X-WP-Total"])

proxy ={
    "http":"http://127.0.0.1:10809",
    "https":"http://127.0.0.1:10809"
}

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
}
updateHeader = {
    'Content-Type': 'application/json',
    'Cookie': 'pxcelPage_c01002=1'
}

response = requests.get(url, headers=headers)

prices = response.json()

def get_products_sku_by_id(sku):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products/",params={"sku":sku},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    p = response.json()[0]
    data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
    ikeaAEResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=data)
    if(ikeaAEResponse.status_code!=200):
        resp = requests.put( 
            f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
            headers=putHeaders,
            json=put_json_data,
            auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
        )
        print("bad response",resp.status_code)
        with open(f"error/{p["sku"]}.text","w") as f:
            f.write(ikeaAEResponse.text)
            return


    payload = json.dumps({
        "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
        "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
        "barcode": p["sku"]
    })
    headers = {
    'Content-Type': 'application/json'
    }

    hesabfaRes = requests.post(hesanfa_url,payload,headers=headers)
    hesabfaKala =  hesabfaRes.json()
    hesabId = hesabfaKala["Result"]["Id"]
    try:
        ikeaData = ikeaAEResponse.json()
    except requests.exceptions.JSONDecodeError:
        print("decode error")
        return
    
    if(len(ikeaData["results"])==0):
        resp = requests.put(
            f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
            headers=putHeaders,
            json=put_json_data,
            auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
        )
        print("item not found",resp.status_code)

    item = ikeaData["results"][0]["items"][0]["product"]
    IKEA_NUMERIC = item["salesPrice"]["numeral"]
    itemPrice =0
    if "previous" in item["salesPrice"]:
        number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
        itemPrice = float(number.replace(",","."))
    else:
        itemPrice = IKEA_NUMERIC
    print("Current Price",IKEA_NUMERIC,"OfferedPrice",itemPrice)
    isSellable = item["onlineSellable"]
    if not isSellable:
        requests.get(f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
            headers=putHeaders,
            json=put_json_data,
            auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
        )
        print("is not selleble",resp.status_code)

    offerPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
    
    print(f"itemPrice: {itemPrice} offerPrice: {offerPrice}",end="")
    updateHeader = {
        "Content-Type": "application/json"
    }
    data={
        "id":p["id"],
        "reqular_price":itemPrice,
        "sale_price":offerPrice
    }                
    resp = requests.post(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/cwc/v1/price",
                        headers=updateHeader
                        ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                        ,data=json.dumps(data))
    print(resp.text)

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

def get_products_sku(page):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        stock = p["stock_quantity"]
        if(stock ==None or stock<=0):
            log_error(p["sku"],-1,stock,p["name"],response.status_code,p["id"])
            continue
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=get_IKEA_Body(p["sku"]))
        ikeaData:IKEA_PRODUCT  = ikeaResponse.json()

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
            log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Out of Stock : {isSellable}",-1,-1,-1,tag)
            continue
        if ikeaResponse.status_code!=200:
            writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Discontinued : {isSellable}",-1,-1,-1,tag])
            continue

        if len(ikeaData["results"])==0:
            log_error(p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Discontinued : {isSellable}",-1,-1,-1,tag)
            continue
        offerPrice = round_up(IKEA_NUMERIC)
        if "previous" in item["salesPrice"]:
            number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
            itemPrice = float(number.replace(",","."))
        else:
            itemPrice = get_IU_PRICE(meta_data=p["meta_data"])


        data = {
            "id": p["id"],
            "reqular_price":float(itemPrice) ,
            "sale_price": offerPrice
        }
        res = requests.post(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/cwc/v1/price",
                            headers=updateHeader
                            ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                            ,json=data)
        print(f"updatad price for item {p['sku']} price {itemPrice} offerPrice {offerPrice} with {res.text}")
        if res.status_code == 500:
            breakpoint
        writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],res.status_code,f"Updated product {p['sku']}: قیمت {itemPrice} تخفیف: {offerPrice}",-1,offerPrice,IKEA_NUMERIC,tag])
        
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

if __name__ == '__main__':
    for i in range(1,pageCount+2):
        get_products_sku(i)
    #get_products_sku_by_id("39533356") #۷۰۴۷۸۱۴۰properto