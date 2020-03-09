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

import abc
import inspect
# https://stackoverflow.com/questions/47555934/how-require-that-an-abstract-method-is-a-coroutine

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

class AbstractAGLBaseService:
    def __await__(self):
        return self._async_init().__await__()

    async def __aenter__(self):
        return self._async_init()

    async def _async_init(self):
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'])
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
                print(f"received {msg}")
                try:
                    data = json.loads(msg)
                    if isinstance(data,list):
                        if data[0] == AFBT.RESPONSE and str.isnumeric(data[1]):
                            msgid = int(data[1])
                            if msgid in msgq:
                                addresponse(msgid, data)


                except JSONDecodeError:
                    print("not decoding a non-json message")

        except KeyboardInterrupt:
            pass
        except asyncio.CancelledError:
            print("websocket listener coroutine stopped")
