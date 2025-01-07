import httpx

from db_access import DatabaseHandler
from scraper.AsyncRateLimiter import AsyncRateLimiter


class BondScraper:
    def __init__(self):
        self.limiter = AsyncRateLimiter.get_instance()

    def set_database_handler(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler
