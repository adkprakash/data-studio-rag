from clean_html import call_build_block
from bs4 import BeautifulSoup
import pandas as pd
import time

class MisumiExtractTable:
    def __init__(self,html_clean_data):
        self.html_element = html_clean_data
        self.soup = BeautifulSoup(self.html_element, "html.parser")
        self.tables = self.soup.find_all("table")

    def _clean_nested_tr(self, table):
        for outer_tr in table.find_all("tr"):
            inner_trs = outer_tr.find_all("tr", recursive=False)
            if inner_trs:
                outer_tr.unwrap()
        return table

    def _parse_table_to_dict(self, table):
        cleaned_table = self._clean_nested_tr(table)
        data = {}
        for row in cleaned_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                header = th.get_text(strip=True)
                value = td.get_text(strip=True)
                if header != "-":
                    data[header] = value
        return data
    
    def _parse_price_table_to_dict(self, table):
        result = []

        thead = table.find('thead')
        tbody = table.find('tbody')

        if not thead or not tbody:
            return result

        headers = [th.get_text(strip=True) for th in thead.find_all('th')]

        for tr in tbody.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            row = dict(zip(headers, cells))
            result.append(row)

  

        return result

    def create_dataframe(self):
        if not self.tables:
            return pd.DataFrame()

        attribute_data = self._parse_table_to_dict(self.tables[0]) if len(self.tables) >= 1 else {}
        price_data = self._parse_price_table_to_dict(self.tables[-1])

        if not price_data:
            return pd.DataFrame()

        
        flat_row = []
        for key, value in attribute_data.items():
            flat_row.extend([key, value])

        
        for row in price_data:
            for key, value in row.items():
                flat_row.extend([key, value])

        
        return pd.DataFrame([flat_row], columns=range(len(flat_row)))

def get_misumi_data(html_clean_data):
    extractor = MisumiExtractTable(html_clean_data)
    dataframe = extractor.create_dataframe()
    return dataframe




