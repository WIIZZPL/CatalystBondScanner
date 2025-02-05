import random
import re
from bs4 import BeautifulSoup
from scraper.component_scrappers.BaseScraper import BaseScraper

class GPWBondScraper(BaseScraper):

    def item_to_url(self, item):
        return f'https://gpwcatalyst.pl/o-instrumentach-instrument?nazwa={item}#kalkulatorTab'

    def parse(self, resource):
        result: (str, str, str, str, str, str, str, str, str)  #Bond name, Type, Par value, Bond count, Interest rate, Index name, Accrued interest, Maturity date, Payments per anum
        doc = BeautifulSoup(resource, 'html.parser')
        bond_name = doc.find('div', class_="font30 font-light padding-top-10 padding-bottom-5").text

        exit(0)

        return (bond_name, bond_type, par_value, bond_count, interest_rate, index_name, accrued_interest, maturity_date, payments_per_anum), True

    async def save(self, parsed_resource):
        raise NotImplementedError