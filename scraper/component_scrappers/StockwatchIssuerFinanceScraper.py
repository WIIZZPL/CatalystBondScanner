import re

from bs4 import BeautifulSoup

from scraper.component_scrappers.BaseScraper import BaseScraper

quarters_to_grab = 4

class StockwatchIssuerFinanceScraper(BaseScraper):
    def item_to_url(self, item: str) -> str | None:
        return f'https://www.stockwatch.pl{item}'

    def parse(self, resource: str, item: str = None) -> (([str], str, str), bool):
        result: ([str], str, str) = ()  # ([Bond codes], SW code, Financial data url)
        doc = BeautifulSoup(resource, 'html.parser')

        stock = doc.find('div', class_='cmpn-info stock').find('a')['href']
        print(stock)

        desc = doc.find('div', id='ctl00_Body_CompanyMain1_StIt2j').find('div', class_='descBx').find('p').text
        print(desc)

        table = doc.find('table', class_='cctabdtdn')
        table_head = table.find('thead')
        table_body = table.find('tbody')

        if table_head is None or table_body is None:
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            print(f'{table_head is None} or {table_body is None}')

        dates = []

        for head in table_head.find_all('th')[-quarters_to_grab:]:
            dates.append(head.find('b').text)

        print(dates)

        rows = table_body.find_all('tr', class_=lambda c: c is None or 'dyn' not in c)

        data = []
        for filter in ['Liczba akcji', 'Zysk operacyjny', 'Zysk netto', 'Aktywa razem', 'Zobowiązania razem', '(Zyski zatrzymane)|(Zysk lat ubiegłych)', 'Aktywa obrotowe', 'Aktywa trwałe']:
            temp = []
            print(rows.find(value=re.compile(filter)))
            # for cols in rows[row_id].find_all('td')[-quarters_to_grab:]:
            #     temp.append(cols.text.replace(" ", ''))
            # print(temp)
            # data.append(temp)

        exit(0)
        #return (bonds, sw_code, fin_data_url), True

    def save(self, parsed_resource):
        pass
        #self.database_handler.upsert_sw_finance(parsed_resource)