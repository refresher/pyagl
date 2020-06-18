from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio
import os


class GeoClueService(AGLBaseService):
    service = 'agl-service-geoclue'
    parser = AGLBaseService.getparser()
    parser.add_argument('--location', help='Get current location', action='store_true')

    def __init__(self, ip, port=None, api='geoclue'):
        super().__init__(ip=ip, port=port, api=api, service='agl-service-geoclue')

    async def location(self):
        return await self.request('location')

    async def subscribe(self, event='location'):
        return await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        return await super().unsubscribe(event=event)


async def main(loop):
    args = GeoClueService.parser.parse_args()
    gcs = await GeoClueService(args.ipaddr)

    if args.location:
        msgid = await gcs.location()
        print(f'Sent location request with messageid {msgid}')
        print(AFBResponse(await gcs.response()))

    if args.subscribe:
        for event in args.subscribe:
            msgid = await gcs.subscribe(event)
            print(f"Subscribed for {event} with messageid {msgid}")
            print(AFBResponse(await gcs.response()))
    if args.listener:
        async for response in gcs.listener():
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
