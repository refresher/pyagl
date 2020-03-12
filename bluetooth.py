import asyncio
import json
import os
from random import randint
from aglbaseservice import AGLBaseService

Verbs = ['subscribe', 'unsubscribe', 'managed_objects', 'adapter_state', 'default_adapter', 'avrcp_controls',
         'connect', 'disconnect', 'pair', 'cancel_pairing', 'confirm_pairing', 'remove_device']
AdapterStateParams = ['discovery', 'discoverable', 'powered', ]
BTEventType = ['adapter_changes', 'device_changes', 'media', 'agent']

class BluetoothService(AGLBaseService):

    def __init__(self, ip, port):
        super().__init__(api='Bluetooth-Manager', ip=ip, port=port)

    async def subscribe(self, event='device_changes'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='device_changes'):
        await super().unsubscribe(event=event)

    async def managed_objects(self):
        verb = 'managed_objects'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",""]'
        # print(msg)
        await self.send(msg)
        return await self.receive()

    async def adapter_state(self, param=None, value=None):
        verb = 'adapter_state'
        msgid = randint(0, 999999)
        if param:
            p = {'adapter': param}
            if isinstance(value, dict):
                p = {**p, **value}

            # msg = f'[2,"{msgid}","{self.api}/{verb}","{param}": {value if value is not None else ""}]'
            msg = f'[2,"{msgid}","{self.api}/{verb}", {json.dumps(p)}]'
        else:
            msg = f'[2,"{msgid}","{self.api}/{verb}", ""]'

        print(msg)
        await self.send(msg)
        return await self.receive()

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
    port = os.environ.get('AGL_TGT_PORT', '30005')

    BTS = await BluetoothService(ip=addr, port=port)
    print(await BTS.adapter_state('hci1', {'uuids': ['0000110e-0000-1000-8000-00805f9b34fb']}))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))