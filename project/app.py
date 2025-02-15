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
load_dotenv()

proxy = {
    "http":"http://127.0.0.1:10809",
    "https":"http://127.0.0.1:10809",
}


def get_products_sku_by_id(sku):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products/",params={"sku":sku},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
        if(ikeaResponse.status_code!=200):
            print(ikeaResponse.status_code)
            with open(f"error/{p["sku"]}.text","w") as f:
                f.write(ikeaResponse.text)
                break
        ikeaData = ikeaResponse.json()
        IKEA_NUMERIC = ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["numeral"]
        targetPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
        i = 0
        meta_datas = p["meta_data"]
        for i in range(len(p["meta_data"])):
            if p["meta_data"][i]["key"]=="_mnswmc_regular_price":
                currentPrice = meta_datas[i]["value"]
                if int(targetPrice)>int(currentPrice):
                    meta_datas[i]["value"] = targetPrice
                    updateHeader = {
                        "Content-Type": "application/json"
                    }
                    data={
                        "meta_data" : meta_datas
                    }
                    resP = requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                        headers=updateHeader
                                        ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                        ,data=json.dumps(data))
                    print(f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}")
                    break
            i+=1
import time
def get_products_sku():
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    time.sleep(0.5)
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=data)
        ikeaData:Welcome9  = ikeaResponse.json()
        if(len(ikeaData["results"])==0):
            print(p["sku"]+ " this sku not found")
            open(f"not_founds/{p["sku"]}.json","w").write(json.dumps(p))
            continue
        isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
        if  not isSellable:
            with open(f'nonSeleble/{p["sku"]}.json',"w") as f:
                f.write(ikeaResponse.text)
            continue
        if ikeaResponse.status_code!=200:
            with open(f'error/{p["sku"]}.json',"w") as f:
                f.write(json.dumps(ikeaResponse))
            continue
        if len(ikeaData["results"])==0:
            with open(f'error/{p["sku"]}.json',"w") as f:
                f.write(json.dumps(ikeaResponse))
            continue
        IKEA_NUMERIC = ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["numeral"]
        targetPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
        i = 0
        meta_datas = p["meta_data"]
        for i in range(len(p["meta_data"])):
            if p["meta_data"][i]["key"]=="_mnswmc_regular_price":
                currentPrice = meta_datas[i]["value"]
                if int(targetPrice)>int(float(currentPrice)):
                    meta_datas[i]["value"] = targetPrice
                    updateHeader = {
                        "Content-Type": "application/json"
                    }
                    data={
                        "meta_data" : meta_datas
                    }
                    requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                        headers=updateHeader
                                        ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                        ,data=json.dumps(data))
                    print(f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}")
                    break
            i+=1
    for page in range(2,int(response.headers["X-WP-Total"]),10):
        pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
        time.sleep(0.5)
        for p in pageResponse.json():
            data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
            pageResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',proxies=proxy,params={"c":"sr","v":20241114},data=data)
            if pageResponse.status_code!=200:
                with open(f'error/{p["sku"]}.json',"w") as f:
                    f.write(pageResponse.text)
                continue
            ikeaData:Welcome9  = pageResponse.json()
            if(len(ikeaData["results"])==0):
                print(p["sku"]+ " this sku not found")
                open(f"not_founds/{p["sku"]}.json","w").write(json.dumps(p))
                continue
            isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
            if  not isSellable:
                with open(f'nonSeleble/{p["sku"]}.json',"w") as f:
                    f.write(pageResponse.text)
                continue

            if len(ikeaData["results"])>0:
                # IKEA_CODE = ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["currencyCode"]
                IKEA_NUMERIC = ikeaData["results"][0]["items"][0]["product"]["salesPrice"]["numeral"]
                targetPrice = round(IKEA_NUMERIC) if(IKEA_NUMERIC-int(IKEA_NUMERIC)>0.5) else IKEA_NUMERIC
                i = 0
                meta_datas = p["meta_data"]
                for i in range(len(p["meta_data"])):
                    if p["meta_data"][i]["key"]=="_mnswmc_regular_price":
                        currentPrice = meta_datas[i]["value"]
                        if int(targetPrice)>int(float(currentPrice)):
                            meta_datas[i]["value"] = targetPrice
                            updateHeader = {
                                "Content-Type": "application/json"
                            }
                            data={
                                "meta_data" : meta_datas
                            }
                            requests.put(f"https://{os.getenv("WOOCOMERCE_HOST")}/wp-json/wc/v3/products/{p["id"]}",
                                                headers=updateHeader
                                                ,auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                                                ,data=json.dumps(data))
                            print(f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}")
                            break
                    i+=1
if __name__ == '__main__':
    get_products_sku()
    # get_products_sku_by_id(20410888)