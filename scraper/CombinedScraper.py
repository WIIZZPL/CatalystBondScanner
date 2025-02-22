import logging
import threading
import tkinter
from time import sleep

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter
from scraper.component_scrappers.GPWBondScraper import GPWBondScraper
from scraper.component_scrappers.GPWListScraper import GPWListScraper
from scraper.component_scrappers.ObligacjeBondScraper import ObligacjeBondScraper
from scraper.component_scrappers.StockwatchIssuerBondScraper import StockwatchIssuerBondScraper
from scraper.component_scrappers.StockwatchIssuerFinanceScraper import StockwatchIssuerFinanceScraper
from scraper.component_scrappers.StockwatchIssuerListScraper import StockwatchIssuerListScraper


class CombinedScraper:
    def __init__(self):
        self.database_handler :DatabaseHandler = None
        self.exit_event = threading.Event()
        self.client = httpx.Client(headers={
            'Connection': 'close',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3'
        })
        self.progress_vars = {}

    def set_database_handler(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler

    def start(self):
        self.exit_event.clear()
        gpw_limiter = AsyncRateLimiter('gpwcatalyst.pl')
        obligacje_limiter = AsyncRateLimiter('obligacje.pl')
        #stockwatch_limiter = AsyncRateLimiter('stockwatch.pl')

        scrappers = [
            GPWListScraper(self.client, self.database_handler, gpw_limiter, self.exit_event, self.progress_vars['GPW_bond_list']),
            GPWBondScraper(self.client, self.database_handler, gpw_limiter, self.exit_event, self.progress_vars['GPW_bond_detail']),
            ObligacjeBondScraper(self.client, self.database_handler, obligacje_limiter, self.exit_event, self.progress_vars['Obligacje_bond_detail']),
            #StockwatchIssuerListScraper(self.client, self.database_handler, stockwatch_limiter, self.exit_event, self.progress_vars['StockWatch_issuer_list']),
            #StockwatchIssuerBondScraper(self.client, self.database_handler, stockwatch_limiter, self.exit_event, self.progress_vars['StockWatch_issuer_bond']),
            #StockwatchIssuerFinanceScraper(self.client, self.database_handler, stockwatch_limiter, self.exit_event, self.progress_vars['StockWatch_issuer_finance'])
        ]

        scrappers[0].set_next_scraper('GPW_bond_detail', scrappers[1])
        scrappers[0].set_next_scraper('Obligacje_bond_detail', scrappers[2])

        #scrappers[3].set_next_scraper('StockWatch_issuer_bond', scrappers[4])
        #scrappers[4].set_next_scraper('StockWatch_issuer_finance', scrappers[5])

        threads = [
            threading.Thread(target=scrapper.run, name=f'{scrapper.__class__.__name__}')
            for scrapper in scrappers
        ]

        for thread in threads:
            thread.start()
            logging.debug(f'{thread.name} started')

        self.database_handler.delete_bond_list()

        [scrappers[0].put_todo(item) for item in [
            'obligacje-korporacyjne',
            'obligacje-spoldzielcze',
            'listy-zastawne',
            'obligacje-komunalne',
            'obligacje-skarbowe'
        ]]

        # while scrappers[0].is_working():
        #     sleep(1)
        #
        # scrappers[3].put_todo('0')

        while any([scrapper.is_working() for scrapper in scrappers]):
            sleep(1)

        self.exit_event.set()

        for thread in threads:
            thread.join()
            logging.debug(f'{thread.name} joined')

        self.database_handler.update_last_modified_date()

    def set_progress_vars(self, progress_vars: {str: tkinter.DoubleVar}):
        self.progress_vars = progress_vars