import asyncio
import os
import pytest
from bluetooth import BluetoothService as BTS
import logging
from aglbaseservice import AFBResponse, AFBT

logger = logging.getLogger(f'pytest-{BTS.service}')
logger.setLevel(logging.DEBUG)
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def service():
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', None)

    bts = await BTS(ip=address, port=port)
    yield bts
    await bts.websocket.close()


@pytest.mark.xfail
@pytest.fixture(scope='module')
def btaddr():
    bthtestaddr = os.environ.get('AGL_TEST_BT_ADDR', None)
    if not bthtestaddr:
        pytest.xfail('No test bluetooth test address set in environment variables')

    return bthtestaddr


@pytest.mark.dependency
async def test_default_adapter(event_loop, service: BTS):
    id = await service.default_adapter()
    resp = AFBResponse(await service.response())
    assert resp.status == 'success', resp
    assert 'adapter' in resp.data.keys()
    assert resp.data['adapter'] == 'hci0'


@pytest.mark.dependency(depends=['test_default_adapter'])
async def test_managed_objects(event_loop, service: BTS):
    id = await service.managed_objects()
    resp = AFBResponse(await service.response())
    assert resp.status == 'success', str(resp)


@pytest.mark.dependency(depends=['test_default_adapter'])
async def test_has_single_adapter(event_loop, service: BTS):
    id = await service.managed_objects()
    resp = AFBResponse(await service.response())
    assert len(resp.data['adapters']) == 1, \
        f'Detected {len(resp.data["adapters"])} adapters. Multiple adapters may also break testing'


@pytest.mark.dependency(depends=['test_default_adapter'])
async def test_adapter_state(event_loop, service: BTS):
    id = await service.adapter_state('hci0')
    resp = AFBResponse(await service.response())
    assert resp.status == 'success', 'adapter state verb failed'


async def test_pairing_verb(event_loop, service: BTS, btaddr):
    id = await service.pair(btaddr)
    resp = await service.afbresponse()
    assert id == resp.msgid
    assert resp.status == 'success', f'pair verb failed - {resp.info}'


async def test_connect_verb(event_loop, service: BTS, btaddr):
    id = await service.connect(btaddr)
    resp = await service.afbresponse()
    assert id == resp.msgid
    assert resp.status == 'success', f'connect verb failed - {resp.info}'


async def test_disconnect_verb(event_loop, service: BTS, btaddr):
    id = await service.disconnect(btaddr)
    resp = await service.afbresponse()
    assert id == resp.msgid
    assert resp.status == 'success', f'disconnect verb failed - {resp.info}'


async def test_remove_pairing_verb(event_loop, service: BTS, btaddr):
    id = await service.remove_device(btaddr)
    resp = await service.afbresponse()
    assert id == resp.msgid
    assert resp.status == 'success'


@pytest.mark.xfail(reason='This is expected to fail because there has to be an ongoing pairing attempt')
async def test_confirm_pairing_verb(event_loop, service: BTS, btaddr):
    id = await service.confirm_pairing(pincode='123456')
    resp = await service.afbresponse()
    assert id == resp.msgid
    assert resp.status == 'success', f'confirm_pairing verb failed - {resp.info}'
