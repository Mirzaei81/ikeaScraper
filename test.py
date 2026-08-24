import aiofiles
import asyncio


async def main():
    fPostId = await aiofiles.open("post.id","r+", encoding="utf-8-sig")
    await fPostId.seek(0)
    await fPostId.write('12345')
    await fPostId.truncate()
asyncio.wait_for(main(),timeout=3600*5+56*60)