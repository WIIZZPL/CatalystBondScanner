import re
from bs4 import BeautifulSoup

from scraper.component_scrappers.BaseScraper import BaseScraper


class ObligacjeBondScraper(BaseScraper):
    def item_to_url(self, item):
        return f'https://obligacje.pl/pl/obligacja/{item}'

    def parse(self, resource):
        result: (str, str, str, str, str)  #Bond code, Secured, Index, Base interest rate, Amount of payments per anum
        doc = BeautifulSoup(resource, 'html.parser')

        bond_code = doc.find('div', class_='title').find('h1').text

        table = doc.find('table', class_='table-9')

        is_secured = table.find('th', string='Zabezpieczenie:').find_next('td').text

        interest_rate_type = table.find('th', string='Typ oprocentowania:').find_next('td').text

        index_name = re.search(r'(?<=zmienne ).*(?= \+)', interest_rate_type)
        index_name = index_name.group() if index_name is not None else None

        base_interest_rate = re.search(r'[0-9]+(\.[0-9]+)?(?=%)', interest_rate_type)
        base_interest_rate = base_interest_rate.group() if base_interest_rate is not None else None

        payments_tags = doc.find('h4', string='Dni wypłaty odsetek').find_next('div').find_all('li')
        payment_dates = list(map(lambda x: x.text, payments_tags))

        additional_content_box = table.find_next('div', class_='content-txt')

        additional_info = None
        if additional_content_box is not None:
            strings = list(additional_content_box.stripped_strings)
            additional_info = '\n'.join(strings[1:])

        return (bond_code, is_secured, index_name, base_interest_rate, payment_dates, additional_info), True

    def save(self, parsed_resource):
        self.database_handler.upsert_obligacje_bond_detail(parsed_resource)