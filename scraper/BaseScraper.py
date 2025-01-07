import asyncio
from queue import Queue
from threading import Event
from typing import Iterable

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter


class BaseScraper:

    def __init__(self, client: httpx.AsyncClient, database_handler: DatabaseHandler, limiter: AsyncRateLimiter, exit_event: Event, workers: int = 10):
        self.client = client
        self.todo = Queue()
        self.seen = set()
        self.done = set()

        self.database_handler = database_handler
        self.limiter = limiter
        self.exit_event = exit_event

        self.max_workers = workers

    def clear_queue(self):
        self.todo = Queue()

    async def run(self):
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.max_workers)
        ]

        while not self.todo.empty() or not self.exit_event.is_set():
            await asyncio.sleep(1)

        for worker in workers:
            worker.cancel()

    async def on_found_links(self, urls):
        new = urls - self.seen
        self.seen.update(new)

        #TODO DATABASE_HANDLER

        for url in new:
            await self.put_todo(url)

    async def put_todo(self, url):
        await self.todo.put(url)

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def process_one(self):
        url = await self.todo.get()
        try:
            await self.crawl(url)
        except Exception as e:
            #retry handling
            pass
        finally:
            self.todo.task_done()

    async def crawl(self, url):
        #TODO rate limit
        await asyncio.sleep(.1)

        resource = await self.client.get(url, follow_redirects=True)

        await self.parse_links()

        await self.on_found_links()

        self.done.add(url)