import asyncio
from random import randint
from aglbaseservice import AGLBaseService


class GeoClueService(AGLBaseService):
    def __init__(self, ip, port=None, api='geoclue', service='agl-service-geoclue'):
        super().__init__(ip=ip, port=port, api=api, service=service)

    async def location(self, waitresponse=False):
        return await self.request('location', waitresponse=waitresponse)
        # verb = 'location'
        # msgid = randint(0, 999999)
        #
        # await self.send(f'[2,"{msgid}","{self.api}/{verb}",""]')
        # return await self.receive()

    async def subscribe(self, event='location'):
        super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        super().unsubscribe(event=event)


async def main(loop):
    GCS = await GeoClueService(ip='192.168.128.13')
    print(await GCS.location())
    listener = loop.create_task(GCS.listener())
    await listener


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
