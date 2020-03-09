from random import randint
import sys
import asyncio
from random import randint
from websockets import connect
from websockets.exceptions import ConnectionClosedError
import json
import concurrent


IPADDR = '192.168.234.34'
PORT = '30011'
# PORT = '30031'
TOKEN = 'HELLO'
UUID = 'magic'
URL = f'ws://{IPADDR}:{PORT}/api?token={TOKEN}&uuid={UUID}'

msgq = {}


class GPSService:
    def __await__(self):
        return self._async_init().__await__()

    async def _async_init(self):
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'], ping_interval=1)
        self.websocket = await self._conn.__aenter__()
        return self

    async def close(self):
        await self._conn.__aexit__(*sys.exc_info())

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def location(self):
        msgid = randint(0, 999999)
        msgq[msgid] = {'request': msgid, 'response': None}
        await self.websocket.send(f'[2,"{msgid}","gps/location",""]')
        return await self.receive()

    async def subscribe(self, event='location'):
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","gps/subscribe",{{"value": "{event}"}}]'
        await self.send(msg)

async def main():
    gpss = await GPSService()
    try:
        await gpss.subscribe()
        data = await gpss.receive()
        data = await gpss.receive()
        data = await gpss.receive()
        data = await gpss.receive()
        print(data)

    except ConnectionClosedError as e:
        print(e)

    finally:
        await gpss.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())