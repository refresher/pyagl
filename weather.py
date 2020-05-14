import asyncio
from random import randint
import json
from aglbaseservice import AGLBaseService
msgq = {}


class WeatherService(AGLBaseService):
    service = 'agl-service-weather'
    parser = AGLBaseService.getparser()
    parser.add_argument('--apikey', default=False, help='Request weather API Key', action='store_true')

    def __init__(self, ip, port=None):
        super().__init__(api='weather', ip=ip, port=port, service='agl-service-weather')

    async def apikey(self):
        return await self.request('api_key', "")


async def main():
    args = WeatherService.parser.parse_args()
    ws = await WeatherService(ip=args.ipaddr)
    if args.apikey:
        id = await ws.apikey()
        resp = await ws.response()
        print(resp[2]['response']['api_key'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())