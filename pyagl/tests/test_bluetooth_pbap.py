import asyncio
import os
import pytest
import logging

from pyagl.services.base import AFBResponse, AFBT
from pyagl.services.bluetooth_pbap import BTPBAPService as PBAP

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope='module')
async def service():
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    port = os.environ.get('AGL_TGT_PORT', None)

    ams = await PBAP(ip=address, port=port)
    yield ams
    await ams.websocket.close()

@pytest.fixture(scope='module')
def searchvcf():
    vcf = os.environ.get('AGL_PBAP_VCF')
    if not vcf:
        pytest.xfail('Please export AGL_PBAP_VCF with an existing .vcf string e.g. 63602.vcf')

    return vcf


@pytest.mark.dependency
async def test_status(event_loop, service: PBAP):
    msgid = await service.status()
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert isinstance(resp.data, dict)
    assert 'connected' in resp.data
    if not resp.data['connected']:
        pytest.xfail('BT PBAP is not currently connected to the phone')
    assert resp.data['connected'] is True


async def test_search(event_loop, service: PBAP):
    msgid = await service.search("+359887224379")
    resp = await service.afbresponse()
    assert resp.status == 'success'


@pytest.mark.dependency(depends=['test_status'])
async def test_import_contacts(event_loop, service: PBAP):
    msgid = await service.import_contacts()
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    assert isinstance(resp.data['vcards'], list)
    vcards = resp.data['vcards']
    assert len(vcards) > 0
    print(f' import verb from OBEX returned {len(vcards)} .vcf objects ')


@pytest.mark.dependency(depends=['test_import_contacts'])
async def test_contacts(event_loop, service: PBAP):
    msgid = await service.contacts()
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    assert isinstance(resp.data['vcards'], list)
    vcards = resp.data['vcards']
    assert len(vcards) > 0
    print(f' contacts verb returned {len(vcards)} cached .vcf objects ')

@pytest.mark.dependency(depends=['test_contacts'])
async def test_history_incoming_calls(event_loop, service: PBAP):
    msgid = await service.history(param='ich')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0

@pytest.mark.dependency(depends=['test_contacts'])
async def test_history_outgoing_calls(event_loop, service: PBAP):
    msgid = await service.history(param='och')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0

@pytest.mark.dependency(depends=['test_contacts'])
async def test_history_missed_calls(event_loop, service: PBAP):
    msgid = await service.history(param='mch')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0

@pytest.mark.dependency(depends=['test_contacts'])
async def test_history_combined_calls(event_loop, service: PBAP):
    msgid = await service.history(param='cch')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0

@pytest.mark.dependency(depends=['test_contacts'])
async def test_entry_phonebook(event_loop, service: PBAP, searchvcf):
    msgid = await service.entry(handle=searchvcf)
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    assert len(resp.data['vcards']) > 0


@pytest.mark.dependency(depends=['test_contacts'])
async def test_incoming_calls(event_loop, service: PBAP):
    msgid = await service.entry(handle='1.vcf', param='ich')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0


@pytest.mark.dependency(depends=['test_contacts'])
async def test_outgoing_calls(event_loop, service: PBAP):
    msgid = await service.entry(handle='1.vcf', param='och')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0


@pytest.mark.dependency(depends=['test_contacts'])
async def test_missed_calls(event_loop, service: PBAP):
    msgid = await service.entry(handle='1.vcf', param='mch')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0


@pytest.mark.dependency(depends=['test_contacts'])
async def test_combined_calls(event_loop, service: PBAP):
    msgid = await service.entry(handle='1.vcf', param='cch')
    resp = await service.afbresponse()
    assert resp.status == 'success'
    assert 'vcards' in resp.data
    vcards = resp.data['vcards']
    assert len(vcards) > 0

