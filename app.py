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
output = io.StringIO()
writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["sku","status","description"])
load_dotenv()



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
    time.sleep(5)
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
        ikeaData:Welcome9  = ikeaResponse.json()
        if(len(ikeaData["results"])==0):
            writer.writerow(p["sku"],f"NotFound / discontinued",ikeaResponse.status_code)
            continue
        isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
        if  not isSellable:
            writer.writerow(p["sku"],f"Out of Stock : {isSellable}",ikeaResponse.status_code)
            continue
        if ikeaResponse.status_code!=200:
            writer.writerow(p["sku"],f"Error / discontinued",ikeaResponse.status_code)
            continue
        if len(ikeaData["results"])==0:
            writer.writerow(p["sku"],f"notFound / discontinued",ikeaResponse.status_code)
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
                    writer.writerow(p["sku"],f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}",ikeaResponse.status_code)
                    break
            i+=1
    for page in range(2,int(response.headers["X-WP-Total"]),10):
        pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
        time.sleep(5)
        for p in pageResponse.json():
            data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
            pageResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
            if pageResponse.status_code!=200:
                writer.writerow(p["sku"],f"Error / discontinued",ikeaResponse.status_code)
                continue
            ikeaData:Welcome9  = pageResponse.json()
            if(len(ikeaData["results"])==0):
                writer.writerow(p["sku"],f"Error / discontinued",ikeaResponse.status_code)
                continue
            isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
            if  not isSellable:
                writer.writerow(p["sku"],f"OutOfStock",ikeaResponse.status_code)
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
                            writer.writerow(p["sku"],f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}",ikeaResponse.status_code)
                            break
                    i+=1
    with ftplib.FTP('ftp.chitoobox.com') as ftp:
        try:
            ftp.login(os.getenv('FTP_USER'), os.getenv('FTP_PASS'))
            filename = 'out.csv'
            string_to_write = output.getvalue()
            with open(filename, 'w') as fp:
                fp.write(string_to_write)
            with open(filename, 'r') as fp:
                res = ftp.storlines("STOR " + filename, fp)
                if not res.startswith('226 Transfer complete'):
                    print('Upload failed')
        except ftplib.all_errors as e:
            print('FTP error:', e)
if __name__ == '__main__':
    get_products_sku()
    # get_products_sku_by_id(20410888)