import re

from bs4 import BeautifulSoup

from scraper.component_scrappers.BaseScraper import BaseScraper

class StockwatchIssuerListScraper(BaseScraper):
    def item_to_url(self, item: str) -> str | None:
        return f'https://www.stockwatch.pl/async/bondsemitentslistasync.aspx?pg={item}'

    def parse(self, resource: str) -> (([str], int, int), bool):
        result: ([str], int, int) = ()  # ([Relative url], Current page, Number of pages)
        doc = BeautifulSoup(resource, 'html.parser')

        urls = []

        table = doc.find('tbody')

        tag_links = table.find_all('strong')

        for tag in tag_links:
            urls.append(tag.find('a')['href'])

        nav = doc.find('div', class_='postnavigation').find(string=re.compile('[0-9]+/[0-9]+')).split('/')

        current_page_no = int(nav[0])
        no_pages = int(nav[1])

        return (urls, current_page_no, no_pages), True

    async def save(self, parsed_resource):
        if parsed_resource[1] < parsed_resource[2]:
            await self.put_todo(parsed_resource[1])

        for issuer_path in parsed_resource[0]:
            await self.next_scrapers['StockWatch_issuer_bond'].put_todo(issuer_path)