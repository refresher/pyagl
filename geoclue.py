import asyncio
from random import randint
from aglbaseservice import AGLBaseService, AFBT


class GeoClueService(AGLBaseService):
    def __init__(self):
        super().__init__(api='geoclue', ip='192.168.234.202', port='30009')

    async def location(self):
        verb = 'location'
        msgid = randint(0, 999999)

        await self.send(f'[2,"{msgid}","{self.api}/{verb}",""]')
        return await self.receive()

    async def subscribe(self, event='location'):
        super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        super().unsubscribe(event=event)


async def main(loop):
    GCS = await GeoClueService()
    print(await GCS.location())
    listener = loop.create_task(GCS.listener())
    await listener


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
