from aglbaseservice import AGLBaseService
import asyncio
import os


class GeoClueService(AGLBaseService):
    def __init__(self, ip, port=None, api='geoclue'):
        super().__init__(ip=ip, port=port, api=api, service='agl-service-geoclue')

    async def location(self):
        return await self.request('location')

    async def subscribe(self, event='location'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        await super().unsubscribe(event=event)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    GCS = await GeoClueService(ip=addr)
    tasks = []
    tasks.append(loop.create_task(GCS.location()))
    tasks.append(loop.create_task(GCS.listener()))
    loop.run_until_complete(tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
