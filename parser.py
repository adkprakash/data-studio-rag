import os
import pandas as pd
from bs4 import BeautifulSoup
from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from pydentic_classes import TableParser
from clean_html import call_build_block
import time

class TableDataParser:
    def __init__(self):
        self.llm = OllamaLLM(
            model="llama3",
            # base_url="http://192.168.20.106:11434",
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=TableParser)
        self.format_instructions = self.output_parser.get_format_instructions()
        
        self.prompt = PromptTemplate(
            template=(
                "SYSTEM: You are a structured data extraction tool. "
                "Follow these rules strictly:\n"
                "1. Extract ONLY the specified fields in the schema. Here is the schema:\n"
                "{format_instructions}\n"
                "2. NEVER add comments, explanations, or markdown.\n"
                "3. Use EXACTLY the structure defined in the schema.\n"
                "4. If information is missing, use null.\n"
                "5. Maintain strict key names as shown in the schema.\n\n"
                "USER INPUT: {raw_data}\n\n"
                "ASSISTANT RESPONSE (ONLY VALID JSON):"
            ),
            input_variables=["raw_data"],
            partial_variables={"format_instructions": self.format_instructions},
        )
        
        self.chain = (
            RunnablePassthrough.assign(raw_data=lambda x: x["raw_data"])
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def parse_company_data(self, raw_data: str) -> TableParser:
        """Send extracted table HTML content to LLM for parsing."""
        try:
            return self.chain.invoke({"raw_data": raw_data})
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None

    def extract_tables_from_html(self, html_content: str):
        """Extracts tables from HTML and returns them as a list of strings."""
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        return [str(table) for table in tables]  # Convert each table to a string

# Instantiate the parser
table_parser = TableDataParser()

# Get HTML content from the `build_block_tree` function
html_content = call_build_block()

try:
    # Extract tables from HTML
    html_tables = table_parser.extract_tables_from_html(html_content)
    
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


    """ def save_to_excel(self, filename="./excel/output2.xlsx"):
        
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




 