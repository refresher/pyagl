from aglbaseservice import AGLBaseService, AFBResponse
from typing import Union
import logging
import asyncio
import os

class AFBMediaPlayerResponse(AFBResponse):
    status: str
    info: str
    data = None

    def __init__(self, data: AFBResponse):
        if isinstance(data, list):
            super().__init__(data)
        self.msgid = data.msgid
        self.type = data.type
        self.data = data.data


class MediaPlayerService(AGLBaseService):
    service = 'agl-service-mediaplayer'
    parser = AGLBaseService.getparser()
    parser.add_argument('--playlist', help='Get current playlist', action='store_true')
    parser.add_argument('--control', help='Play/Pause/Previous/Next')
    parser.add_argument('--seek', help='Seek time through audio track', metavar='msec', type=int)
    parser.add_argument('--rewind', help='Rewind time', metavar='msec', type=int)
    parser.add_argument('--fastforward', help='Fast forward time', metavar='msec', type=int)
    parser.add_argument('--picktrack', help='Play specific track in the playlist', metavar='index', type=int)
    parser.add_argument('--volume', help='Volume control - <1-100>', metavar='int')
    parser.add_argument('--loop', help='Set loop state - <off/track/playlist>', metavar='string')
    parser.add_argument('--avrcp', help='AVRCP Controls')
    def __await__(self):
        return super()._async_init().__await__()

    def __init__(self, ip, port=None):
        super().__init__(api='mediaplayer', ip=ip, port=port, service='agl-service-mediaplayer')

    async def playlist(self):
        return await self.request('playlist')

    async def subscribe(self, event='metadata'):
        return await super().subscribe(event=event)

    async def unsubscribe(self, event='metadata'):
        return await super().subscribe(event=event)

    async def control(self, name, value=None):
        loopstate = ['off', 'playlist', 'track']
        avrcp_controls = ['next', 'previous', 'play', 'pause']
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
            'loop': 'state',
            # 'avrcp_controls': 'value'
        }
        assert name in controls.keys(), f'Tried to use non-existent {name} as control for {self.api}'
        msg = None
        if name in ['play', 'pause', 'previous', 'next']:
            msg = {'value': name}
        elif name in ['seek', 'fast-forward', 'rewind']:
            #assert value > 0, "Tried to seek with negative integer"
            msg = {'value': name, controls[name]: str(value)}
        elif name == 'pick-track':
            assert type(value) is int, "Try picking a song with an integer"
            assert value > 0, "Tried to pick a song with a negative integer"
            msg = {'value': name, controls[name]: str(value)}
        elif name == 'volume':
            assert type(value) is int, "Try setting the volume with an integer"
            assert value > 0, "Tried to set the volume with a negative integer, use values betwen 0-100"
            assert value < 100, "Tried to set the volume over 100%, use values betwen 0-100"
            msg = {'value': name, name: str(value)}
        elif name == 'loop':
            assert value in loopstate, f'Tried to set invalid loopstate - {value}, use "off", "playlist" or "track"'
            msg = {'value': name, controls[name]: str(value)}
        # elif name == 'avrcp_controls':
        #     msg = {'value': name, }
        assert msg is not None, "Congratulations, somehow you made an invalid control request"

        return await self.request('controls', msg)


async def main(loop):
    args = MediaPlayerService.parser.parse_args()
    MPS = await MediaPlayerService(ip=args.ipaddr)

    if args.playlist:
        id = await MPS.playlist()
        r = AFBResponse(await MPS.response())
        for l in r.data['list']: print(l)

    if args.control:
        id = await MPS.control(args.control)
        print(f'Sent {args.control} request with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.seek:
        id = await MPS.control('seek', args.seek)
        print(f'Sent seek request to {args.seek} msec with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.fastforward:
        id = await MPS.control('fast-forward', args.fastforward)
        print(f'Sent fast-forward request for {args.fastforward} msec with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.rewind:
        id = await MPS.control('rewind', -args.rewind)
        print(f'Sent rewind request for {args.rewind} msec with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.picktrack:
        id = await MPS.control('pick-track', args.picktrack)
        print(f'Sent pick-track request with index {args.rewind} with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.volume:
        id = await MPS.control('volume', int(args.volume))
        print(f'Sent volume request: {args.rewind} with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    if args.loop:
        id = await MPS.control('loop', args.loop)
        print(f'Sent loop-state request: {args.loop} with messageid {id}')
        r = AFBResponse(await MPS.response())
        print(r)

    # if args.avrcp:
    #     id = await MPS.control('avrcp_controls', args.avrcp)
    #     print(f'Sent AVRCP control request: {args.loop} with messageid {id}')
    #     r = AFBResponse(await MPS.response())
    #     print(r)

    if args.subscribe:
        for event in args.subscribe:
            id = await MPS.subscribe(event)
            print(f"Subscribed for event {event} with messageid {id}")
            r = await MPS.response()
            print(r)

    if args.listener:
        async for response in MPS.listener():
            print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
