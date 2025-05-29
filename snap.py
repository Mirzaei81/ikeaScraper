import requests 
from PIL import Image
from io import BytesIO
def getProduct(sku):
	url = "https://zardaan.com/wp-json/wc/v3/products?sku={}".format(sku)
	headers = {
	'Authorization': 'Basic Y2tfYTdjNGVlM2U5NTc1MDI4MWQ5MTg1MmRlOTJkMjc1NWNkMDUyZGUyMjpjc18yNWU4NDQ4YzZkMWE1YzdkYTlhMGFlMDE0Y2M4ZWQ2YzViMGU2MWE5',
	'Content-Type': 'application/json',
	'Cookie': 'pxcelPage_c01002=1'
	}

	response = requests.get(url, headers=headers) 
	zProd = response.json()
	isMain = True	
	for img in zProd[0]["images"][:3]:
		imgData = requests.get(img["src"])
		ext:str = img["src"].split(".")[-1]
		if(ext.upper()=="JPG")	:
			ext= "JPEG"
		Pimg = Image.open(BytesIO(imgData.content))
		Pimg = Pimg.resize((600,600))
		resizedImg = BytesIO()
		Pimg.save(resizedImg,format=ext.upper())
		headers = {
			'accept': 'application/json',
			'accept-language': 'en-US,en;q=0.7',
			'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMDUiLCJqdGkiOiJhMjg1M2Y3NzE5MzI2YzYxNGQ4ZWM2Y2ZlM2IwZjQ1MGYwMDk0ZWU4ZWM4ZGVkZmNiMTNjNjU1NGVmNTE3Y2U5YzgwMzQxZmJhMGY1OTg0MiIsImlhdCI6MTc0ODA4MDQ3MS45Mzk5MTYsIm5iZiI6MTc0ODA4MDQ3MS45Mzk5MTksImV4cCI6MTc0ODY4NTI3MS45MzQ3NDksInN1YiI6IjQyNzM5MjAiLCJzY29wZXMiOlsicm9sZTpzZWxsZXIiXSwiYXV0aG9yaXphdGlvbl9kZXRhaWxzIjpbeyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9xdWV1ZTptcXR0LSovcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIiwid3JpdGUiLCJjb25maWd1cmUiXX0seyJ0eXBlIjoicHVzaCIsImxvY2F0aW9ucyI6WyJjbHVzdGVyOjEwNS92aG9zdDpwcy9leGNoYW5nZTphbXEudG9waWMvcm91dGluZy1rZXk6di1nZVpsODEiXSwiYWN0aW9ucyI6WyJyZWFkIl19XX0.o91zwFyBgoZSvV-99NJE7GxLAmrmbDBU0xopHZ66OU4rwFUNbxDOQRMIm6tvaw0EU7WFOQ9DFvfip5rYv4G0HIrkTRo0H_VcEEFww7rrQNhmUFriQBlCfP8LEDNNXMSbPZrGXMEvh_xyqsyTWYHrorTnuYcRUHPZh4tq465n6Fzhi5AskYJi55ayj3Y7p32EPKDKRFYX55KZ3XFoBfCwZ0z65ia-lH0LldDGspWP1SgAyikj6b3p7IZECqtNLawu5hCC_xd7jGx4fkgn4OwzjBZNztlRfpdVWxWArIRv8HQ3J1_9phi1nKTb_mPVhzJAXheLIhXfAEuKzRR4wxFYzqZVTGI-sXQrLuPO23_S4DwMCfnq1BALFbE0i2hOVFgyYFAg98W1-szodebNQivq5LmeN6a5gZRG7P38j5Ipg4RtllBP2yhKI6Wvqu1BoQzkpbMDpSC2FxpDMYshUkAzsypkrd6ZIr3br55hqeEPWdYDNMx8bVegl3ApR8fXg_jdnXop8kqIJ-LVJe3Aq0CzYNV6gkWVX4fL94VT0T9Q9AbPj7gBiH2jQBlgfSANHHZjKWEbU8mEIYFPCdAcgsRRb3BCStFCY4xzeZTKQmLHqGaXTwk0CqTaZxjGj-ey_E7QZOHdCGWtgYXuJUu2NrkkxBPoV78fn78SVSkFfPzqkHw',
			'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary9RierxoWj89jLWQz',
			'origin': 'https://seller.snappshop.ir',
			'priority': 'u=1, i',
			'referer': 'https://seller.snappshop.ir/',
			'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"Windows"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'sec-gpc': '1',
			'snappshop-seller-code': 'geZl81',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
			'uuid': '7f42c8f3-2d57-4e8d-b172-683fc84c6f5b',
			'x-client-type': 'seller',
		}

		files = {
			'image': (f"{str(img["id"])}.{ext}", resizedImg),
			'is_main':('true' if isMain else 'false'),
		}
		response = requests.post(
			'https://apix.snappshop.ir/vendors/v1/geZl81/product-quotes/gNylbe/images',
			headers=headers,
			files=files,
		
		)
		print(response.request.body)

		print(response.status_code)


getProduct("09509013")