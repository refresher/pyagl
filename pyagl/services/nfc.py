from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio

class NFCService(AGLBaseService):
    service = 'agl-service-nfc'
    parser = AGLBaseService.getparser()

    def __init__(self, ip, port=None, api='nfc'):
        super().__init__(ip=ip, port=port, api=api, service='agl-service-nfc')

    async def subscribe(self, event='presence'):
        return await super().subscribe(event=event)

    async def unsubscribe(self, event='presence'):
        return await super().unsubscribe(event=event)


async def main(loop):
    args = NFCService.parser.parse_args()
    nfcs = await NFCService(ip=args.ipaddr, port=args.port)

    if args.subscribe:
        for event in args.subscribe:
            msgid = await nfcs.subscribe(event)
            print(f"Subscribing for event {event} with messageid {msgid}")
            r = AFBResponse(await nfcs.response())
            print(r)

    if args.unsubscribe:
        for event in args.unsubscribe:
            msgid = await nfcs.unsubscribe(event)
            print(f"Unsubscribing for event {event} with messageid {msgid}")
            r = AFBResponse(await nfcs.response())
            print(r)

    if args.listener:
        async for response in nfcs.listener():
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
