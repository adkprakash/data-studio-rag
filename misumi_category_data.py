from clean_html import call_build_block
from misumi_extract_table import get_misumi_data
import os
import time
import pandas as pd 

def process_files_in_folder(folder_path):
    
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    all_dataframes=[]
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        
        if os.path.isfile(file_path):
            cleaned_html_data=call_build_block(file_path)
            dataframe=get_misumi_data(cleaned_html_data)

            all_dataframes.append(dataframe)

        else:
            print(f"Skipping directory: {filename}")
    return all_dataframes

def merge_all_dataframes(all_dataframes):

    merged_df = pd.concat(all_dataframes, axis=0, ignore_index=True, sort=False)
    return merged_df



def get_all_data():
    start_time = time.time()
    all_dataframes=process_files_in_folder("misumi_usa")
    merged_dataframe=merge_all_dataframes(all_dataframes)
    print(merged_dataframe)
    end_time = time.time()
    print(f"Processing time: {end_time - start_time:.2f} seconds")
    return merged_dataframe


get_all_data()

