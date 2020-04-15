import asyncio
import json
import os
from random import randint
from aglbaseservice import AGLBaseService
import logging

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

    async def managed_objects(self, waitresponse=False):
        return await self.request('managed_objects', waitresponse=waitresponse)

    async def adapter_state(self, adapter=None, value=None, waitresponse=False):
        p = {}
        if adapter:
            p = {'adapter': adapter}
            if isinstance(value, dict):
                p = {**p, **value}

        return await self.request('adapter_state', p, waitresponse=waitresponse)
        if waitresponse:
            return await self.request('adapter_state', p)
        else:
            await self.request('adapter_state', p)

    async def default_adapter(self):
        verb = 'default_adapter'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",""]'
        # print(msg)
        await self.send(msg)
        return await self.receive()

    async def avrcp_controls(self):
        pass

    async def connect(self, device):
        verb = 'connect'
        msgid = randint(0, 999999)
        d = {'device': device}
        msg = f'[2,"{msgid}","{self.api}/{verb}","{json.dumps(d)}"]'

    async def disconnect(self, device):
        verb = 'disconnect'
        msgid = randint(0, 999999)
        d = {'device': device}
        msg = f'[2,"{msgid}","{self.api}/{verb}","{json.dumps(d)}"]'

    async def pair(self, device):
        verb = 'pair'
        msgid = randint(0, 999999)
        d = {'device': device}
        msg = f'[2,"{msgid}","{self.api}/{verb}","{json.dumps(d)}"]'

    async def cancel_pairing(self):
        verb = 'cancel_pairing'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",""]'

    async def confirm_pairing(self, pincode):
        verb = 'confirm_pairing'
        msgid = randint(0, 999999)
        d = {'pincode': pincode}
        msg = f'[2,"{msgid}","{self.api}/{verb}","{json.dumps(d)}"]'

async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    #port = os.environ.get('AGL_TGT_PORT', '30005')

    BTS = await BluetoothService(ip=addr, port=port)
    print(await BTS.adapter_state('hci1', {'uuids': ['0000110e-0000-1000-8000-00805f9b34fb']}))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))