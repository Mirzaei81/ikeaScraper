"""
This is an Ikea Web scraper Module.
A scraper designed to automatically open a URL, navigate to a specific web page, 
extract multiple data types from different variables, and store the data in an 
organised manner in an external storage service.
"""

from IKEA_TYPES import Welcome9
from dotenv import load_dotenv
import requests
import os
import json
import ftplib
import csv 
import io 
import sys
from math import ceil
output = io.StringIO()
writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["sku","hesabfaCode","stock","name","status","description","currentPrice","offerPrice","ikeaPrice","tag"])
load_dotenv()

proxy ={
    "http":"http://127.0.0.1:10809",
    "https":"http://127.0.0.1:10809"
}
hesanfa_url = "https://api.hesabfa.com/v1/item/getByBarcode"
import requests

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
response = requests.get(url, headers=headers)

prices = response.json()

def get_products_sku_by_id(sku):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products/",params={"sku":sku},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaAEResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=data)
        print(ikeaAEResponse.status_code)
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
                break


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
            sys.exit(-1)

        with open("out.json","w") as f:
            f.write(json.dumps(ikeaData))
        
        if(len(ikeaData["results"])==0):
            resp = requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            print("item not found",resp.status_code)
            break

        item = ikeaData["results"][0]["items"][0]["product"]
        tag = item["tag"] if "tag" in item  else ""
        IKEA_NUMERIC = item["salesPrice"]["numeral"]
        itemPrice =0
        if "previous" in item["salesPrice"]:
            number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
            itemPrice = float(number.replace(",","."))
        else:
            itemPrice = IKEA_NUMERIC
        isSellable = item["onlineSellable"]
        if not isSellable:
            requests.get(f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            print("is not selleble",resp.status_code)

        offerPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
        
        print(f"item: {item}\nitemPrice: {itemPrice} offerPrice: {offerPrice}",end="")
        meta_datas = p["meta_data"]
        for i in range(len(p["meta_data"])):
            if p["meta_data"][i]["key"]=="_mnswmc_currency_ids":
                try:
                    itemId = json.loads(meta_datas[i]["value"])[0]
                    itemPrice *=prices[itemId]["rate"]
                except Exception as e:
                    break
            if p["meta_data"][i]["key"]=="_mnswmc_regular_price":
                currentPrice = meta_datas[i]["value"]
                print("currentPrice: ",currentPrice)    
                if int(offerPrice)>int(currentPrice):
                    meta_datas[i]["value"] = itemPrice
                    updateHeader = {
                        "Content-Type": "application/json"
                    }
                    data={
                        "meta_data" : meta_datas,
                        "sales_price": offerPrice
                    }
                    requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                        headers=updateHeader
                                        ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                        ,data=json.dumps(data))
                break

