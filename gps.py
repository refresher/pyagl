import asyncio
import os
import asyncssh
from aglbaseservice import AGLBaseService
from parse import *
import re

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
    async with asyncssh.connect(addr, username='root') as c:
        # find the name of the service since it is dynamically generated every time
        #TODO CHANGE ME to use the name of the service dynamically after cleaning this crap here
        servicestr = 'agl-service-gps'
        servicename = await c.run(f"systemctl | grep {servicestr} | awk '{{print $1}}'", check=False)

        #TODO decide what to do if the service is not started - scan for disabled units/run service via afm-util
        print(f"Found service name: {servicename.stdout.strip()}")
        # get the pid
        pid = await c.run(f'systemctl show --property MainPID --value {servicename.stdout}')
        print(f'Service PID: {pid.stdout.strip()}')

        # get all sockets in the process' fd directory and their respective inodes
        sockets = await c.run(f'find /proc/{pid.stdout.strip()}/fd/ | xargs readlink | grep socket')
        inodes = frozenset(re.findall('socket:\[(.*)\]', sockets.stdout))

        print(f"Socket inodes: {inodes}")

        alltcp = await c.run('cat /proc/net/tcp')
        # fieldsstr = ' '.join(alltcp.stdout.strip().splitlines()[0].strip().split()) + ' sref_cnt memloc rto pred_sclk ack_quick congest slowstart'

        # https://www.kernel.org/doc/Documentation/networking/proc_net_tcp.txt
        # ['sl', 'local_address', 'rem_address', 'st', 'tx_queue:rx_queue', 'tr:tm->when',  'retrnsmt', 'uid',
        #  '0:    00000000:753E    00000000:0000  0A    00000000:00000000    00:00000000     00000000    1001

        #  'timeout',  'inode', 'sref_cnt', 'memloc',         'rto', 'pred_sclk', 'ackquick', 'congest', 'slowstart' ]
        #   0           20062    1           0000000095c038d6  100    0            0           10         0'
        # fields = fieldsstr.split()

        fieldsstr = '{sl}: {local_address} {rem_address} {st} {tx_queue}:{rx_queue} {tr}:{tmwhen} {retrnsmt} {uid}' \
                    ' {timeout} {inode} {sref_cnt} {memloc} {rto} {pred_sclk} {ackquick} {congest} {slowstart}'
        tcpsockets = [' '.join(l.split()) for l in alltcp.stdout.splitlines()[1:]]

        # seen once an irregular line   "65: 0D80A8C0:D5BE 8410A6BC:0050 06 00000000:00000000 03:000000F8 00000000     0        0 0 3 0000000083dad9fb"
        # parsing could break at some point, because returns None and cannot be parsed

        parsedtcpsockets = [parse(fieldsstr, l) for l in tcpsockets if l is not None]
        socketinodesbythisprocess = [l for l in parsedtcpsockets if l is not None and l.named['inode'] in inodes]
        # got dem sockets
        # expecting >1 because the process could be listening on 8080, all api services' ports are in 30000 port range
        for s in socketinodesbythisprocess:
            _, port = tuple(parse('{}:{}', s['local_address']))
            port = int(port,16)
            if port > 30000:
                print(f'found port {port}')
                break



        #thesocketswearelookingfor = list(filter(lambda x: ( l for l in parsed if l.named['inode'] in inodes), inodes ))

        # result = parse(fieldsstr, l)
        # if isinstance(Result, result):
        #      result.named['inode'] in inodes
        #
        # print(result)

        # print(' '.join(alltcp.stdout.strip().splitlines()[1].strip().split()))
        # result = findall('{}: {}:{} {} {} {} {} {} {} ')

        # serviceport = await c.run(f'journalctl -u {servicename.stdout}')
        # print(serviceport.stdout)
        # matches = re.findall('Listening interface \*:(.*) \[',serviceport.stdout)

    print("breaketh pointeth h're")
    # print(await gpss.location())

    # listener = loop.create_task(gpss.listener())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))