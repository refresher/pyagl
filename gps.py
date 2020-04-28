from aglbaseservice import AGLBaseService
import asyncio
import os


class GPSService(AGLBaseService):
    service = 'agl-service-gps'
    parser = AGLBaseService.getparser()
    parser.add_argument('--location', help='Query location verb', action='store_true')

    def __init__(self, ip, port=None):
        super().__init__(api='gps', ip=ip, port=port, service='agl-service-gps')

    async def location(self, waitresponse=False):
        return await self.request('location', waitresponse=waitresponse)

    async def subscribe(self, event='location', waitresponse=False):
        return await super().subscribe(event=event, waitresponse=waitresponse)

    async def unsubscribe(self, event='location', waitresponse=False):
        return await super().subscribe(event=event, waitresponse=waitresponse)


async def main(loop):
    args = GPSService.parser.parse_args()
    gpss = await GPSService(args.ipaddr)

    if args.loglevel:
        GPSService.logger.setLevel(args.loglevel)
    if args.location:
        print(await gpss.location(waitresponse=True))
    if args.subscribe:
        await gpss.subscribe(args.subscribe)

    await gpss.listener()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
