import asyncio
import os
import pytest
import urllib3
import logging
from pyagl.services.base import AFBResponse, AFBT
from pyagl.services.weather import WeatherService as ws

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.fixture(scope='module')
async def service():
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', None)
    gpss = await ws(ip=address, port=port)
    yield gpss
    await gpss.websocket.close()

async def test_apikey(event_loop, service: ws):
    msgid = await service.apikey()
    resp = await service.afbresponse()
    assert resp.msgid == msgid
    assert resp.data['api_key'] == 'a860fa437924aec3d0360cc749e25f0e'

async def test_current_weather(event_loop, service: ws):
    msgid = await service.current_weather()
    resp = await service.afbresponse()
    assert resp.msgid == msgid
    assert 'sys' in resp.data

