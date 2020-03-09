from random import randint
import sys
import asyncio
from random import randint
from websockets import connect
import json
msgq = {}

IPADDR = '192.168.234.34'
PORT = '30031'
# PORT = '30031'
TOKEN = 'HELLO'
UUID = 'magic'
URL = f'ws://{IPADDR}:{PORT}/api?token={TOKEN}&uuid={UUID}'

class WeatherService:
    def __await__(self):
        return self._async_init().__await__()

    async def _async_init(self):
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'])
        self.websocket = await self._conn.__aenter__()
        return self

    async def close(self):
        await self._conn.__aexit__(*sys.exc_info())

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def apikey(self):
        msgid = randint(0, 999999)
        msgq[msgid] = {'request': msgid, 'response': None}
        await self.websocket.send(message=f'[2,"{msgid}","weather/api_key",""]'.format(str(msgid)))
        return await self.receive()



async def main():
    MPS = await WeatherService()
    try:
        print(json.dumps(json.loads(await MPS.apikey()), indent=4, sort_keys=True))

    finally:
        await MPS.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())