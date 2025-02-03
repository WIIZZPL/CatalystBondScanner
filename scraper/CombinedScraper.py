import asyncio
import logging
import threading
import tkinter
from time import sleep

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter
from scraper.component_scrappers.GPWBondScraper import GPWBondScraper
from scraper.component_scrappers.GPWListScraper import GPWListScraper


class CombinedScraper:
    def __init__(self):
        self.database_handler = None
        self.exit_event = threading.Event()
        self.client = httpx.AsyncClient()
        self.progress_vars = []

    def set_database_handler(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler

    def start(self):
        self.exit_event.clear()
        gpw_limiter = AsyncRateLimiter('gpwcatalyst.pl')

        scrappers = [
            GPWListScraper(self.client, self.database_handler, gpw_limiter, self.exit_event, self.progress_vars[0]),
            GPWBondScraper(self.client, self.database_handler, gpw_limiter, self.exit_event, self.progress_vars[1])
        ]

        scrappers[0].set_bond_scraper(scrappers[1])

        threads = [
            threading.Thread(target=asyncio.run, args=(scrapper.run(),) , name=f'{scrapper.__class__.__name__} {i}')
            for i, scrapper in enumerate(scrappers)
        ]

        for thread in threads:
            thread.start()
            logging.debug(f'{thread.name} started')

        [asyncio.run(scrappers[0].put_todo(item)) for item in [
            'obligacje-korporacyjne',
            'obligacje-spoldzielcze',
            'listy-zastawne',
            'obligacje-komunalne',
            'obligacje-skarbowe'
        ]]

        while any([scrapper.is_working() for scrapper in scrappers]):
            sleep(1)

        self.exit_event.set()

        for thread in threads:
            thread.join()
            logging.debug(f'{thread.name} joined')

        self.database_handler.update_last_modified_date()

    def set_progress_vars(self, progress_vars: [tkinter.DoubleVar]):
        self.progress_vars = progress_vars