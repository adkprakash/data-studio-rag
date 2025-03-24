from clean_html import call_build_block
from bs4 import BeautifulSoup

def parse_html_table(html_data):
    soup = BeautifulSoup(html_data, "html.parser")
    tables = soup.find_all("table")
    extracted_tables = {}

    for table_idx, table in enumerate(tables, start=1):
        rows = table.find_all("tr")
        if not rows:
            continue

        # Extract headers from the first row
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        
        # If no headers found in first row, determine from max columns
        if not headers:
            max_columns = max(len(row.find_all(["td", "th"])) for row in rows)
            headers = [f"Column_{i+1}" for i in range(max_columns)]
            data_rows = rows
        else:
            data_rows = rows[1:]

        # Process all data rows (including handling orphan th)
        table_data = []
        for row in data_rows:
            cells = row.find_all(["td", "th"])  # Capture both td and th
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            table_data.append(cell_texts)

        # Determine maximum columns
        max_columns = max(len(headers), max((len(row) for row in table_data), default=0))
        
        # Pad headers and rows to max_columns
        headers = headers[:max_columns] + [f"Column_{i+1}" for i in range(len(headers), max_columns)]
        padded_data = [row + [''] * (max_columns - len(row)) for row in table_data]

        # Transpose data to column-based dictionary
        data_dict = {header: [] for header in headers}
        for row in padded_data:
            for i, header in enumerate(headers):
                data_dict[header].append(row[i] if i < len(row) else '')

        extracted_tables[f"table_{table_idx}"] = data_dict

    return extracted_tables

# Example usage
if __name__ == "__main__":
    table_dicts = extract_tables_as_column_dict()

    # Print only the first 3 tables
    for table_idx, (table_name, table_data) in enumerate(table_dicts.items()):
        if table_idx >= 3:
            break
        print(f"{table_name}:")
        for key, values in table_data.items():
            print(f"  {key}: {values}")
