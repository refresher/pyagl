from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio
import os

class BTPBAPService(AGLBaseService):
    service = 'agl-service-bluetooth-pbap'
    parser = AGLBaseService.getparser()

    def __init__(self, ip, port=None, service='agl-service-bluetooth-pbap'):
        super().__init__(api='bluetooth-pbap', ip=ip, port=port, service=service)

    async def subscribe(self, event='status'):
        return await super().subscribe(event)

    async def unsubscribe(self, event='status'):
        return await super().subscribe(event)

    async def import_contacts(self):
        return await super().request('import')

    async def status(self):
        return await super().request('status')

    async def contacts(self):
        return await super().request('contacts')

    async def entry(self, handle, param='pb'):
        return await super().request('entry', {'list': param, 'handle': handle})

    async def search(self, number):
        return await super().request('search', {'number': number})

    async def history(self, param):
        return await super().request('history', {'list': param})

