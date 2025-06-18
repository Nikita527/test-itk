import aiohttp

API_URL = "https://api.exchangerate-api.com/v4/latest/{}"


async def app(scope, receive, send):
    """ASGI app."""
    assert scope["type"] == "http"

    path = scope.get("path", "/")
    if not path.startswith("/") or len(path) < 2:
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error": "Currency not specified"}',
        })
        return

    currency = path[1:].upper()
    url = API_URL.format(currency)

    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(url)
            if response.status == 200:
                data = await response.read()
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"application/json"],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": data,
                })
            else:
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [
                        [b"content-type", b"application/json"],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"error": "Currency not found"}',
                })
        except aiohttp.ClientError:
            await send({
                "type": "http.response.start",
                "status": 502,
                "headers": [
                    [b"content-type", b"application/json"],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error": "Upstream error"}',
            })
