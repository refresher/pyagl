from aglbaseservice import AGLBaseService, AFBResponse
import asyncio
import os

Verbs = ['subscribe', 'unsubscribe', 'managed_objects', 'adapter_state', 'default_adapter', 'avrcp_controls',
         'connect', 'disconnect', 'pair', 'cancel_pairing', 'confirm_pairing', 'remove_device']
AdapterStateParams = ['discovery', 'discoverable', 'powered', ]

BTEventType = ['adapter_changes', 'device_changes', 'media', 'agent']


class BluetoothService(AGLBaseService):
    service = 'agl-service-bluetooth'
    parser = AGLBaseService.getparser()
    parser.add_argument('--default_adapter', help='Get default bluetooth adapter', action='store_true')
    parser.add_argument('--managed_objects', help='Get managed objects', action='store_true')
    parser.add_argument('--adapter', help='Select remote adapter', required=False, default='hci0')
    parser.add_argument('--adapter_state')
    parser.add_argument('--connect', help='Connect to device', metavar='dev_88_0F_10_96_D3_20')
    parser.add_argument('--disconnect', help='Disconnect from device', metavar='dev_88_0F_10_96_D3_20')
    parser.add_argument('--pair', help='Pair with a device', metavar='dev_88_0F_10_96_D3_20')
    parser.add_argument('--cancel_pairing', help='Cancel ongoing pairing')
    parser.add_argument('--confirm_pairing', metavar='pincode')
    parser.add_argument('--remove_device', metavar='dev_88_0F_10_96_D3_20', help='Remove paired device')



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
    args = BluetoothService.parser.parse_args()
    bts = await BluetoothService(ip=args.ipaddr, port=args.port)

    if args.default_adapter:
        id = await bts.default_adapter()
        print(f'Requesting default adapter with id {id}')
        r = AFBResponse(await bts.response())
        print(r)

    if args.adapter_state:
        pass

    if args.listener:
        for response in bts.listener():
            print(response)

    bts.logger.debug(await bts.adapter_state('hci0', {'uuids': ['0000110e-0000-1000-8000-00805f9b34fb']}))


    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
