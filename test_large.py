import ijson
import aiofiles
import asyncio

async def main():
    async with aiofiles.open("./large.json","rb") as f:
        parser =  ijson.items_async(f,"response.item")
        async for item in parser:
            print(item)


if __name__ == "__main__":
    asyncio.run(main())
