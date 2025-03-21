import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from datetime import datetime
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM
from extract_table import create_dataframes  
from pydentic_classes import TableParser
import time

class TableDataParser:
    def __init__(self):
        self.dataframes = create_dataframes()  
        self.llm = OllamaLLM(
            model="llama3",
            base_url="http://192.168.20.106:11434",
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=TableParser)  # Fixed variable name
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
    def single_dataframe(self):
        for idx, df in enumerate(self.dataframes):
            self.table=df

    def 

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


if __name__ == "__main__":
    #start_time = time.time()  

    parser = TableDataParser()  
    parser.single_dataframe()

    """
    parser.save_to_excel()  

    end_time = time.time()  
    execution_time = end_time - start_time  

    print(f"Total Execution Time: {execution_time:.2f} seconds")"""




 