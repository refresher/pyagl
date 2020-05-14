import asyncio
import os
import pytest
from gps import GPSService
from concurrent import futures
import logging
from functools import partial


logger = logging.getLogger('pytest-gps')
logger.setLevel(logging.DEBUG)

@pytest.fixture
async def service():
    event_loop = asyncio.get_running_loop()
    address = os.environ.get('AGL_TGT_IP', 'localhost')
    gpss = await GPSService(ip=address)
    # gpss = await GPSService(ip=address)
    yield gpss
    await gpss.websocket.close()

# @pytest.fixture
# async def listener(service):
#     loop = asyncio.get_event_loop()
#     xc = futures.ThreadPoolExecutor(1)
#     l = await loop.run_in_executor(xc, service.listener)
#     while True:
#         try:
#             yield l.__anext__()
#         except RuntimeError:
#             xc.shutdown()
#         except asyncio.CancelledError:
#             logger.warning("Websocket listener coroutine stopped")
#         except Exception as e:
#             logger.error(e)

@pytest.mark.asyncio
async def test_location(event_loop, service):
    await service.location()
    r = await service.response()
    print(r)
    assert True

