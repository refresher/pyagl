from random import randint
import sys
import asyncio
from random import randint
from websockets import connect
from websockets.exceptions import ConnectionClosedError
import os
import json
import concurrent
from aglbaseservice import AGLBaseService


class GPSService(AGLBaseService):
    def __init__(self, ip, port):
        super().__init__(api='gps', ip=ip, port=port)

    async def location(self):
        verb = 'location'
        msgid = randint(0, 999999)
        await self.send(f'[2,"{msgid}","{self.api}/{verb}",""]')
        return await self.receive()

    async def subscribe(self, event='location'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        await super().subscribe(event=event)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', '30011')

    gpss = await GPSService(ip=addr, port=port)

    await gpss.location()
    # listener = loop.create_task(gpss.listener())



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))