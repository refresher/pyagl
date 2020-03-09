import asyncio
from random import randint
from aglbaseservice import AGLBaseService

Verbs = ['subscribe', 'unsubscribe', 'managed_objects', 'adapter_state', 'default_adapter', 'avrcp_controls',
         'connect', 'disconnect', 'pair', 'cancel_pairing', 'confirm_pairing', 'remove_device']

BTEventType = ['adapter_changes', 'device_changes', 'media', 'agent']

class BluetoothService(AGLBaseService):

    def __init__(self, ip, port):
        super().__init__(api='Bluetooth-Manager', ip=ip, port=port)

    async def subscribe(self, event='location'):
        super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        super().unsubscribe(event=event)

    async def managed_objects(self):
        verb = 'managed_objects'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",""]'
        print(msg)
        await self.send(msg)
        return await self.receive()

    async def adapter_state(self, param = None, value = None):
        verb = 'adapter_state'
        msgid = randint(0, 999999)
        if param:
            p = str({'adapter': param})
            # msg = f'[2,"{msgid}","{self.api}/{verb}","{param}": {value if value is not None else ""}]'
            msg = f'[2,"{msgid}","{self.api}/{verb}", {p}]'
        else:
            msg = f'[2,"{msgid}","{self.api}/{verb}", ""]'

        print(msg)
        await self.send(msg)
        return await self.receive()

    async def default_adapter(self):
        verb = 'default_adapter'
        msgid = randint(0, 999999)
        msg = f'[2,"{msgid}","{self.api}/{verb}",""]'
        print(msg)
        await self.send(msg)
        return await self.receive()

    async def avrcp_controls(self):
        pass


async def main(loop):
    BTS = await BluetoothService(ip='192.168.234.202', port='30005')
    #print(await BTS.managed_objects())
    print(await BTS.adapter_state('hci0', '{"discoverable": true}'))
    await asyncio.sleep(delay=1)
    print(await BTS.adapter_state('hci0'))
    print(await BTS.adapter_state('hci1', '""'))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))