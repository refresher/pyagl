from json import JSONDecodeError
from parse import Result, parse
from websockets import connect
from random import randint
from enum import IntEnum
from typing import Union
import asyncssh
import argparse
import asyncio
import logging
import json
import sys
import os
import re
from contextlib import asynccontextmanager

logging.getLogger('AGLBaseService')
logging.basicConfig(level=logging.DEBUG)

class AFBT(IntEnum):
    REQUEST = 2,
    RESPONSE = 3,
    ERROR = 4,
    EVENT = 5

msgq = {}
AFBLEN = 3

def addrequest(msgid, msg):
    msgq[msgid] = {'request': msg, 'response': None}

def addresponse(msgid, msg):
    if msgid in msgq.keys():
        msgq[msgid]['response'] = msg


class AGLBaseService:
    api: str
    url: str
    ip : str
    port = None
    token: str
    uuid: str
    service = None
    logger = None

    @staticmethod
    def getparser():
        parser = argparse.ArgumentParser(description='Utility to interact with agl-service-gps via it\'s websocket')
        parser.add_argument('-l', '--loglevel', help='Level of logging verbosity', default='INFO',
                            choices=list(logging._nameToLevel.keys()))
        parser.add_argument('ipaddr', default=os.environ.get('AGL_TGT_IP', 'localhost'), help='AGL host address')
        parser.add_argument('--port', default=os.environ.get('AGL_TGT_PORT', None), help=f'AGL service websocket port')
        parser.add_argument('--listener', default=False, help='Register a listener for incoming events', action='store_true')
        parser.add_argument('--subscribe', type=str, help='Subscribe to event type', metavar='event')
        parser.add_argument('--unsubscribe', type=str, help='Unsubscribe from event type', metavar='event')
        parser.add_argument('--json', type=str, help='Send your own json string')
        parser.add_argument('--verb', type=str, help='Send the json above to specific verb')
        parser.add_argument('--api', type=str, help='Send the above two to a specific api')
        return parser

    def __init__(self, api: str, ip: str, port: str = None, url: str = None,
                 token: str = 'HELLO', uuid: str = 'magic', service: str = None):
        self.api = api
        self.url = url
        self.ip = ip
        self.port = port
        self.token = token
        self.uuid = uuid
        self.service = service
        self.logger = logging.getLogger(service)

    def __await__(self):
        return self._async_init().__await__()

    async def __aenter__(self):
        return self._async_init()

    async def _async_init(self):
        # setting ping_interval to None because AFB does not support websocket ping
        # if set to !None, the library will close the socket after the default timeout
        if self.port is None:
            serviceport = await self.portfinder()
            if serviceport is not None:
                self.port = serviceport
            else:
                self.logger.error('Unable to find port')
                exit(1)

        URL = f'ws://{self.ip}:{self.port}/api?token={self.token}&uuid={self.uuid}'
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'], ping_interval=None, timeout=2)
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def close(self):
        await self._conn.__aexit__(*sys.exc_info())

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def portfinder(self):
        # TODO:handle ssh timeouts, asyncssh does not support it apparently, and connect returns context_manager which
        # cannot be used with asyncio.wait_for

        async with asyncssh.connect(self.ip, username='root') as c:

            servicename = await c.run(f"systemctl --all | grep {self.service}-- | awk '{{print $1}}'", check=False)
            if self.service not in servicename.stdout:
                logging.error(f"Service matching pattern - '{self.service}' - NOT FOUND")
                exit(1)
            pidres = await c.run(f'systemctl show --property MainPID --value {servicename.stdout.strip()}')
            pid = int(pidres.stdout.strip(), 10)
            if pid is 0:
                logging.warning(f'Service {servicename.stdout.strip()} is stopped')
                return None
            else:
                self.logger.debug(f'Service PID: {str(pid)}')

            sockets = await c.run(f'find /proc/{pid}/fd/ | xargs readlink | grep socket')
            inodes = frozenset(re.findall('socket:\[(.*)\]', sockets.stdout))
            self.logger.debug(f"Socket inodes: {inodes}")

            procnettcp = await c.run('cat /proc/net/tcp')
            fieldsstr = '{sl}: {local_address} {rem_address} {st} {tx_queue}:{rx_queue} {tr}:{tmwhen} {retrnsmt} {uid}'\
                        ' {timeout} {inode} {sref_cnt} {memloc} {rto} {pred_sclk} {ackquick} {congest} {slowstart}'
            tcpsockets = [' '.join(l.split()) for l in procnettcp.stdout.splitlines()[1:]]
            # different lines with less stats appear sometimes, parse will return None, so ignore 'None' lines
            parsedtcpsockets = []
            for l in tcpsockets:
                res = parse(fieldsstr, l)
                if isinstance(res, Result):
                    parsedtcpsockets.append(res)

            socketinodesbythisprocess = [l for l in parsedtcpsockets if
                                         isinstance(l, Result) and
                                         l.named['inode'] in inodes and
                                         # 0A is listening state for the socket
                                         l.named['st'] == '0A']

            for s in socketinodesbythisprocess:
                _, port = tuple(parse('{}:{}', s['local_address']))
                port = int(port, 16)
                if port >= 30000:  # the port is above 30000 range, 8080 is some kind of proxy
                    self.logger.debug(f'Service running at port {port}')
                    return port

    async def listener(self, stdout: bool = False):
        while True:
            data = await self.response()
            if stdout: print(data)
            yield data

    async def response(self):
        try:
            msg = await self.websocket.recv()
            try:
                data = json.loads(msg)
                self.logger.debug('[AGL] -> ' + msg)
                if isinstance(data, list):

                    if len(data) == AFBLEN and data[0] == AFBT.RESPONSE and str.isnumeric(data[1]):
                        msgid = int(data[1])
                        if msgid in msgq:
                            addresponse(msgid, data)
                return data
            except JSONDecodeError:
                self.logger.warning("Not decoding a non-json message")

        except KeyboardInterrupt:
            self.logger.debug("Received keyboard interrupt, exiting")
        except asyncio.CancelledError:
            self.logger.warning("Websocket listener coroutine stopped")
        except Exception as e:
            self.logger.error("Unhandled seal: " + str(e))

    async def request(self, verb: str, values: Union[str, dict] = "", msgid: int = randint(0, 9999999)):
        l = json.dumps([AFBT.REQUEST, str(msgid), f'{self.api}/{verb}', values])
        self.logger.debug(f'[AGL] <- {l}')
        await self.send(l)
        return msgid

    async def subscribe(self, event):
        return await self.request('subscribe', {'value': f'{event}'})

    async def unsubscribe(self, event):
        return await self.request('unsubscribe', {'value': f'{event}'})
