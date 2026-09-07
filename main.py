import asyncio
from dotenv import load_dotenv
load_dotenv()
from Ikea.ikea_parser import getProductDetail,init as ikeaInit
from Ikea.zardan import updateItem,getItems,init as zardanInit,dispose,root
async def main():
    i=0 
    await zardanInit()
    await ikeaInit()
    c = 0
    t = 0 
    try:
        async for  i in getItems():
            price,tag,stock= await getProductDetail(i)
            t+=1
            if price:
                c +=1
                await updateItem(i,price,stock,tag)

        print(f"ended the session with {c}/{t}")
        root.info(f"ended the session with {c}/{t}")
    except Exception as e:
        print(e)
async def runner():
    try:
        await asyncio.wait_for(main(),timeout=3600*5+60*57)
    except Exception as e:
        await dispose()
asyncio.run(runner())
