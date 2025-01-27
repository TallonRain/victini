import asyncio
import socket
import ssl
import aiohttp
import certifi
import logging


def run(client, token, debug_mode):
    async def runner():
        async with client:
            client.http.connector = aiohttp.TCPConnector(limit=0, family=socket.AF_INET,
                                                         ssl=ssl.create_default_context(cafile=certifi.where()))
            await client.start(token)

    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)
    if not debug_mode:
        logging.basicConfig(level=logging.INFO)

    asyncio.run(runner())
