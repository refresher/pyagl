from aglbaseservice import AGLBaseService
import asyncio
import os

from concurrent import futures
xc = futures.ThreadPoolExecutor(1)

class GPSService(AGLBaseService):
    service = 'agl-service-gps'
    parser = AGLBaseService.getparser()
    parser.add_argument('--location', help='Query location verb', action='store_true')

    def __init__(self, ip, port=None):
        super().__init__(api='gps', ip=ip, port=port, service='agl-service-gps')

    async def location(self):
        return await self.request('location')

    async def subscribe(self, event='location'):
        return await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        return await super().subscribe(event=event)


async def main(loop):
    args = GPSService.parser.parse_args()
    gpss = await GPSService(args.ipaddr)

    l = await loop.run_in_executor(xc, gpss.listener)
    # print(await r.__anext__())

    if args.loglevel:
        gpss.logger.setLevel(args.loglevel)
    if args.location:
        msgid = await gpss.location()
        print(await gpss.receive())

    if args.subscribe:
        await gpss.subscribe(args.subscribe)

    print(await l.__anext__())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
