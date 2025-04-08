import json
import re
from bs4 import BeautifulSoup
from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  
from pydentic_classes import GenericPartsData
from clean_html import call_build_block
from dotenv import load_dotenv
import os  

class TableDataParser:
    def __init__(self,api_key):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=api_key,  
            # base_url="...",
            # organization="...",
            # other params...
        )
        self.output_parser = PydanticOutputParser(pydantic_object=GenericPartsData)

        self.prompt = PromptTemplate(
            template="""Extract the following fields as raw JSON. 
            **DO NOT INCLUDE ANY TEXT BEFORE/AFTER THE JSON**. 

            Fields to extract:
            - thread_size: List of thread sizes (e.g., "2-56", "M6-0.5", "1/4-20 UNC")
            - material_surface: List of materials (e.g., "Alloy Steel", "Black-Oxide Alloy Steel","Double Nut")

            Rules:
            1. Output **ONLY** valid JSON.
            2. Ensure there are **NO** extra quotation marks around the values (e.g., not `""4-40""`, but `"4-40"`).
            3. Ensure that the values are directly enclosed in double quotes without any additional formatting.
            4. No explanations, comments, or formatting outside the JSON.
            5. If no material is found, use `"material_surface": ["unknown"]`.
            6. Do not extract data from the examples given in the prompt.
            7. Some of the materials surface are made up of more than one materials.

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

    def clean_json_output(self, raw_json: str) -> str:
        if not isinstance(raw_json, str):
            raise TypeError(f"Expected a string, but got {type(raw_json)} with value: {raw_json}")

        json_match = re.search(r'\{.*\}', raw_json, flags=re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in output")
        
        json_str = json_match.group()

        json_str = re.sub(
            r'"thread_size": \[(.*?)\]',
            lambda m: '"thread_size": [' + ', '.join(
                ['"' + s.strip().replace('"', '').replace('\\', '') + '"'  
                for s in m.group(1).split(',') if s.strip()]
            ) + ']',
            json_str,
            flags=re.DOTALL
        )

        json_str = json_str.replace(u'\xa0', ' ')
        
        return json_str


    def parse_company_data(self, raw_data: list) -> GenericPartsData:
        try:
            if isinstance(raw_data, list):
                
                raw_data = "\n".join(raw_data)
                
            
            formatted_data = "TABLE HEADERS:\n" + raw_data
            
            return self.chain.invoke({"raw_data": formatted_data})
        except Exception as e:
            print(f"Parser error: {str(e)}")
            return GenericPartsData(thread_size=[], material_surface=["unknown"])
    def process_tables_batch(self, tables: list) -> list:
        
        results = []
        for header_group in tables:
            if header_group:  # Check if headers exist
                raw_data = "\n".join(header_group)
                try:
                    result = self.parse_company_data(raw_data)
                    if result:
                        results.append(result.model_dump_json(indent=2))
                except Exception as e:
                    print(f"Skipping header group due to error: {str(e)}")
        return results

    
    def extract_tables_and_headers(self, html_content: str):
        
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        
        extracted_headers = []
        for table in tables:
            # Get all <th> text content
            headers = [
                th.get_text(strip=True).replace(u'\xa0', ' ') 
                for th in table.find_all("th")
            ]
            if headers:
                extracted_headers.append(headers)
        
        return extracted_headers
def get_openai_api_key():
    load_dotenv()
    api_key=os.getenv("openai_api_key")

    return api_key

def process_html_and_extract_data():
    api_key=get_openai_api_key()
    table_parser = TableDataParser(api_key)

    html_content = call_build_block()  
    if not html_content:
        print("Error: No HTML content retrieved!")
        return []

    
    html_tables_heads = table_parser.extract_tables_and_headers(html_content)

    if not html_tables_heads:
        print("Error: No tables found in HTML!")
        return []

    
    parsed_data = table_parser.process_tables_batch(html_tables_heads)

    
    return parsed_data