import time
def get_products_sku():
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":1,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        stock = p["stock_quantity"]
        if(stock==0):
            continue
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
        ikeaData:Welcome9  = ikeaResponse.json()
        payload = json.dumps({
            "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
            "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
            "barcode": p["sku"]
        })
        headers = {
        'Content-Type': 'application/json'
        }

        time.sleep(0.5)
        try:
            hesabfaRes = requests.post(hesanfa_url,payload,headers=headers)
            hesabfaKala =  hesabfaRes.json()
            hesabId = hesabfaKala["Result"]["Id"] 
        except Exception:
            print(p["sku"])
        hesabId =-1
        if("results"  not in ikeaData or len(ikeaData["results"])==0):

            writer.writerow([p["sku"],hesabId,stock,p["name"],ikeaResponse.status_code,f"NotFound / discontinued",-1,-1,-1,""])
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )

            continue
        item = ikeaData["results"][0]["items"][0]["product"]
        tag = item["tag"] if "tag" in item  else ""
        IKEA_NUMERIC = item["salesPrice"]["numeral"]
        isSellable =   item["onlineSellable"]
        if  not isSellable:
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Out of Stock : {isSellable}",-1,-1,-1,tag])
            continue
        if ikeaResponse.status_code!=200:
            writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Discontinued : {isSellable}",-1,-1,-1,tag])
            continue
        if len(ikeaData["results"])==0:
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Discontinued : {isSellable}",-1,-1,-1,tag])
            continue
        offerPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
        if "previous" in item["salesPrice"]:
            number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
            itemPrice = float(number.replace(",","."))
        else:
            itemPrice = IKEA_NUMERIC
        currentPrice = 0
        meta_datas = p["meta_data"]
        for i in range(len(p["meta_data"])):
            if p["meta_data"][i]["key"]=="_mnswmc_currency_ids":
                try:
                    itemId = json.loads(meta_datas[i]["value"])[0]
                    itemPrice *=prices[itemId]["rate"]
                except Exception as e:
                    break
                updateHeader = {
                    "Content-Type": "application/json"
                }
                data={
                    "meta_data" : meta_datas,
                    "sale_price": offerPrice
                }
                requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                    headers=updateHeader
                                    ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                    ,data=json.dumps(data))

                writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Discontinued : {isSellable}",-1,-1,-1,tag])
                break                     
        writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Updated product {p['sku']}: {currentPrice} -> {offerPrice} offer by {offerPrice}",currentPrice,offerPrice,IKEA_NUMERIC,tag])
    for page in range(2,int(response.headers["X-WP-Total"])):
        pageData=None
        for  i in range(5):
            try:
                pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page,"per_page":100},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
                pageData = pageResponse.json()

                time.sleep(1)
                break
            except Exception:
                print(pageResponse.status_code)

        for p in pageData:
            stock = p["stock_quantity"]
            if(stock==0):
                continue
            data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
            pageResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
            payload = json.dumps({
                "apiKey": "hPYhvvcfeP1q4EAd1fucG9bCIJuAXUrW",
                "loginToken": "6deb2b60112cd8cb927cbe6ccea860bbca6726964f642559972551d87f13afaed96e596d1a18fb49ed5fdbda5fa6335b",
                "barcode": p["sku"]
            })
            headers = {
            'Content-Type': 'application/json'
            }

            time.sleep(0.4)
            try:
                hesabfaRes = requests.post(hesanfa_url,payload,headers=headers)
                hesabfaKala =  hesabfaRes.json()
                hesabId = hesabfaKala["Result"]["Id"]
            except Exception:
                hesabId = -1

            if pageResponse.status_code!=200:
                writer.writerow([p["sku"],hesabId,stock,p["name"],ikeaResponse.status_code,f"Error / discontinued",-1,-1,-1,""])
                continue
            ikeaData:Welcome9  = pageResponse.json()
 
            if("results"  not in ikeaData  or len(ikeaData["results"])==0):
                requests.put(
                    f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                    headers=putHeaders,
                    json=put_json_data,
                    auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                )
                writer.writerow([p["sku"],hesabId,stock,p["name"],ikeaResponse.status_code,f"Error / discontinued",-1,-1,-1,""])
                continue
            if  "results" in ikeaData and len(ikeaData["results"])>0:
                item = ikeaData["results"][0]["items"][0]["product"]
                IKEA_NUMERIC = item["salesPrice"]["numeral"]

                offerPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
                itemPrice = offerPrice
                if "previous" in item:
                    number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
                    itemPrice = float(number.replace(",","."))
                
                tag = item["tag"] if "tag" in item  else ""
                isSellable = item["onlineSellable"]
                if  not isSellable:
                    requests.put(
                        f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                        headers=putHeaders,
                        json=put_json_data,
                        auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                    )
                    writer.writerow([p["sku"],hesabId,stock,p["name"],ikeaResponse.status_code,f"Out Of stock",-1,-1,-1,""])
                    continue

                offerPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
                if "previous" in item["salesPrice"]:
                    number = item["salesPrice"]["previous"]["wholeNumber"]+item["salesPrice"]["previous"]["separator"]+item["salesPrice"]["previous"]["decimals"]
                    itemPrice = float(number.replace(",","."))
                else:
                    itemPrice = IKEA_NUMERIC
                currentPrice = 0
                meta_datas = p["meta_data"]
                
                for i in range(len(p["meta_data"])):
                    if p["meta_data"][i]["key"]=="_mnswmc_currency_ids":
                        try:
                            itemId = json.loads(meta_datas[i]["value"])[0]
                            itemPrice *=prices[itemId]["rate"]
                        except Exception as e:
                            break
                        meta_datas[i]["value"] = str(ceil(itemPrice/1000)*1000)
                        updateHeader = {
                            "Content-Type": "application/json"
                        }
                        data={
                            "meta_data" : meta_datas,
                            "sale_price": offerPrice
                        }
                        requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                            headers=updateHeader
                                            ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                            ,data=json.dumps(data))
                        break
                writer.writerow([p["sku"],hesabId,p["stock_quantity"],p["name"],ikeaResponse.status_code,f"Updated product {p['sku']}: {currentPrice} -> {offerPrice} offer by {offerPrice}",currentPrice,offerPrice,IKEA_NUMERIC,tag])
            else:
                requests.put(
                    f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                    headers=putHeaders,
                    json=put_json_data,
                    auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                )
                writer.writerow([p["sku"],hesabId,stock,p["name"],ikeaResponse.status_code,f"NotFound / discontinued",-1,-1,-1,""])
        
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
    get_products_sku()
    #get_products_sku_by_id("20468110") #۷۰۴۷۸۱۴۰
