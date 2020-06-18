import asyncio
import os
import pytest
import logging
from pyagl.services.base import AFBResponse, AFBT
from concurrent.futures import TimeoutError

from pyagl.services.{{cookiecutter.service_slug}} import {{cookiecutter.classname}}
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
    svc = await {{cookiecutter.classname}}(ip=address, port=port)
    yield svc
    await svc.websocket.close()
