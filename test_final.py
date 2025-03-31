from parsing_on_batch import process_html_and_extract_data
from extract_table import create_dataframes
import json
import pandas as pd
import numpy as np
import os
import time

class FinalDataframe:
    def __init__(self):
        self.header_dfs, self.body_dfs = create_dataframes()
        self.llm_output_list = process_html_and_extract_data()
        self.total_tables = len(self.header_dfs)
        self.processed_dfs = []

    def process_all_tables(self):
        for i in range(self.total_tables):
            header_df = self.header_dfs[i]
            body_df = self.body_dfs[i]
            llm_output = self.llm_output_list[i]

            merged_df = self.add_header(llm_output, header_df, body_df)
            if merged_df is not None:
                data_dict = json.loads(llm_output)
                merged_df = self.assign_thread_size(data_dict, merged_df)
                merged_df = self.assign_material_surface(data_dict, merged_df)
                final_df = self.merge_header(header_df, merged_df)
                self.processed_dfs.append(final_df)
            else:
                print(f"Skipping table {i+1} due to processing error.")

    @staticmethod
    def add_header(llm_output, header_df, body_df):
        try:
            parsed_dict = json.loads(llm_output)
            keys = list(parsed_dict.keys())

            header_df = header_df.copy()
            current_cols = header_df.shape[1]

            for idx, key in enumerate(keys):
                new_col_name = str(current_cols + idx + 1)
                header_df[new_col_name] = np.nan
                header_df[new_col_name] = header_df[new_col_name].astype('object')
                header_df.iloc[-1, header_df.columns.get_loc(new_col_name)] = str(key)

            combined = pd.concat([header_df.iloc[[-1]], body_df], ignore_index=True)
            combined.columns = combined.iloc[0]
            combined = combined.drop(0).reset_index(drop=True)
            combined.columns = combined.columns.str.strip()
            return combined
        except Exception as e:
            print(f"Error adding header: {e}")
            return None

    @staticmethod
    def assign_thread_size(data_dict, dataframe):
        thread_sizes = data_dict.get('thread_size', [])
        if not thread_sizes:
            return dataframe

        df = dataframe.copy()
        first_col = df.columns[0]
        df['thread_size'] = None
        current_size = None

        for idx, row in df.iterrows():
            value = row[first_col]
            if value in thread_sizes:
                current_size = value
            df.at[idx, 'thread_size'] = current_size

        df = df[~df[first_col].isin(thread_sizes)].reset_index(drop=True)
        return df

    @staticmethod
    def assign_material_surface(data_dict, dataframe):
        materials = data_dict.get('material_surface', [])
        if not materials:
            return dataframe

        df = dataframe.copy()
        first_col = df.columns[0]
        df['material_surface'] = None
        current_material = None

        for idx, row in df.iterrows():
            value = row[first_col]
            if value in materials:
                current_material = value
            df.at[idx, 'material_surface'] = current_material

        df = df[~df[first_col].isin(materials)].reset_index(drop=True)
        return df
    
    @staticmethod
    def merge_header(header_df, assign_material_surface_df):
        try:
            header_columns = header_df.columns.tolist()
            assign_columns = assign_material_surface_df.columns.tolist()

            column_mapping = {header_col: assign_col for header_col, assign_col in zip(header_columns, assign_columns)}
            header_df_renamed = header_df.rename(columns=column_mapping)
            
            merged_df = pd.concat([header_df_renamed, assign_material_surface_df], axis=0, ignore_index=True)
            
            value = 0
            for header in merged_df.columns:
                merged_df.rename(columns={header: value}, inplace=True)
                value += 1
            
            print(merged_df.head())
            return merged_df
        except Exception as e:
            print(f"Error merging header: {e}")
            return None

if __name__ == "__main__":
    start_time = time.time()
    final_data = FinalDataframe()
    final_data.process_all_tables()
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Processing time: {processing_time:.2f} seconds")
