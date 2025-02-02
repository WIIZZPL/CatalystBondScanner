import asyncio
import datetime
import logging
from threading import Event
import httpx
from httpx import Response

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter


class BaseScraper:

    def __init__(self, client: httpx.AsyncClient, database_handler: DatabaseHandler, limiter: AsyncRateLimiter,
                 exit_event: Event, workers: int = 5):
        self.client = client
        self.todo = asyncio.Queue()  #Items
        self.done = set()  #URLs

        self.database_handler = database_handler
        self.limiter = limiter
        self.exit_event = exit_event

        self.max_workers = workers

    def clear_queue(self):
        self.todo = asyncio.Queue()
        logging.warning('Todo queue cleared')

    def is_working(self):
        return not self.todo.empty()

    async def put_todo(self, item):
        await self.todo.put(item)

    async def run(self):
        logging.debug('Scrapper start')
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.max_workers)
        ]

        while not self.exit_event.is_set():
            await asyncio.sleep(1)

        logging.debug('Scrapper stopping')

        for worker in workers:
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
            except asyncio.CancelledError:
                return

    async def process_one(self):
        item = await self.todo.get()
        try:
            await self.process(item)
        finally:
            self.todo.task_done()

    async def process(self, item):
        url = self.item_to_url(item)

        if url in self.done:
            return

        logging.debug('Waiting for limiter')
        start = datetime.datetime.now()
        while True:
            async with self.limiter:
                logging.debug('Sending request')
                resource = await self.client.get(url, follow_redirects=True)


            parsed_resource, parse_success = self.parse(resource.text)

            if not parse_success:
                pass

            break

        logging.debug('Saving parsed data')
        #await self.save(parsed_resource)

        self.done.add(url)

    def item_to_url(self, item: str) -> str:
        raise NotImplementedError

    def parse(self, resource: str) -> (str, bool):
        raise NotImplementedError

    async def save(self, parsed_resource):
        raise NotImplementedError
