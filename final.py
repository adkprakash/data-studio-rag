from parsing_on_batch import process_html_and_extract_data
from extract_table import create_dataframes
import json
import pandas as pd
import numpy as np 

class FinalDataframe:
    def __init__(self):
        self.header_df,self.body_df=create_dataframes()
        self.llm_output_list=process_html_and_extract_data()
        self.total_table=len(self.header_df)
    
    def add_header(llm_output,header_df,body_df):
        parsed_dict = json.loads(llm_output)
        keys = list(parsed_dict.keys())
        head_row_len=header_df.shape[0]
        no_cols=header_df.shape[1]

        
        for i in range(len(keys)):
            new_column_name = f"{no_cols + 1}" 
            header_df[new_column_name] = np.nan  
            header_df.loc[head_row_len-1, new_column_name] = keys[i]  
            no_cols += 1 

        merged_df = pd.concat([header_df.iloc[[-1]], body_df], ignore_index=True)
        
        
        merged_df.columns = merged_df.iloc[0]  
        merged_df = merged_df.drop([0])
        merged_df = merged_df.reset_index(drop=True)
        merged_df.columns = merged_df.columns.str.strip()

        return merged_df
    
    def assign_thread_size(data_dict, dataframe):
        
        thread_sizes = data_dict.get('thread_size', [])
        
        
        dataframe['thread_size'] = None
        current_thread = None
        
        
        first_col_name = dataframe.columns[0]
        
        
        for index, row in dataframe.iterrows():
            first_col_value = row[first_col_name]
            if first_col_value in thread_sizes:
                current_thread = first_col_value
            dataframe.at[index, 'thread_size'] = current_thread
        
        
        dataframe = dataframe[~dataframe[first_col_name].isin(thread_sizes)].reset_index(drop=True)
        
        return dataframe
    
    def assign_material_surface(data_dict, dataframe):
        
        material_surfaces = data_dict.get('material_surface', [])
        
        
        dataframe['material_surface'] = None
        current_thread = None
        
        
        first_col_name = dataframe.columns[0]
        
        
        for index, row in dataframe.iterrows():
            first_col_value = row[first_col_name]
            if first_col_value in material_surfaces:
                current_thread = first_col_value
            dataframe.at[index, 'material_surface'] = current_thread
        
       
        dataframe = dataframe[~dataframe[first_col_name].isin(material_surfaces)].reset_index(drop=True)
        
        return dataframe
    
    def merge_header():


        

