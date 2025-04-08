from clean_html import call_build_block
from bs4 import BeautifulSoup
import pandas as pd

def create_dataframes():
    html_data = call_build_block()
    soup = BeautifulSoup(html_data, "html.parser")
    tables = soup.find_all("table")

    thead_dataframes = []
    tbody_dataframes = []

    for table in tables:
        thead_data = []
        tbody_data = []

        thead = table.find("thead")
        if thead:
            for row in thead.find_all("tr"):
                cols = row.find_all(["th", "td"])
                
                for col in cols:
                    if col.name == "td":
                        col.name = "th"
                thead_data.append([col.get_text(strip=True) for col in cols])


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
                tbody_data.append([col.get_text(strip=True) for col in cols])

        max_thead_cols = max((len(row) for row in thead_data), default=0)
        max_tbody_cols = max((len(row) for row in tbody_data), default=0)
        
        thead_df = pd.DataFrame([row + [""] * (max_thead_cols - len(row)) for row in thead_data])
        tbody_df = pd.DataFrame([row + [""] * (max_tbody_cols - len(row)) for row in tbody_data])
        try:
            tbody_df = tbody_df[tbody_df.iloc[:, 0] != ""].reset_index(drop=True)
        except IndexError:
            print("tbody_df has no columns. Skipping...")
            return None, None
        
        
        thead_dataframes.append(thead_df)
        tbody_dataframes.append(tbody_df)


        

    return thead_dataframes, tbody_dataframes


