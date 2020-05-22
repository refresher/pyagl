import asyncio
import os
import pytest
from gps import GPSService
import logging


logger = logging.getLogger('pytest-gps')
logger.setLevel(logging.DEBUG)

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='module')
async def service():
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    gpss = await GPSService(ip=address)
    yield gpss
    await gpss.websocket.close()

@pytest.fixture(scope='module')
async def listener(event_loop, service):
    listener = service.listener()

@pytest.mark.asyncio
async def test_location(event_loop, service: GPSService):
    await service.location()
    resp = await service.response()
    print(resp)
    assert isinstance(resp, list)
    assert resp[2]['request']['status'] == 'success', f"location() returned failure; {resp[2]['request']['info']}"

