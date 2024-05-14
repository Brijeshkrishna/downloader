import httpx
import asyncio
import aiofiles

import os

async def download(url:str, folder:str):
    filename = url.split("/")[-1]
    resp =  httpx.get(url)
    resp.raise_for_status()
    async with aiofiles.open(os.path.join(folder, filename), "wb") as f:
        await f.write(resp.content)


async def download_all_photos(out_dir: str):
    resp =  httpx.get("https://jsonplaceholder.typicode.com/photos")
    resp.raise_for_status()
    urls = list(set(d["url"] for d in resp.json()))[:100]
    os.makedirs(out_dir, exist_ok=True)
    await asyncio.gather(*[download(url, out_dir) for url in urls])


if __name__ == "__main__":
    asyncio.run(download_all_photos('100_photos'))