import asyncio
from Ikea.ikea_parser import getProductDetail,init as ikeaInit
from Ikea.zardan import updateItem,getItems,init as zardanInit
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
asyncio.wait_for(main(),timeout=3600*5+56*60)
