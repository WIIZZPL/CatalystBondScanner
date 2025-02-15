from bs4 import BeautifulSoup
import re

from scraper.component_scrappers.BaseScraper import BaseScraper


class StockwatchIssuerBondScraper(BaseScraper):
    def item_to_url(self, item: str) -> str | None:
        return f'https://www.stockwatch.pl{item}'

    def parse(self, resource: str) -> (([str], str, str), bool):
        result: ([str], str, str) = ()  # ([Bond codes], SW code, Financial data url)
        doc = BeautifulSoup(resource, 'html.parser')

        code_path = doc.find('form', id='aspnetForm')['action']
        sw_code_res = re.search(r'(?<=\?ticker=).*', code_path)
        sw_code = sw_code_res.group() if sw_code_res is not None else None

        if sw_code is None:
            return ([], sw_code, None), True

        panel = doc.find('div', class_='panel-button')
        fin_data_url = panel.find('a', href=re.compile('dane-finansowe'))['href'] if panel is not None else None

        if fin_data_url is None:
            return ([], sw_code, fin_data_url), True

        table = doc.find('table', class_='cctabdt table-emitent')

        bonds = []
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) == 0:
                continue
            if tds[-2].text.lower() == 'wykup w terminie':
                continue

            bond_tag = tds[0].find('a')
            bonds.append(bond_tag.text.strip())

        return (bonds, sw_code, fin_data_url), True

    def save(self, parsed_resource):
        if len(parsed_resource[0]) == 0 or parsed_resource[1] is None or parsed_resource[2] is None:
            return

        self.database_handler.upsert_sw_issuer_bonds(parsed_resource)

        self.next_scrapers['StockWatch_issuer_finance'].put_todo(parsed_resource[2])
