from aglbaseservice import AGLBaseService, AFBResponse
import asyncio
import os

class {{cookiecutter.classname}}(AGLBaseService):

    def __init__(self, ip, port=None, service='{{cookiecutter.aglsystemdservice}}'):
        super().__init__(api='{{cookiecutter.api}}', ip=ip, port=port, service=service)

