from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio
import os


class GPSService(AGLBaseService):
    service = 'agl-service-gps'
    parser = AGLBaseService.getparser()
    parser.add_argument('--record', help='Begin recording verb ')
    parser.add_argument('--location', help='Get current location', action='store_true')

    def __init__(self, ip, port=None):
        super().__init__(api='gps', ip=ip, port=port, service='agl-service-gps')

    async def location(self):
        return await self.request('location')

    async def record(self, state='on'):
        return await self.request('record', {'state': state})

    async def subscribe(self, event='location'):
        return await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        return await super().subscribe(event=event)


async def main(loop):
    args = GPSService.parser.parse_args()
    gpss = await GPSService(ip=args.ipaddr, port=args.port)

    if args.loglevel:
        gpss.logger.setLevel(args.loglevel)

    if args.record:
        msgid = await gpss.record(args.record)
        print(f'Sent gps record request with value {args.record} with messageid {msgid}')
        print(AFBResponse(await gpss.response()))

    if args.location:
        msgid = await gpss.location()
        print(AFBResponse(await gpss.response()))

    if args.subscribe:
        for event in args.subscribe:
            msgid = await gpss.subscribe(event)
            print(f'Subscribed for event {event} with messageid {msgid}')
            print(AFBResponse(await gpss.response()))

    if args.listener:
        async for response in gpss.listener():
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
