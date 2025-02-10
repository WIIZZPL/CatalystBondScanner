import random
import re
from bs4 import BeautifulSoup
from scraper.component_scrappers.BaseScraper import BaseScraper

class GPWBondScraper(BaseScraper):

    async def item_to_url(self, item):
        return f'https://gpwcatalyst.pl/o-instrumentach-instrument?nazwa={item}'

    def parse(self, resource):
        result: (str, str, str, str, str, str, str)  #Bond code, Maturity date, Par value, Issue value, Type of interest, Current interest rate, Accrued interest
        doc = BeautifulSoup(resource, 'html.parser')
        bond_code = doc.find('div', class_="font30 font-light padding-top-10 padding-bottom-5").text

        table = doc.find('table', id='footable_basic')

        maturity_date = table.find('td', string='Data wykupu').find_next('td').text

        par_value = (table.find('td', string=re.compile('Wartość nominalna')).find_next('td').text
                     .replace(' ', '').replace(',', '.'))

        issue_value = (table.find('td', string=re.compile('Wartość emisji')).find_next('td').text
                       .replace(' ', '').replace(',', '.'))

        type_of_interest = (table.find('td', string='Rodzaj oprocentowania obligacji').find_next('td').text
                            .strip())

        current_interest_rate_label = table.find('td', string='Oprocentowanie w bieżącym okresie odsetkowym (%)')
        current_interest_rate = None
        if current_interest_rate_label is not None:
            current_interest_rate = current_interest_rate_label.find_next('td').text
        if type_of_interest == 'zerokuponowe':
            current_interest_rate = 0

        accrued_interest_label = table.find('td', string=re.compile('Odsetki skumulowane'))
        accrued_interest = None
        if accrued_interest_label is not None:
            accrued_interest = (accrued_interest_label.find_next('td').text
                                .replace(' ', '').replace(',', '.'))
        if type_of_interest == 'zerokuponowe':
            accrued_interest = 0

        return (bond_code, maturity_date, par_value, issue_value, type_of_interest, current_interest_rate, accrued_interest), True

    async def save(self, parsed_resource):
        self.database_handler.upsert_gpw_bond_detail(parsed_resource)