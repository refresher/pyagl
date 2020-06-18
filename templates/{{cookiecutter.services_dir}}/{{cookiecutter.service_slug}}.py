from pyagl.services.base import AGLBaseService, AFBResponse
import asyncio
import os


class {{cookiecutter.classname}}(AGLBaseService):
    service = '{{cookiecutter.aglsystemdservice}}'
    parser = AGLBaseService.getparser()

    def __init__(self, ip, port=None, service='{{cookiecutter.aglsystemdservice}}'):
        super().__init__(api='{{cookiecutter.api}}', ip=ip, port=port, service=service)
        # more init stuff specific to the new service

async def main(loop):
    args = {{cookiecutter.classname}}.parser.parse_args()
    svc = {{cookiecutter.classname}}(args.ipaddr)

