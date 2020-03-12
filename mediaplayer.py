import json
from json import JSONDecodeError
from random import randint
import os
import sys
import asyncio
from random import randint
from websockets import connect, ConnectionClosedError
import concurrent
from enum import IntEnum
from os import environ
from argparse import ArgumentParser
from aglbaseservice import AGLBaseService

URL = f'ws://{os.environ["AGL_TGT_IP"]}:{os.environ.get("AGL_TGT_PORT","30016")}/api?token=HELLO&uuid=magic'

# x-AFB-ws-json1 message Type
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


class MediaPlayerService():
    def __init__(self, ip, port):
        super().__init__(api='mediaplayer', ip=ip, port=port)

    def __init__(self, url=None, api='', ip='127.0.0.1', port='30000', token='HELLO', uuid='magic'):
        self.api = api
        self.url = url
        self.ip = ip
        self.port = port
        self.token = token
        self.uuid = uuid

        # if url is set, disregard other params; if not - construct url
#TODO: finish implementing constructor with params

    def __await__(self):
        return self._async_init().__await__()

    async def __aenter__(self):
        return self._async_init()

    async def _async_init(self):
        self._conn = connect(uri=URL, subprotocols=['x-afb-ws-json1'], close_timeout=0, ping_interval=None)
        self.websocket = await self._conn.__aenter__()
        self.url = URL
        self.api = 'mediaplayer'
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

    async def playlist(self):
        verb = 'playlist'
        msgid = randint(0, 999999)
        addrequest(msgid, msg)
        await self.send(f'[2,"{msgid}","{self.api}/{verb}",""]')

    async def subscribe(self, event='metadata'): # event could also be 'playlist' instead of 'metadata'
        verb = 'subscribe'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",{{"value": "{event}"}}]'
        addrequest(msgid, msg)
        await self.send(msg)

    async def unsubscribe(self, event='metadata'):
        verb = 'unsubscribe'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",{{"value": "{event}"}}]'
        addrequest(msgid, msg)
        await self.send(msg)

    async def control(self, name, value=None):
        verb = 'controls'
        loopstate = ['off', 'playlist', 'track']

        controls = {
            'play': None,
            'pause': None,
            'previous': None,
            'next': None,
            'seek': 'position',
            'fast-forward': 'position',
            'rewind': 'position',
            'pick-track': 'index',
            'volume': 'volume',
            'loop': 'state'
        }
        assert name in controls.keys(), 'Tried to use non-existant {name} as control for {self.api}'

        msgid = randint(0, 999999)
        if name in ['play', 'pause', 'previous', 'next']:
            msg = f'[2,"{msgid}","{self.api}/{verb}", {{"value": "{name}"}}]'
        elif name in ['seek', 'fast-forward', 'rewind']:
            assert value > 0, "Tried to seek with negative integer"
            msg = f'[2,"{msgid}","{self.api}/{verb}", {{"value": "{name}", "position": "{str(value)}"}}]'
        elif name == 'pick-track':
            assert type(value) is int, "Try picking a song with an integer"
            assert value > 0, "Tried to pick a song with a negative integer"
            msg = f'[2,"{msgid}","{self.api}/{verb}", {{"value": "{name}", "index": {str(value)}}}]'
        elif name == 'volume':
            assert type(value) is int, "Try setting the volume with an integer"
            assert value > 0, "Tried to set the volume with a negative integer, use values betwen 0-100"
            assert value < 100, "Tried to set the volume over 100%, use values betwen 0-100"
            msg = f'[2,"{msgid}","{self.api}/{verb}", {{"value": "{name}", "{name}": {str(value)}}}]'
        elif name == 'loop':
            assert value in loopstate, f'Tried to set invalid loopstate - {value}, use "off", "playlist" or "track"'
            msg = f'[2,"{msgid}","{self.api}/{verb}", {{"value": "{name}", "{controls[name]}": {str(value)}}}]'
        addrequest(msgid, msg)

        await self.send(msg)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', '30016')

    MPS = await MediaPlayerService(ip=addr, port=port)
    listener = loop.create_task(MPS.listener())
    try:
        await MPS.subscribe()

        await listener
    except ConnectionClosedError as e:
        print("Connection timed out or closed abnormally. Trying to reconnect...")
        result = await MPS._async_init()
        print(result)
    except KeyboardInterrupt:
        pass

    listener.cancel()
    await MPS.unsubscribe()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
