from aglbaseservice import AGLBaseService
import asyncio
import os

Verbs = ['subscribe', 'unsubscribe', 'managed_objects', 'adapter_state', 'default_adapter', 'avrcp_controls',
         'connect', 'disconnect', 'pair', 'cancel_pairing', 'confirm_pairing', 'remove_device']
AdapterStateParams = ['discovery', 'discoverable', 'powered', ]
BTEventType = ['adapter_changes', 'device_changes', 'media', 'agent']


class BluetoothService(AGLBaseService):

    def __init__(self, ip, port=None, service='agl-service-bluetooth'):
        super().__init__(api='Bluetooth-Manager', ip=ip, port=port, service=service)

    async def subscribe(self, event='device_changes'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='device_changes'):
        await super().unsubscribe(event=event)

    async def managed_objects(self):
        return await self.request('managed_objects')

    async def adapter_state(self, adapter=None, value=None):
        p = {}
        if adapter:
            p = {'adapter': adapter}
            if isinstance(value, dict):
                p = {**p, **value}

        return await self.request('adapter_state', p)

    async def default_adapter(self):
        return await self.request('default_adapter', "")

    async def connect(self, device: str = 'hci0'):
        return await self.request('connect', {'device': device})

    async def disconnect(self, device: str = 'hci0'):
        return await self.request('disconnect', {'device': device})

    async def pair(self, device):
        return await self.request('pair', {'device': device})

    async def cancel_pairing(self):
        return await self.request('cancel_pairing')

    async def confirm_pairing(self, pincode):
        return await self.request('confirm_pairing', {'pincode': pincode})

    async def avrcp_controls(self):
        pass

async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', None)
    BTS = await BluetoothService(ip=addr, service='agl-service-bluetooth', port=port)
    listener = loop.create_task(BTS.listener())
    await BTS.subscribe()
    BTS.logger.debug(await BTS.adapter_state('hci0', {'uuids': ['0000110e-0000-1000-8000-00805f9b34fb']}))
    await listener

    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
