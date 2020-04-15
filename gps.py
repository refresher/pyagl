import asyncio
import os
import asyncssh
from asyncssh import SSHClientProcess
from aglbaseservice import AGLBaseService
from parse import *
import re
import argparse

class GPSService(AGLBaseService):
    def __init__(self, ip, port=None):
        super().__init__(api='gps', ip=ip, port=port, service='agl-service-gps')

    async def location(self):
        return await self.request('location', waitresponse=True)

    async def subscribe(self, event='location'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        await super().subscribe(event=event)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', '30011')
    jsonpayload = os.environ.get('AGL_TGT_JSON_PAYLOAD', None)

    gpss = await GPSService(addr)
    print(await gpss.location())
    listener = loop.create_task(gpss.listener())
    await listener


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))