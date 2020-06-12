import asyncio
import json
from aglbaseservice import AGLBaseService, AFBResponse


class WeatherService(AGLBaseService):
    service = 'agl-service-weather'
    parser = AGLBaseService.getparser()
    parser.add_argument('--current', default=True, help='Request current weather state', action='store_true')
    parser.add_argument('--apikey', default=False, help='Request weather API Key', action='store_true')

    def __init__(self, ip, port=None):
        super().__init__(api='weather', ip=ip, port=port, service='agl-service-weather')

    async def current_weather(self):
        return await self.request('current_weather', "")

    async def apikey(self):
        return await self.request('api_key', "")


async def main():
    args = WeatherService.parser.parse_args()
    aws = await WeatherService(ip=args.ipaddr, port=args.port)
    if args.current:
        id = await aws.current_weather()
        resp = AFBResponse(await aws.response())
        print(json.dumps(resp.data, indent=2))

    if args.apikey:
        id = await aws.apikey()
        resp = AFBResponse(await aws.response())
        print(resp.data['api_key'])

    if args.subscribe:
        for event in args.subscribe:
            id = await aws.subscribe(event)
            print(f'Subscribed for event {event} with messageid {id}')
            resp = AFBResponse(await aws.response())
            print(resp)

    if args.listener:
        async for response in aws.listener():
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
