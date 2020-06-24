from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio
import os

class BTMAPService(AGLBaseService):
    service = 'agl-service-bluetooth-map'
    parser = AGLBaseService.getparser()
    parser.add_argument('--compose', help='Compose text message to a recipient', action='store_true')
    parser.add_argument('--recipient', help='Recipient for composing a message')
    parser.add_argument('--message', help='Message to send to the recipient')
    parser.add_argument('--list_messages', help='List text messages over MAP', action='store_true')


    def __init__(self, ip, port=None, service='agl-service-bluetooth-map'):
        super().__init__(api='bluetooth-map', ip=ip, port=port, service=service)

    async def compose(self, recipient, message):
        return await self.request('compose', {'recipient': recipient, 'message': message})

    async def message(self, handle):
        return await self.request('message', {'handle': handle})

    async def list_messages(self, folder='INBOX'):
        return await self.request('list_messages', {'folder': folder})

    async def subscribe(self, event='notification'):
        return await super().subscribe(event)

    async def unsubscribe(self, event='notification'):
        return await super().subscribe(event)

async def main(loop):
    args = BTMAPService.parser.parse_args()
    bmp = await BTMAPService(args.ipaddr)

    if args.compose:
        if 'recipient' not in args or 'message' not in args:
            BTMAPService.parser.error("You have to use both --recipipent and --message in order to compose")
        msgid = await bmp.compose(recipient=args.recipient, message=args.message)
        print(f'Sent compose request [recipient:{args.recipient}][message:{args.message}] with messageid {msgid}')
        resp = await bmp.afbresponse()
        print(resp)

    if args.list_messages:
        msgid = await bmp.list_messages()
        print(f'Sent list_messages request with messageid {msgid}')
        resp = await bmp.afbresponse()
        print(resp)

    if args.subscribe:
        msgid = await bmp.subscribe(args.subscribe)
        print(f'Subscribed for {args.subscribe} with messageid {msgid}')
        resp = await bmp.afbresponse()
        print(resp)

    if args.listener:
        async for response in bmp.listener():
            print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
