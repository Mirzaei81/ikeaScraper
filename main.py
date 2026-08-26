import asyncio
from Ikea.ikea_parser import getProductDetail,init as ikeaInit
from Ikea.zardan import updateItem,getItems,init as zardanInit,dispose
async def main():
    i=0 
    await zardanInit()
    await ikeaInit()
    try:
        async for  i in getItems():
            price,tag,stock= await getProductDetail(i)
            if price:
                await updateItem(i,price,stock,tag)
    except Exception as e:
        print(e)
async def runner():
    try:
        await asyncio.wait_for(main(),timeout=3600*5+60*57)
    except Exception as e:
        await dispose()
asyncio.run(runner())
