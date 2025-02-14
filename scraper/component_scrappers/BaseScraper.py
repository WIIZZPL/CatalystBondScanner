import asyncio
import logging
import random
import threading
import tkinter
from asyncio import new_event_loop
from threading import Event

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter


class BaseScraper:

    def __init__(self, client: httpx.AsyncClient, database_handler: DatabaseHandler, limiter: AsyncRateLimiter, exit_event: Event, progress_var: tkinter.DoubleVar, workers: int = 5):
        self.client = client
        self.todo = asyncio.Queue()  #Items
        self.seen = set() #URLs

        self.lock = threading.Lock()
        self.scheduled = 0
        self.finished = 0
        self.progress_var = progress_var

        self.database_handler = database_handler
        self.limiter = limiter
        self.exit_event = exit_event

        self.workers = []
        self.max_workers = workers

        self.next_scrapers : {str: BaseScraper} = {}

    def set_next_scraper(self, key, next_scraper):
        self.next_scrapers[key] = next_scraper

    def is_working(self):
        working = 0
        for worker in self.workers:
            if not worker.done():
                working += 1

        return self.scheduled > self.finished and working > 0

    def has_finished_all(self):
        return self.scheduled == self.finished

    async def put_todo(self, item):
        self.lock.acquire()
        self.scheduled += 1
        await self.todo.put(item)
        self.lock.release()

    def update_prgoress(self):
        self.progress_var.set(self.finished/self.scheduled)

    async def run(self):
        logging.debug('Scrapper start')
        self.workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.max_workers)
        ]

        while not self.exit_event.is_set():
            await asyncio.sleep(1)

        logging.debug('Scrapper stopping')

        for worker in self.workers:
            worker.cancel()
            try:
                await worker
            except BaseException as e:
                logging.exception(e)
        logging.debug('Scrapper stopped')

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError as e:
                logging.debug(repr(e))
                return
            except Exception as e:
                logging.exception(repr(e))

    async def process_one(self):
        item = await self.todo.get()
        try:
            await self.process(item)
        finally:
            self.lock.acquire()
            self.todo.task_done()
            self.finished += 1
            self.update_prgoress()
            self.lock.release()

    async def process(self, item):
        url = self.item_to_url(item)

        if url is None:
            logging.debug(f'{item} URL not found')
            return

        if url in self.seen:
            logging.debug(f'{item} already done as {url}, skipping')
            return

        self.seen.add(url)

        logging.debug(f'{item} waiting for limiter')
        while True:
            async with self.limiter:
                logging.debug(f'{item} sending request')
                try:
                    resource = await self.client.get(url, follow_redirects=True)
                except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError):
                    logging.info(f'{item} timeout')
                    await asyncio.sleep(5)
                    continue

            parsed_resource, parse_success = self.parse(resource.text)

            if not parse_success:
                pass

            break

        logging.debug(f'{item} saving')
        await  self.save(parsed_resource)
        logging.debug(f'{item} saved')

    def item_to_url(self, item: str) -> str:
        raise NotImplementedError

    def parse(self, resource: str) -> (str, bool):
        raise NotImplementedError

    async def save(self, parsed_resource):
        raise NotImplementedError
