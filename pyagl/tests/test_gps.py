import asyncio
import os
import pytest
import logging
from pyagl.services.base import AFBResponse, AFBT
from pyagl.services.gps import GPSService as GPS
from concurrent.futures import TimeoutError

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
    gpss = await GPS(ip=address, port=port)
    yield gpss
    await gpss.websocket.close()

# @pytest.fixture(scope='module')
# async def response(event_loop, service):
#     async for _response in service.listener():
#         yield _response

async def test_location_verb(event_loop, service: GPS):
    msgid = await service.location()
    resp = AFBResponse(await service.response())
    assert resp.msgid == msgid

@pytest.mark.xfail  # expecting this to fail because of "No 3D GNSS fix" and GPS is unavailable
async def test_location_result(event_loop, service: GPS):
    msgid = await service.location()
    resp = AFBResponse(await service.response())
    assert resp.status == 'success'

async def test_subscribe_verb(event_loop, service: GPS):
    msgid = await service.subscribe("")
    resp = AFBResponse(await service.response())
    assert resp.msgid == msgid
    assert resp.status == 'success'

async def test_subscribe_location(event_loop, service: GPS):
    msgid = await service.subscribe('location')
    resp = AFBResponse(await service.response())
    assert resp.msgid == msgid
    assert resp.status == 'success'

async def test_unsubscribe(event_loop, service: GPS):
    msgid = await service.unsubscribe('location')
    resp = AFBResponse(await service.response())
    assert resp.msgid == msgid
    assert resp.status == 'success'

@pytest.mark.xfail  # expecting this to fail because of "No 3D GNSS fix" and GPS is unavailable
async def test_location_events(event_loop, service: GPS):
    msgid = await service.subscribe('location')
    resp = AFBResponse(await service.response())
    assert resp.msgid == msgid
    assert resp.status == 'success'  # successful subscription
    try:
        resp = await asyncio.wait_for(service.afbresponse(), 10)
        resp = AFBResponse(resp)
        assert resp.type == AFBT.EVENT, f'Expected EVENT response, got {resp.type.name} instead'
        # TODO one more assert for the actual received event, haven't received a location event yet
    except TimeoutError:
        pytest.xfail("Did not receive location event")


