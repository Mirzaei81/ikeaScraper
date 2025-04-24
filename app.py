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
writer.writerow(["sku","name","status","description"])
load_dotenv()



def get_products_sku_by_id(sku):
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products/",params={"sku":sku},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaAEResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
        ikeaARResponse = requests.post('https://sik.search.blue.cdtapps.com/ar/en/search',params={"c":"sr","v":20241114},data=data)
        print(ikeaARResponse)
        break
        if(ikeaAEResponse.status_code!=200):
            print(ikeaAEResponse.status_code)
            with open(f"error/{p["sku"]}.text","w") as f:
                f.write(ikeaAEResponse.text)
                break
        ikeaData = ikeaAEResponse.json()
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
putHeaders = {
    'Content-Type': 'application/json',
}

put_json_data = {
    'status': 'pending',
}
import time
def get_products_sku():
    response = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
    print(response.status_code)
    time.sleep(5)
    for p in response.json():
        data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
        ikeaResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
        ikeaData:Welcome9  = ikeaResponse.json()
        if(len(ikeaData["results"])==0):
            writer.writerow([p["sku"],p["name"],f"NotFound / discontinued",ikeaResponse.status_code])
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )

            continue
        isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
        if  not isSellable:
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            writer.writerow([p["sku"],p["name"],f"Out of Stock : {isSellable}",ikeaResponse.status_code])
            continue
        if ikeaResponse.status_code!=200:
            writer.writerow([p["sku"],p["name"],f"Error / discontinued",ikeaResponse.status_code])
            continue
        if len(ikeaData["results"])==0:
            requests.put(
                f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                headers=putHeaders,
                json=put_json_data,
                auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
            )
            writer.writerow([p["sku"],p["name"],f"notFound / discontinued",ikeaResponse.status_code])
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
                    writer.writerow([p["sku"],p["name"],f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}",ikeaResponse.status_code])
                    break
                else: 
                    writer.writerow([p["sku"],p["name"],f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}",ikeaResponse.status_code])
                    break
            i+=1
    for page in range(2,int(response.headers["X-WP-Total"]),10):
        pageData=None
        for  i in range(5):
            try:
                pageResponse = requests.get("https://"+os.getenv("WOOCOMERCE_HOST")+"/wp-json/wc/v3/products",params={"page":page},auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET")))
                time.sleep(5)
                pageData = pageResponse.json()
                break
            except requests.RequestsJSONDecodeError:
                print(pageResponse.status_code)
        
        for p in pageData:
            data = f'{{"searchParameters":{{"input":{p["sku"]},"type":"QUERY"}},"components":[{{"component":"PRIMARY_AREA"}}]}}'
            pageResponse = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search',params={"c":"sr","v":20241114},data=data)
            if pageResponse.status_code!=200:
                writer.writerow([p["sku"],p["name"],f"Error / discontinued",ikeaResponse.status_code])
                continue
            ikeaData:Welcome9  = pageResponse.json()
            if(len(ikeaData["results"])==0):
                requests.put(
                    f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                    headers=putHeaders,
                    json=put_json_data,
                    auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                )
                writer.writerow([p["sku"],p["name"],f"Error / discontinued",ikeaResponse.status_code])
                continue
            isSellable = ikeaData["results"][0]["items"][0]["product"]["onlineSellable"]
            if  not isSellable:
                requests.put(
                    f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                    headers=putHeaders,
                    json=put_json_data,
                    auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                )
                writer.writerow([p["sku"],p["name"],f"OutOfStock",ikeaResponse.status_code])
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
                            writer.writerow([p["sku"],p["name"],f"Updated product {p['sku']}: {currentPrice} -> {targetPrice}",ikeaResponse.status_code])
                            break
                    i+=1
            else:
                requests.put(
                    f'https://zardaan.com/wp-json/wc/v3/products/{p["id"]}',
                    headers=putHeaders,
                    json=put_json_data,
                    auth=(os.getenv("WOOCOMERCE_KEY"),os.getenv("WOOCOMERCE_SECRET"))
                )
        
    with ftplib.FTP('ftp.zardaan.com.com') as ftp:
        try:
            ftp.login(os.getenv('FTP_USER'), os.getenv('FTP_PASS'))
            filename = 'out.csv'
            with open('tmp.csv', 'w',encoding="utf-8") as fd:
                fd.write(output.getvalue())
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
    # get_products_sku_by_id(20410888)