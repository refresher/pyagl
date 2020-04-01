import json
from json import JSONDecodeError
import os
import sys
import asyncio
from random import randint

from websockets import connect, ConnectionClosedError
import concurrent
from enum import IntEnum
from aglbaseservice import AGLBaseService

global DEBUG
DEBUG = True


class MediaPlayerService(AGLBaseService):
    def __await__(self):
        return super()._async_init().__await__()

    def __init__(self, ip, port):
        super().__init__(api='mediaplayer', ip=ip, port=port)

    async def playlist(self):
        self.request('playlist')
        verb = 'playlist'
        msgid = randint(0, 999999)

        await self.send(f'[2,"{msgid}","{self.api}/{verb}",""]')

    async def subscribe(self, event='metadata'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='metadata'):
        await super().subscribe(event=event)

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

        await self.send(msg)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', '192.168.234.202')
    port = os.environ.get('AGL_TGT_PORT', '30016')

    MPS = await MediaPlayerService(ip=addr, port=port)
    listener = loop.create_task(MPS.listener())
    try:
        await MPS.subscribe('metadata')
        await MPS.control('next')

        await listener

    except KeyboardInterrupt:
        pass

    listener.cancel()
    await MPS.unsubscribe('playlist')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
