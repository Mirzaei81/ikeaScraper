import ftplib
import io
import os
import requests
import json

import csv
products = []
output = io.StringIO()
writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(["name","tag"])
with open("dist/zarddanProduct.txt","r")as f :
    for line in f:
        if "=" in line:
            k,v = line.split("=")
            products[k.strip()] = v

MAX_PRODCOUNTS = 0
def parseProd(i):
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
    }

    params = {
        'c': 'listaf',
        'v': '20241114',
    }
    data = {"searchParameters":{"input":"new_lower_price","type":"SPECIAL"},"store":"218","optimizely":{"ran-7101_-_red_vs_grey_crossed_over_icon_for_not_sold":None,"listing_3299_event_orch_null_test":None,"listing_3332_collapsed_filter_bar":None,"sik_null_test_20250514_default":"a"},"optimizelyAttributes":{"market":"ae","device":" ","deviceType":"desktop","deviceVendor":" ","isLoggedIn":False,"environment":"prod","browser":"Brave","os":"Windows","language":"en","feedMarket":"en-AE","locale":"en-AE","customerType":"guest","isEntranceVisit":False,"pip_to_pip_src":""},"isUserLoggedIn":False,"components":[{"component":"PRIMARY_AREA","columns":4,"types":{"main":"PRODUCT","breakouts":["PLANNER","LOGIN_REMINDER","MATTRESS_WARRANTY"]},"filterConfig":{"f-online-sellable":True,"subcategories-style":"tree-navigation","max-num-filters":4},"sort":"MOST_POPULAR","window":{"offset":24000*i+1,"size":24}}]}
    response = requests.post('https://sik.search.blue.cdtapps.com/ae/en/search', params=params, headers=headers, data=json.dumps(data))
    ikeaProd = response.json()
    MAX_PRODCOUNTS =  int(ikeaProd["results"][0]["metadata"]["max"])
    for item in ikeaProd["results"][0]["items"]:
        tag =  item['product']["tag"]
        sku  = item['product']["id"]
        if sku in products:
            writer.writerow([products[sku],tag])

        else:
            url = "https://zardaan.com/wp-json/wc/v3/products?sku={}".format(sku)
            headers = {
            'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
            'Content-Type': 'application/json',
            'Cookie': 'pxcelPage_c01002=1'
            }

            response = requests.get(url, headers=headers) 
            zProd = response.json()
            writer.writerow([zProd[0]["name"],tag])
            with open("zarrdanProuct","a") as f: 
                f.write(f"{sku}={zProd["name"]}")
parseProd(0)
for i in range(1,(MAX_PRODCOUNTS//24)+1):
    parseProd(i)
with ftplib.FTP('ftp.zardaan.com') as ftp:
    try:
        ftp.login(os.getenv('FTP_USER'), os.getenv('FTP_PASS'))
        filename = 'offers.csv'
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