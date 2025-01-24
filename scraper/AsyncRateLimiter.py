import asyncio
import datetime
from asyncio import Semaphore
from configparser import ConfigParser
from importlib import resources


class AsyncRateLimiter:

    def __init__(self, domain :str = 'DEFAULT'):
        self.config_parser = ConfigParser()
        config_file = resources.files(__name__).joinpath('config.ini')
        self.config_parser.read(config_file)

        self.domain = domain
        self.semaphore = None
        self.timeout = None
        self.last_request_datetime = datetime.datetime.min

        if domain in self.config_parser:
            self.semaphore = Semaphore(int(self.config_parser[domain]['max_connections'])) if 'max_connections' in self.config_parser[domain] else None
            self.timeout = datetime.timedelta(seconds=float(self.config_parser[domain]['timeout'])) if 'timeout' in self.config_parser[domain] else None

        if self.semaphore is None:
            self.semaphore = Semaphore(int(self.config_parser['DEFAULT']['max_connections']))
        if self.timeout is None:
            self.timeout = datetime.timedelta(seconds=float(self.config_parser['DEFAULT']['timeout']))

    async def __aenter__(self):
        await self.semaphore.acquire()

        while True:
            now = datetime.datetime.now()
            delta = now-self.last_request_datetime
            if delta > self.timeout:
                return
            await asyncio.sleep((self.timeout-delta).total_seconds())

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()