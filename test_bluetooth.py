import asyncio
import os
import pytest
from bluetooth import BluetoothService as BTS
import logging
from aglbaseservice import AFBResponse, AFBT

logger = logging.getLogger(f'pytest-{BTS.service}')
logger.setLevel(logging.DEBUG)
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
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


async def test_default_adapter(event_loop, service: BTS):
    id = await service.default_adapter()
    resp = AFBResponse(await service.response())
    assert resp.status == 'success', resp
    assert 'adapter' in resp.data.keys()
    assert resp.data['adapter'] == 'hci0'


async def test_managed_objects(event_loop, service: BTS):
    id = await service.managed_objects()
    resp = AFBResponse(await service.response())
    assert resp.status == 'success', str(resp)


async def test_has_single_adapter(event_loop, service: BTS):
    id = await service.managed_objects()
    resp = AFBResponse(await service.response())
    assert len(resp.data['adapters']) == 1, \
        f'Detected {len(resp.data["adapters"])} adapters. Multiple adapters may also break testing'


