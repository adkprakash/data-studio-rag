from clean_html import call_build_block
from bs4 import BeautifulSoup
import pandas as pd

def create_dataframes():
    html_data = call_build_block()

    soup = BeautifulSoup(html_data, "html.parser")
    tables = soup.find_all("table")


    dataframes = []

    for table in tables:
        data = []

        
        thead = table.find("thead")
        if thead:
            for row in thead.find_all("tr"):
                cols = row.find_all(["th", "td"])
                data.append([col.get_text(strip=True) for col in cols])

        
        tbody = table.find("tbody")
        if tbody:
            
            orphan_ths = tbody.find_all("th", recursive=False)  
            if orphan_ths:
                for orphan_th in orphan_ths:
                    
                    new_td = soup.new_tag("td")
                    new_td.string = orphan_th.get_text(strip=True)

                    
                    new_tr = soup.new_tag("tr")
                    new_tr.append(new_td)

                    
                    orphan_th.insert_before(new_tr)
                    orphan_th.decompose()  

            
            for row in tbody.find_all("tr"):
                cols = row.find_all(["th", "td"])
                data.append([col.get_text(strip=True) for col in cols])

        
        max_cols = max(len(row) for row in data)  
        
        df = pd.DataFrame([row + [""] * (max_cols - len(row)) for row in data])  

       
        dataframes.append(df)

    return dataframes






