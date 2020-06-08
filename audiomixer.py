from aglbaseservice import AGLBaseService, AFBResponse
import asyncio
import os

verbs = ['subscribe', 'unsubscribe', 'list_controls', 'volume', 'mute']
events = ['volume_changed', 'mute_changed', 'controls_changed']


class AudioMixerService(AGLBaseService):
    service = 'agl-service-audiomixer'
    parser = AGLBaseService.getparser()
    parser.add_argument('--list_controls', default=True, help='Request list of controls', action='store_true')
    parser.add_argument('--getmute', help='Get mute state', action='store_true')
    parser.add_argument('--setmute', help='Set mute state', type=int, choices=[0, 1])
    parser.add_argument('--setvolume', help='Set volume level', type=float)
    parser.add_argument('--getvolume', help='Get volume level', action='store_true')


    def __init__(self, ip, port=None, service='agl-service-audiomixer'):
        super().__init__(api='audiomixer', ip=ip, port=port, service=service)

    async def subscribe(self, event='volume_changed'):  # audio mixer uses 'event' instead 'value',
        return await self.request('subscribe', {'event': event})

    async def unsubscribe(self, event='volume_changed'):
        return await self.request('unsubscribe', {'event': event})

    async def list_controls(self):
        return await self.request('list_controls')

    async def volume(self, value=None):
        if value is not None:
            return await self.request('volume', {'control': 'Master', 'value': value})
        else:
            return await self.request('volume', {'control': 'Master'})

    async def mute(self, value=None):
        return await self.request('mute', {'control': 'Master', 'value': value})


async def main():
    args = AudioMixerService.parser.parse_args()
    ams = await AudioMixerService(ip=args.ipaddr, port=args.port)

    if args.list_controls:
        resp = await ams.list_controls()
        print(f'Requesting list_controls with id {resp}')
        r = AFBResponse(await ams.response())
        print(r)

    if args.setvolume is not None:
        resp = await ams.volume(args.setvolume)
        print(f'Setting volume to {args.setvolume} with id {resp}')
        r = AFBResponse(await ams.response())
        print(r)

    if args.getvolume:
        resp = await ams.volume()
        print(f'Requesting volume with id {resp}')
        r = AFBResponse(await ams.response())
        print(r)

    if args.setmute is not None:
        resp = await ams.mute(args.setmute)
        print(f'Setting mute to {args.setmute} with id {resp}')
        r = AFBResponse(await ams.response())
        print(r)

    if args.getmute:
        resp = await ams.mute()
        r = AFBResponse(await ams.response())
        print(r)

    if args.subscribe:
        for event in args.subscribe:
            id = await ams.subscribe(event)
            print(f'Subscribing to {event} with id {id}')
            r = AFBResponse(await ams.response())
            print(r)

    if args.unsubscribe:
        for event in args.unsubscribe:
            id = await ams.unsubscribe(event)
            print(f'Unsubscribing from {event} with id {id}')
            r = AFBResponse(await ams.response())
            print(r)

    if args.listener:
        async for response in ams.listener():
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
