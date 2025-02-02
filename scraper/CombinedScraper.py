import asyncio
import logging
import threading
from threading import Event
from time import sleep

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter
from scraper.GPWListScraper import GPWListScraper


class CombinedScraper:
    def __init__(self, exit_event: Event):
        self.database_handler = None
        self.exit_event = exit_event
        self.client = httpx.AsyncClient()

    def set_database_handler(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler

    def start(self):
        gpw_limiter = AsyncRateLimiter('gpwcatalyst.pl')

        scrappers = [
            GPWListScraper(self.client, self.database_handler, gpw_limiter, self.exit_event)
        ]

        threads = [
            threading.Thread(target=asyncio.run, args=(scrapper.run(),) , name=f'{scrapper.__class__.__name__} {i}')
            for i, scrapper in enumerate(scrappers)
        ]

        for thread in threads:
            thread.start()
            logging.debug(f'{thread.name} started')

        [asyncio.run(scrappers[0].put_todo(item)) for item in [
            'obligacje-korporacyjne',
            #'obligacje-spoldzielcze',
            #'listy-zastawne',
            #'obligacje-komunalne',
            #'obligacje-skarbowe'
        ]]

        while not self.exit_event.is_set() and any([scrapper.is_working() for scrapper in scrappers]):
            sleep(1)

        self.exit_event.set()

        for thread in threads:
            thread.join()
            logging.debug(f'{thread.name} joined')