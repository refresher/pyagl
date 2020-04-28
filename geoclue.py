from aglbaseservice import AGLBaseService
import asyncio
import os


class GeoClueService(AGLBaseService):
    def __init__(self, ip, port=None, api='geoclue'):
        super().__init__(ip=ip, port=port, api=api, service='agl-service-geoclue')

    async def location(self, waitresponse=False):
        return await self.request('location', waitresponse=waitresponse)

    async def subscribe(self, event='location', waitresponse=False):
        await super().subscribe(event=event, waitresponse=waitresponse)

    async def unsubscribe(self, event='location', waitresponse=False):
        await super().unsubscribe(event=event, waitresponse=waitresponse)


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
