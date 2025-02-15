import logging
import queue
import threading
import tkinter
import multiprocessing
from threading import Event
from time import sleep

import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter


class BaseScraper:

    def __init__(self, client: httpx.Client, database_handler: DatabaseHandler, limiter: AsyncRateLimiter, exit_event: Event, progress_var: tkinter.DoubleVar, workers: int = 5):
        self.client = client
        self.todo = multiprocessing.Queue()  #Items
        self.seen = set() #URLs

        self.lock = threading.Lock()
        self.scheduled = 0
        self.finished = 0
        self.progress_var = progress_var

        self.database_handler = database_handler
        self.limiter = limiter
        self.exit_event = exit_event

        self.workers : [threading.Thread] = []
        self.max_workers = workers

        self.next_scrapers : {str: BaseScraper} = {}

    def set_next_scraper(self, key, next_scraper):
        self.next_scrapers[key] = next_scraper

    def is_working(self):
        working = 0
        for worker in self.workers:
            if worker.is_alive():
                working += 1

        return self.scheduled > self.finished and working > 0

    def has_finished_all(self):
        return self.scheduled == self.finished

    def put_todo(self, item):
        self.lock.acquire()
        self.scheduled += 1
        self.todo.put(item)
        self.lock.release()

    def update_progress(self):
        if self.scheduled == 0:
            self.progress_var.set(0)
            return
        self.progress_var.set(self.finished/self.scheduled)

    def run(self):
        logging.debug('Scrapper start')
        self.workers = [
            threading.Thread(target=self.worker, name=f'{self.__class__.__name__} {i}')
            for i in range(self.max_workers)
        ]

        for worker in self.workers:
            worker.start()

        while not self.exit_event.is_set():
            sleep(1)

        logging.debug('Scrapper stopping')

        for worker in self.workers:
            worker.join()

        logging.debug('Scrapper stopped')

    def worker(self):
        while not self.exit_event.is_set():
            try:
                self.process_one()
            except Exception as e:
                logging.exception(repr(e))

    def process_one(self):
        try:
            item = self.todo.get(timeout=3)
            self.process(item)
        except queue.Empty:
            return
        finally:
            self.lock.acquire()
            self.finished += 1
            self.update_progress()
            self.lock.release()

    def process(self, item):
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
            with self.limiter:
                logging.debug(f'{item} sending request')
                try:
                    resource = self.client.get(url, follow_redirects=True)
                except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError):
                    logging.info(f'{item} timeout')
                    sleep(5)
                    continue

            parsed_resource, parse_success = self.parse(resource.text)

            if parse_success:
                break

        logging.debug(f'{item} saving')
        self.save(parsed_resource)
        logging.debug(f'{item} saved')

    def item_to_url(self, item: str) -> str:
        raise NotImplementedError

    def parse(self, resource: str) -> (str, bool):
        raise NotImplementedError

    def save(self, parsed_resource):
        raise NotImplementedError
