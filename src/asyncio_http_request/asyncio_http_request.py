import asyncio
import aiofiles
import aiohttp
import json
from typing import Dict, List


async def _producer(url_queue: asyncio.Queue, urls: List[str]):
    """
    Принимает очередь и список URL.

    Заполняет очередь URL."""
    for url in urls:
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
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                status = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError):
            # любые сетевые ошибки и таймауты — помечаем кодом 0
            status = 0
        line = json.dumps(
            {"url": url, "status_code": status}, ensure_ascii=False
        )
        await write_queue.put(line)
        url_queue.task_done()


async def _writer(write_queue: asyncio.Queue, file_path: str):
    """Пишет результаты в файл."""
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        while True:
            line = await write_queue.get()
            if line is None:
                write_queue.task_done()
                break
            await f.write(line + "\n")
            write_queue.task_done()


async def fetch_url(
    urls: List[str],
    file_path: str,
    concurrency: int = 100
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
        await _producer(url_queue, urls)
        for _ in workers:
            await url_queue.put(None)
        await url_queue.join()
        await write_queue.join()
        await write_queue.put(None)
        await writer_task
        await asyncio.gather(*workers)


if __name__ == "__main__":
    urls = [
        "https://ya.ru",
        "https://google.com",
        "https://yandex.ru",
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]
    asyncio.run(fetch_url(urls, "./results.json"))
