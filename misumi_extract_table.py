from clean_html import call_build_block
from bs4 import BeautifulSoup

class MisumiExtractTable:
    def __init__(self):
        self.html_element = call_build_block()
        self.soup = BeautifulSoup(self.html_element, "html.parser")
        self.tables = None

    def extract_table_element(self):
        self.tables = self.soup.find_all("table")
        top_table = None  
        
        if self.tables:
            top_table = self.tables[0]  
            for th in top_table.find_all("th"):
                td = self.soup.new_tag("td")  
                td.attrs = th.attrs.copy()
                td.string = th.text.strip()
                th.replace_with(td)
        
        return top_table

    def create_dataframe(self):
        import pandas as pd
        
        if not self.tables:
            return pd.DataFrame()
        
        top_table = self.tables[0]
        rows = top_table.find_all("tr")
        
        
        all_data = []
        for row in rows:
            cols = row.find_all("td")
            all_data.extend([col.get_text(strip=True) for col in cols])
        
        
        df = pd.DataFrame([all_data])
        
        return df



tables_extractor = MisumiExtractTable()
tables = tables_extractor.extract_table_element()
print(tables)
dataframe=tables_extractor.create_dataframe()
print(dataframe)
