import logging
import re
import tkinter
from asyncio import Event
import httpx
from search_engine_parser.core.exceptions import NoResultsOrTrafficError, NoResultsFound

from db_access import DatabaseHandler
from scraper import AsyncRateLimiter
from scraper.component_scrappers.BaseScraper import BaseScraper
from search_engine_parser.core.engines.duckduckgo import Search as DuckSearch

class StockwatchIssuerScraper(BaseScraper):
    def __init__(self, client: httpx.AsyncClient, database_handler: DatabaseHandler, limiter: AsyncRateLimiter,
                 exit_event: Event, progress_var: tkinter.DoubleVar, workers: int = 5):
        super().__init__(client, database_handler, limiter, exit_event, progress_var, workers)
        self.dsearch = DuckSearch()

    async def item_to_url(self, item: str) -> str | None:
        #TODO GETTING STOCKWATCH URL
        query = f'site:stockwatch.pl {item}'
        try:
            return None
            #results = await self.dsearch.async_search(query=query, cache=True)
        except NoResultsOrTrafficError | NoResultsFound:
            logging.info(f"No search results found for {item}")
            return None

        for result in results:
            if item in result['title']:
                return result['link']

        return None

    def parse(self, resource: str) -> (str, bool):
        pass

    async def save(self, parsed_resource):
        pass