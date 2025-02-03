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

        print(doc.find_all('table'))
        table = doc.table()
        exit(0)
        #TODO
        bond_type = table.find('td', text='Typ obligacji').find_next_sibling('td').text
        par_value = table.find('td', text='Wartość nominalna').find_next_sibling('td').text
        bond_count = table.find('td', text='Liczba obligacji').find_next_sibling('td').text

        index_name = table.find('td', text='Rodzaj oprocentowania').find_next_sibling('td').text
        interest_rate = table.find('td', text='Marża nominalna').find_next_sibling('td').text

        accrued_interest = table.find('td', text='Narosłe odsetki').find_next_sibling('td').text
        maturity_date = table.find('td', text='Data wykupu').find_next_sibling('td').text
        payments_per_anum = table.find('td', text='Liczba wypłat w ciągu roku').find_next_sibling('td').text

        print(bond_name, bond_type, par_value, bond_count, interest_rate, index_name, accrued_interest, maturity_date, payments_per_anum)
        return (bond_name, bond_type, par_value, bond_count, interest_rate, index_name, accrued_interest, maturity_date, payments_per_anum), True

    async def save(self, parsed_resource):
        raise NotImplementedError