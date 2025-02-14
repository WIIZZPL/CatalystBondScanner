from bs4 import BeautifulSoup

from scraper.component_scrappers.BaseScraper import BaseScraper


class StockwatchIssuerFinanceScraper(BaseScraper):
    def item_to_url(self, item: str) -> str | None:
        return f'https://www.stockwatch.pl{item}'

    def parse(self, resource: str) -> (([str], str, str), bool):
        result: ([str], str, str) = ()  # ([Bond codes], SW code, Financial data url)
        doc = BeautifulSoup(resource, 'html.parser')

        #TODO

        #return (bonds, sw_code, fin_data_url), True

    async def save(self, parsed_resource):
        pass
        #self.database_handler.upsert_sw_finance(parsed_resource)