import re

from bs4 import BeautifulSoup

from scraper.BaseScraper import BaseScraper


class GPWListScraper(BaseScraper):

    def item_to_url(self, item):
        return f'https://gpwcatalyst.pl/notowania-obligacji-{item}'

    def parse(self, resource):
        print("PARSING")
        result :[(str, str, str, str, str)] = [] # Issuer, Bond name, Trading system, Price, Currency
        doc = BeautifulSoup(resource, 'html.parser')
        quotations = doc.find('div', id='bs_quotation')
        table_headers = doc.find_all('div', style='display: flex; justify-content: space-between')

        #Seperates quotations into tables by currency
        for table_header in table_headers:
            table_hearer_title = table_header.find('h3', style='display: block;')
            currency = re.search(r'[A-Z]{3}', table_hearer_title.text).group()
            table = table_header.find_next('tbody')

            for row in table.find_all('tr'):
                issuer_cell = row.find('td', class_='col0')
                bond_cell = row.find('td', class_='col1')
                system_cell = row.find('td', class_='col2')
                price_cell = row.find('td', class_='col4')

                print(issuer_cell, bond_cell, system_cell)

                issuer = issuer_cell.find('a').text.strip() if issuer_cell is not None else result[-1][0]
                bond = bond_cell.find('a').text.strip() if bond_cell is not None else result[-1][0]
                system = system_cell.text
                price = price_cell.text

                result.append((issuer, bond, system, price, currency))
                print(issuer, bond, system, price, currency)


        print(result)

    async def save(self, parsed_resource):
        raise NotImplementedError