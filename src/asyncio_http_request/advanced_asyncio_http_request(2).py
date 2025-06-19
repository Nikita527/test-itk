import asyncio
import aiofiles
import aiohttp
import json
import ijson
from typing import Dict


async def _producer(url_queue: asyncio.Queue, url_file: str):
    """
    Принимает файл с URL.

    Заполняет очередь URL.
    """
    async with aiofiles.open(url_file, "r", encoding="utf-8") as f:
        async for line in f:
            url = line.strip()
            if url:
                await url_queue.put(url)


async def _worker(
    url_queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    write_queue: asyncio.Queue,
):
    """Выполняет запросы и помещает результаты в очередь."""
    while True:
        url = await url_queue.get()
        if url is None:
            url_queue.task_done()
            break
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            async for obj in ijson.items_async(resp.content, ""):
                                line = json.dumps(
                                    {"url": url, "content": obj}, ensure_ascii=False
                                )
                                await write_queue.put(line)
                                break
                        except Exception as e:
                            print(f"Failed to parse JSON for {url}: {e}")
                    else:
                        print(f"Content-Type is not JSON for {url}: {content_type}")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
        url_queue.task_done()


async def _writer(write_queue: asyncio.Queue, file_path: str):
    """Пишет результаты в файл."""
    async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
        while True:
            line = await write_queue.get()
            if line is None:
                write_queue.task_done()
                break
            await f.write(line + "\n")
            write_queue.task_done()


async def fetch_urls(
    url_file: str, file_path: str, concurrency: int = 5
) -> Dict[str, int]:
    """
    Принимает список URL и путь к файлу.

    Возвращает dict: url -> status_code и одновременно пишет в файл JSON.
    """
    url_queue = asyncio.Queue(maxsize=concurrency * 2)
    write_queue = asyncio.Queue(maxsize=concurrency * 2)

    connector = aiohttp.TCPConnector(
        limit=concurrency,
        limit_per_host=max(1, concurrency // 10),
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        writer_task = asyncio.create_task(_writer(write_queue, file_path))
        workers = [
            asyncio.create_task(_worker(url_queue, session, write_queue))
            for _ in range(concurrency)
        ]
        await _producer(url_queue, url_file)
        for _ in workers:
            await url_queue.put(None)
        await url_queue.join()
        await write_queue.join()
        await write_queue.put(None)
        await writer_task
        await asyncio.gather(*workers)


if __name__ == "__main__":
    asyncio.run(fetch_urls("./urls.txt", "./results1.jsonl"))
