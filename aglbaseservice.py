from json import JSONDecodeError
from parse import Result, parse
from websockets import connect
from random import randint
from enum import IntEnum
from typing import Union
import asyncssh
import argparse
import asyncio
import binascii
import logging
import json
import sys
import os
import re

# logging.getLogger('AGLBaseService')
# logging.basicConfig(level=logging.DEBUG)

# AFB message type
class AFBT(IntEnum):
    REQUEST = 2,
    RESPONSE = 3,
    ERROR = 4,
    EVENT = 5

msgq = {}
AFBLEN = 3


def newrand():
    while True:
        bs = os.urandom(5)
        result = bs[0] * bs[1] * bs[2] * bs[3] + bs[4]
        yield result

def addrequest(msgid, msg):
    msgq[msgid] = {'request': msg, 'response': None}

def addresponse(msgid, msg):
    if msgid in msgq.keys():
        msgq[msgid]['response'] = msg

class AFBResponse:
    type: AFBT
    msgid: int
    data: dict
    api: str
    status: str
    info: str

    def __init__(self, data: list):
        if type(data[0]) is not int:
            logging.debug(f'Received a response with non-integer message type {binascii.hexlify(data[0])}')
            raise ValueError('Received a response with non-integer message type')
        if data[0] not in AFBT._value2member_map_:
            raise ValueError(f'Received a response with invalid message type {data[0]}')
        self.type = AFBT(data[0])

        if self.type == AFBT.RESPONSE:
            if 'request' not in data[2]:
                logging.error(f'Received malformed or invalid response without "request" dict - {data}')
            if not str.isnumeric(data[1]):
                raise ValueError(f'Received a response with non-numeric message id {data[1]}')
            else:
                self.msgid = int(data[1])
            self.status = data[2]['request']['status']
            if 'info' in data[2]['request']:
                self.info = data[2]['request']['info']
            if 'response' in data[2]:
                self.data = data[2]['response']

        elif self.type == AFBT.EVENT:
            self.api = data[1]
            if 'data' in data[2]:
                self.data = data[2]['data']

        elif self.type == AFBT.ERROR:
            logging.debug(f'AFB returned erroneous response {data}')
            self.msgid = int(data[1])
            self.status = data[2]['request']['status']
            self.info = data[2]['request']['info']
            # raise ValueError(f'AFB returned erroneous response {data}')
        # if 'request' not in data[2] or 'response' not in data[2]:

        if 'response' in data[2]:
            self.data = data[2]['response']

    def __str__(self):  # for debugging purposes
        if self.type == AFBT.EVENT:
            return f'[{self.type.name}][{self.api}][Data: {self.data if hasattr(self, "data") else None}]'
        else:
            return f'[{self.type.name}][Status: {self.status}][{self.msgid}]' \
                   f'[Info: {self.info if hasattr(self,"info") else None}]' \
                   f'[Data: {self.data if hasattr(self, "data") else None}]'


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
        parser = argparse.ArgumentParser(description='Utility to interact with agl-service-* via it\'s websocket')
        parser.add_argument('-l', '--loglevel', help='Level of logging verbosity', default='INFO',
                            choices=list(logging._nameToLevel.keys()))
        parser.add_argument('ipaddr', default=os.environ.get('AGL_TGT_IP', 'localhost'), help='AGL host address')
        parser.add_argument('--port', default=os.environ.get('AGL_TGT_PORT', None), help=f'AGL service websocket port')
        parser.add_argument('--listener', default=False, help='Register a listener for incoming events', action='store_true')
        parser.add_argument('--subscribe', type=str, help='Subscribe to event type', action='append', metavar='event')
        parser.add_argument('--unsubscribe', type=str, help='Unsubscribe from event type', action='append', metavar='event')
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
        self._conn = connect(close_timeout=0, uri=URL, subprotocols=['x-afb-ws-json1'], ping_timeout=None, compression=None)
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
            inodes = frozenset(re.findall("socket:\\[(.*)\\]", sockets.stdout))
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
            raw = await self.response()
            data = AFBResponse(raw)
            if stdout: print(data)
            yield data

    async def response(self):
        try:
            msg = await self.websocket.recv()
            try:
                data = json.loads(msg)
                self.logger.debug('[AGL] -> ' + msg)
                if isinstance(data, list):
                    # check whether the received response is an answer to previous query and queue it for debugging
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

    async def request(self, verb: str, values: Union[str, dict] = "", msgid: int = None):
        msgid = next(newrand()) if msgid is None else msgid
        l = json.dumps([AFBT.REQUEST, str(msgid), f'{self.api}/{verb}', values])
        self.logger.debug(f'[AGL] <- {l}')
        await self.send(l)
        return msgid

    async def subscribe(self, event):
        return await self.request('subscribe', {'value': f'{event}'})  # some services may use 'event' instead 'value'

    async def unsubscribe(self, event):
        return await self.request('unsubscribe', {'value': f'{event}'})
