import os
import pandas as pd
from bs4 import BeautifulSoup
from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from pydentic_classes import GenericPartsData
from clean_html import call_build_block

class TableDataParser:
    def __init__(self):
        self.llm = OllamaLLM(
            model="llama3",
            base_url="http://192.168.20.194:11434",
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=GenericPartsData)
        
        self.prompt = PromptTemplate(
            template="""SYSTEM: Extract ONLY these fields as raw JSON:
            1. thread_size: Extract the actual thread size/type from the headers (e.g., "2-56", "M6-0.5", "1/4-20 UNC").
            2. material_surface: Extract material surface treatments (ALWAYS list all available).

            STRICT RULES:
            - If no thread size is found, return "unknown".
            - Do NOT return example values; extract directly from the headers.
            - Output ONLY the JSON object. Do not add any other text or explanations.

            Table Headers:
            {raw_data}

            JSON Output:""",
            input_variables=["raw_data"],
        )
        
        self.chain = (
            RunnablePassthrough.assign(raw_data=lambda x: x["raw_data"])
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def parse_company_data(self, raw_data: str) -> GenericPartsData:
        try:
            print("Sending to LLM:", raw_data)  # Debugging log
            raw_response = self.llm.invoke(self.prompt.format(raw_data=raw_data))
            print("Raw LLM Output:", raw_response)  # Debugging log
            return self.output_parser.parse(raw_response)
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None

    def extract_table_headers_from_html(self, html_content: str):
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        
        headers_list = []
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find_all("th") if th.get_text(strip=True)]  # Extract only text
            headers_text = ", ".join(headers) if headers else "unknown"  # Fallback if no headers
            headers_list.append(headers_text)

        return headers_list


# Initialize parser
table_parser = TableDataParser()

# Retrieve HTML content
html_content = call_build_block()
if not html_content:
    print("Error: No HTML content retrieved!")
    exit()

# Extract table headers
html_tables_heads = table_parser.extract_table_headers_from_html(html_content)

if not html_tables_heads:
    print("Error: No tables found in HTML!")
    exit()

# Debug: Print extracted headers before sending to LLM
print("Extracted Headers:", html_tables_heads)

# Parse the first table's headers
parsed_data = table_parser.parse_company_data(html_tables_heads[4])

# Print final parsed data
if parsed_data:
    print(parsed_data.model_dump_json(indent=2))
else:
    print("Failed to process Table")






    """
    # Process each table individually
    for idx, table_html in enumerate(html_tables):
        print(f"\nProcessing Table {idx + 1}:\n")
        
        parsed_data = table_parser.parse_company_data(table_html)
        
        if parsed_data:
            print(parsed_data.model_dump_json(indent=2))  # Ensure `parsed_data` is a Pydantic model
        else:
            print(f"Failed to process Table {idx + 1}")

except Exception as e:
    print(f"Failed to parse company data: {e}")


     def save_to_excel(self, filename="./excel/output2.xlsx"):
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if not self.dataframes:
            print("No dataframes available to save.")
            return
        
        try:
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                for idx, df in enumerate(self.dataframes):
                    sheet_name = f"Sheet{idx+1}"  
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Data saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")"""


"""if __name__ == "__main__":
    #start_time = time.time()  

    parser = TableDataParser()  
    parser.single_dataframe()


    parser.save_to_excel()  

    end_time = time.time()  
    execution_time = end_time - start_time  

    print(f"Total Execution Time: {execution_time:.2f} seconds")"""




 