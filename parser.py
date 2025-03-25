"""import os
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
            template=Extract the following fields as raw JSON. 
            **DO NOT INCLUDE ANY TEXT BEFORE/AFTER THE JSON**. 

            Fields to extract:
            - thread_size: List of thread sizes (e.g., "2-56", "M6-0.5", "1/4-20 UNC")
            - material_surface: List of materials (e.g., "Alloy Steel", "Black-Oxide Alloy Steel")

            Rules:
            1. Output **ONLY** valid JSON. 
            2. No explanations, comments, or formatting outside the JSON.
            3. If no material is found, use `"material_surface": ["unknown"]`.

            Input Data:
            {raw_data}

            Output format (copy-paste this and fill in values):
            {{
            "thread_size": [...],
            "material_surface": [...]
            }}
            ,
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

  

    def extract_tables_and_headers(self, html_content: str):
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        
        
        extracted_headers = []
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            extracted_headers.append(headers if headers else ["unknown"])
        
        return extracted_headers"""



import os
import json
import re
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
            template="""Extract the following fields as raw JSON. 
            **DO NOT INCLUDE ANY TEXT BEFORE/AFTER THE JSON**. 

            Fields to extract:
            - thread_size: List of thread sizes (e.g., "2-56", "M6-0.5", "1/4-20 UNC")
            - material_surface: List of materials (e.g., "Alloy Steel", "Black-Oxide Alloy Steel")

            Rules:
            1. Output **ONLY** valid JSON.
            2. Ensure there are **NO** extra quotation marks around the values (e.g., not `""4-40""`, but `"4-40"`).
            3. Ensure that the values are directly enclosed in double quotes without any additional formatting.
            4. No explanations, comments, or formatting outside the JSON.
            5. If no material is found, use `"material_surface": ["unknown"]`.

            Input Data:
            {raw_data}

            Output format (copy-paste this and fill in values):
            {{
            "thread_size": [...],
            "material_surface": [...]
            }}
            """
            , input_variables=["raw_data"],
        )

        self.chain = (
            RunnablePassthrough.assign(raw_data=lambda x: x["raw_data"])
            | self.prompt
            | self.llm
            | self.output_parser
        )

        
        self.chain = (
            RunnablePassthrough.assign(raw_data=lambda x: x["raw_data"])
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def clean_json_output(self, raw_json: str) -> str:
        """Fix JSON formatting issues in LLM output"""
        # Extract JSON block
        json_match = re.search(r'\{.*\}', raw_json, flags=re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in output")
        
        json_str = json_match.group()
        
        # Ensure thread_size is correctly formatted with escaped quotes and no empty values
        json_str = re.sub(
            r'"thread_size": \[(.*?)\]',
            lambda m: '"thread_size": [' + ', '.join(['"' + s.strip().replace('"', '') + '"' for s in m.group(1).split(',') if s.strip()]) + ']',
            json_str,
            flags=re.DOTALL
        )
        
        # Handle non-breaking spaces and other encoding issues
        json_str = json_str.replace(u'\xa0', ' ')
        
        return json_str



    def parse_company_data(self, raw_data: list) -> GenericPartsData:
        """Parse raw table data with enhanced JSON validation"""
        try:
            print("Sending to LLM:", raw_data)
            raw_response = self.llm.invoke(self.prompt.format(raw_data=raw_data))
            print("Raw LLM Output:", raw_response)
            
            # Clean and validate JSON
            cleaned_json = self.clean_json_output(raw_response)
            return self.output_parser.parse(cleaned_json)
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            print(f"Problematic JSON: {cleaned_json}")
            return None
        except Exception as e:
            print(f"Error parsing data: {str(e)}")
            return None

    def extract_tables_and_headers(self, html_content: str):
        """Extract table headers from HTML with encoding handling"""
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        
        extracted_headers = []
        for table in tables:
            headers = [
                th.get_text(strip=True)
                .replace(u'\xa0', ' ')
                .replace('"', '')  
                for th in table.find_all("th")
            ]
            extracted_headers.append(headers if headers else ["unknown"])
        
        return extracted_headers





table_parser = TableDataParser()


html_content = call_build_block()
if not html_content:
    print("Error: No HTML content retrieved!")
    exit()


html_tables_heads = table_parser.extract_tables_and_headers(html_content)

if not html_tables_heads:
    print("Error: No tables found in HTML!")
    exit()

print("Extracted Headers:", html_tables_heads)


parsed_data = table_parser.parse_company_data(html_tables_heads[0])


if parsed_data:
    print(parsed_data.model_dump_json(indent=2))
else:
    print("Failed to process Table")








 