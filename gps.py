import asyncio
import os
import re
from socket import htons
import asyncssh
from aglbaseservice import AGLBaseService
import collections
from collections import namedtuple
from parse import *

class GPSService(AGLBaseService):
    def __init__(self, ip, port):
        super().__init__(api='gps', ip=ip, port=port, service='agl-service-gps')

    async def location(self):
        return await self.request('location',waitresponse=True)

    async def subscribe(self, event='location'):
        await super().subscribe(event=event)

    async def unsubscribe(self, event='location'):
        await super().subscribe(event=event)


async def main(loop):
    addr = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', '30011')

    # gpss = await GPSService(ip=addr, port=port)
    async with asyncssh.connect(addr,username='root') as c:
        # find the name of the service since it is dynamically generated every time
        servicename = await c.run(f"systemctl | grep agl-service-gps | awk '{{print $1}}'", check=False)
        print(f"Found service name: {servicename.stdout}")

        # get the pid
        pid = await c.run(f'systemctl show --property MainPID --value {servicename.stdout}')
        print(f'Service PID: {pid.stdout}')

        # get all sockets in the process' fd directory and their respective inodes
        sockets = await c.run(f'find /proc/{pid.stdout.strip()}/fd/ | xargs readlink | grep socket')
        inodes = re.findall('socket:\[(.*)\]', sockets.stdout)
        print(f"Socket inodes: {inodes}")

        alltcp = await c.run('cat /proc/net/tcp')
        fieldsstr = ' '.join(alltcp.stdout.strip().splitlines()[0].strip().split()) + ' misc'
        # https://www.kernel.org/doc/Documentation/networking/proc_net_tcp.txt
        # ['sl', 'local_address', 'rem_address', 'st', 'tx_queue:rx_queue', 'tr:tm->when',  'retrnsmt', 'uid', 'timeout',  'inode', 'sref_cnt', 'memloc',         'rto', 'pred_sclk', 'ackquick', 'congest', 'slowstart' ]
        #  '0:    00000000:753E    00000000:0000  0A    00000000:00000000    00:00000000     00000000    1001   0           20062    1           0000000095c038d6  100    0            0           10         0'
        # {'sl':'0', # connection state
        #  'local_address': '00000000:753E',
        #  'rem_address':'00000000:0000',
        #  'st':'0A',
        #  'tx_queue':'00000000:00000000',
        #  'rx_queue':'00:00000000',
        #  'tr':'00000000', 'tm->when':'1001', 'retrnsmt': '0',
        # '20062 1 0000000095c038d6 100 0 0 10 0
        fields = fieldsstr.split()

        tcpsockets = alltcp.stdout.splitlines()[1:]
        print(tcpsockets)

        # print(' '.join(alltcp.stdout.strip().splitlines()[1].strip().split()))
        # result = findall('{}: {}:{} {} {} {} {} {} {} ')

        # serviceport = await c.run(f'journalctl -u {servicename.stdout}')
        # print(serviceport.stdout)
        # matches = re.findall('Listening interface \*:(.*) \[',serviceport.stdout)
        # print(matches)

    # print(await gpss.location())

    # listener = loop.create_task(gpss.listener())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))