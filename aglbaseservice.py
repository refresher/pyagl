from enum import IntEnum
import json
from json import JSONDecodeError
from random import randint
import sys
import asyncio
from random import randint
from websockets import connect
from os import environ
from argparse import ArgumentParser


IPADDR = '127.0.0.1'
PORT = '30000'
TOKEN = 'HELLO'
UUID = 'magic'
URL = f'ws://{IPADDR}:{PORT}/api?token={TOKEN}&uuid={UUID}'

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

    def __init__(self, api, ip, port, url=None, token='HELLO', uuid='magic'):
        self.api = api
        self.url = url
        self.ip = ip
        self.port = port
        self.token = token
        self.uuid = uuid

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

    async def subscribe(self, event):
        msgid = randint(0, 999999)
        msg = f'["{AFBT.REQUEST}","{msgid}","{self.api}/subscribe",{{"value": "{event}"}}]'
        await self.send(msg)

    async def unsubscribe(self, event):
        verb = 'unsubscribe'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",{{"value": "{event}"}}]'
        addrequest(msgid, msg)
        await self.send(msg)
