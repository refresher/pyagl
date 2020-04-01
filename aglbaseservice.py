from enum import IntEnum
import json
from json import JSONDecodeError
from random import randint
import sys
import asyncio
from random import randint
from websockets import connect
import logging
import asyncssh

from typing import Union

class AFBT(IntEnum):
    REQUEST = 2,
    RESPONSE = 3,
    ERROR = 4,
    EVENT = 5

msgq = {}

def addrequest(msgid, msg):
    msgq[msgid] = {'request': msg, 'response': None}

def addresponse(msgid, msg):
    if msgid in msgq.keys():
        msgq[msgid]['response'] = msg

class AGLBaseService:
    api = None
    url = None
    ip = None
    port = None
    token = None
    uuid = None
    service = None

    def __init__(self, api: str, ip: str, port: str, url: str = None,
                 token: str = 'HELLO', uuid: str = 'magic', service: str = None):
        self.api = api
        self.url = url
        self.ip = ip
        self.port = port
        self.token = token
        self.uuid = uuid
        self.service = service

    def __await__(self):
        return self._async_init().__await__()

    async def __aenter__(self):
        return self._async_init()

    async def _async_init(self):
        # setting ping_interval to None because AFB does not support websocket ping
        # if set to !None, the library will close the socket after the default timeout
        URL = f'ws://{self.ip}:{self.port}/api?token={self.token}&uuid={self.uuid}'
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'], ping_interval=None)
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def close(self):
        await self._conn.__aexit__(*sys.exc_info())

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def portfinder(self):
        with asyncssh.connect(self.ip) as c:
            data = await c.run('ls -lah /', check=True)
            print(data)

    async def listener(self):
        try:
            while True:
                msg = await self.receive()
                print(f"Received {msg}")
                try:
                    data = json.loads(msg)
                    if isinstance(data, list):
                        if data[0] == AFBT.RESPONSE and str.isnumeric(data[1]):
                            msgid = int(data[1])
                            if msgid in msgq:
                                addresponse(msgid, data)

                except JSONDecodeError:
                    print("Not decoding a non-json message")

        except KeyboardInterrupt:
            print("Received keyboard interrupt, exiting")
        except asyncio.CancelledError:
            print("Websocket listener coroutine stopped")
        except Exception as e:
            print("vote du phoque?!?!? : " + str(e))

    async def request(self,
                      verb: str,
                      values: Union[str, dict] = "",
                      msgid: int = randint(0, 9999999),
                      waitresponse: bool = False):
        l = json.dumps([AFBT.REQUEST, str(msgid), f'{self.api}/{verb}', values])
        await self.send(l)
        if waitresponse:
            return await self.receive()

    async def subscribe(self, event):
        await self.request('subscribe', {'value': f'{event}'})

    async def unsubscribe(self, event):
        await self.request('unsubscribe', {'value': f'{event}'})
