import asyncio
import datetime
import threading
from threading import Semaphore
from configparser import ConfigParser
from importlib import resources
from time import sleep


class AsyncRateLimiter:

    def __init__(self, domain :str = 'DEFAULT'):
        self.config_parser = ConfigParser()
        config_file = resources.files(__name__).joinpath('config.ini')
        self.config_parser.read(config_file)

        self.domain = domain
        self.max_connections = None
        self.semaphore = None
        self.timeout = None
        self.last_request_datetime = datetime.datetime.min

        if domain in self.config_parser:
            self.max_connections = int(self.config_parser[domain]['max_connections']) if 'max_connections' in self.config_parser[domain] else None
            self.timeout = datetime.timedelta(seconds=float(self.config_parser[domain]['timeout'])) if 'timeout' in self.config_parser[domain] else None

        if self.semaphore is None:
            self.max_connections = int(self.config_parser['DEFAULT']['max_connections'])
        if self.timeout is None:
            self.timeout = datetime.timedelta(seconds=float(self.config_parser['DEFAULT']['timeout']))

        self.semaphore = Semaphore(self.max_connections)

    def __enter__(self):
        self.semaphore.acquire()

        while True:
            now = datetime.datetime.now()
            delta = now-self.last_request_datetime
            if delta > self.timeout:
                self.last_request_datetime = now
                return
            sleep((self.timeout-delta).total_seconds())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()