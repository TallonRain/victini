import asyncio
import socket
import ssl

import aiohttp
import certifi
import discord



def run(client, token):
    async def runner():
        async with client:
            client.http.connector = aiohttp.TCPConnector(limit=0, family=socket.AF_INET,
                                                         ssl=ssl.create_default_context(cafile=certifi.where()))
            await client.start(token)

    discord.utils.setup_logging()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        # nothing to do here
        # `asyncio.run` handles the loop cleanup
        # and `self.start` closes all sockets and the HTTPClient instance.
        return
