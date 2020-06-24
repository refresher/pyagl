import asyncio
import os
import pytest

from pyagl.services.base import AFBResponse, AFBT
from pyagl.services.audiomixer import AudioMixerService as AMS
import logging

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope='module')
async def service():
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', None)

    ams = await AMS(ip=address, port=port)
    yield ams
    await ams.websocket.close()


async def test_list_controls(event_loop, service: AMS):
    msgid = await service.list_controls()
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'


async def test_volume_verb(event_loop, service: AMS):
    msgid = await service.volume()
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'

async def test_set_volume0(event_loop, service: AMS):
    msgid = await service.volume(value=0)
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'

async def test_set_maxvolume(event_loop, service: AMS):
    msgid = await service.volume(value=1)
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'

async def test_get_mute(event_loop, service: AMS):
    msgid = await service.mute()
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'

async def test_set_mute(event_loop, service: AMS):
    msgid = await service.mute(value=1)
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'

async def test_set_unmute(event_loop, service: AMS):
    msgid = await service.mute(value=0)
    resp = await service.afbresponse()
    assert msgid == resp.msgid
    assert resp.type == AFBT.RESPONSE
    assert resp.status == 'success'
