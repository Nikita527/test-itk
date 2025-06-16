import asyncio
import json
from typing import Dict, List

import aiohttp


async def _fetch_one(session: aiohttp.ClientSession,
                     url: str,
                     semaphore: asyncio.Semaphore) -> Dict[str, int]:
    """
    Выполняет один запрос под управлением семафора.

    Возвращает словарь {"url": ..., "status_code": ...}
    """
    async with semaphore:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                status = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError):
            # любые сетевые ошибки и таймауты — помечаем кодом 0
            status = 0
        return {"url": url, "status_code": status}


async def fetch_url(urls: List[str], file_path: str) -> Dict[str, int]:
    """
    Принимает список URL и путь к файлу.

    Возвращает dict: url -> status_code и одновременно пишет в файл JSON.
    """
    semaphore = asyncio.Semaphore(5)
    results: Dict[str, int] = {}
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(_fetch_one(session, url, semaphore))
            for url in urls
        ]

        with open(file_path, "w", encoding="utf-8") as f:
            for coro in asyncio.as_completed(tasks):
                res = await coro
                results[res["url"]] = res["status_code"]
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

    return results


if __name__ == "__main__":
    urls = [
        "https://ya.ru",
        "https://google.com",
        "https://yandex.ru",
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]
    final_results = asyncio.run(fetch_url(urls, "./results.json"))
    print(final_results)
