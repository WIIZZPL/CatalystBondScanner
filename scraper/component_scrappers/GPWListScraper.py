import re
from bs4 import BeautifulSoup
from scraper.component_scrappers.BaseScraper import BaseScraper

class GPWListScraper(BaseScraper):

    async def item_to_url(self, item):
        return f'https://gpwcatalyst.pl/notowania-obligacji-{item}'

    def parse(self, resource):
        result :[(str, str, str, str, str, str)] = [] # Issuer, Bond name, Market, Price, Currency, Bond_type
        doc = BeautifulSoup(resource, 'html.parser')
        quotations = doc.find('div', id='bs_quotation')
        table_headers = quotations.find_all('div', style='display: flex; justify-content: space-between')

        bond_type = doc.find('ol', class_='breadcrumb').find('li', class_='active').text
        bond_type = {
            'Obligacje korporacyjne': 'Korporacyjna',
            'Obligacje spółdzielcze': 'Spółdzielcza',
            'Obligacje skarbowe': 'Skarbowa',
            'Obligacje komunalne': 'Komunalna',
            'Listy zastawne': 'List zastany',
        }[bond_type]

        #Seperates quotations into tables by currency
        for table_header in table_headers:
            table_hearer_title = table_header.find('h3', style='display: block;')
            currency = re.search(r'[A-Z]{3}', table_hearer_title.text).group()
            table = table_header.find_next('tbody')

            for row in table.find_all('tr'):
                issuer_cell = row.find('td', class_='col0')
                bond_cell = row.find('td', class_='col1')
                market_cell = row.find('td', class_='col2')
                price_cell = row.find('td', class_='col4')

                issuer = issuer_cell.find('a').text.strip() if issuer_cell is not None else result[-1][0]

                #GPW Zapisuje Skarb Państwa jako SP
                if issuer == 'SP':
                    issuer = 'SKARB PAŃSTWA'

                bond = bond_cell.find('a').text.strip() if bond_cell is not None else result[-1][1]
                market = market_cell.text.replace(u'\xa0', ' ')
                price = price_cell.text.replace(',', '.')

                result.append((issuer, bond, market, price, currency, bond_type))

        return result, True

    async def save(self, parsed_resource):
        self.database_handler.upsert_bond_list(parsed_resource)
        [await self.next_scrapers['GPW_bond_detail'].put_todo(bond[1]) for bond in parsed_resource]
        [await self.next_scrapers['Obligacje_bond_detail'].put_todo(bond[1]) for bond in parsed_resource]
        for bond in parsed_resource:
            if bond[5] == 'Korporacyjna':
                await self.next_scrapers['StockWatch_issuer_detail'].put_todo(bond[1])