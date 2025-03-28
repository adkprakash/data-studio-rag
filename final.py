from parsing_on_batch import process_html_and_extract_data
from extract_table import create_dataframes
import json
import pandas as pd
import numpy as np
import os
import time

class FinalDataframe:
    def __init__(self):
        # Assuming create_dataframes returns lists of header and body DataFrames per table
        self.header_dfs, self.body_dfs = create_dataframes()
        self.llm_output_list = process_html_and_extract_data()
        self.total_tables = len(self.header_dfs)
        self.processed_dfs = []

    def process_all_tables(self):
        for i in range(self.total_tables):
            header_df = self.header_dfs[i]
            body_df = self.body_dfs[i]
            llm_output = self.llm_output_list[i]

            # Process each table with its corresponding LLM output
            merged_df = self.add_header(llm_output, header_df, body_df)
            if merged_df is not None:
                data_dict = json.loads(llm_output)
                merged_df = self.assign_thread_size(data_dict, merged_df)
                merged_df = self.assign_material_surface(data_dict, merged_df)
                final_df = self.merge_header(merged_df)
                self.processed_dfs.append(final_df)
            else:
                print(f"Skipping table {i+1} due to processing error.")

    @staticmethod
    def add_header(llm_output, header_df, body_df):
        try:
            parsed_dict = json.loads(llm_output)
            keys = list(parsed_dict.keys())

            # Create a copy to avoid modifying the original DataFrame
            header_df = header_df.copy()
            current_cols = header_df.shape[1]

            # Add new columns from LLM output
            for idx, key in enumerate(keys):
                new_col_name = str(current_cols + idx + 1)
                header_df[new_col_name] = np.nan
                header_df[new_col_name] = header_df[new_col_name].astype('object')
                header_df.iloc[-1, header_df.columns.get_loc(new_col_name)] = str(key)

            # Combine header and body
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

        # Remove rows that are thread size markers
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

        # Remove rows that are material markers
        df = df[~df[first_col].isin(materials)].reset_index(drop=True)
        return df

    def merge_header(self, processed_df):
        # Align columns between original header and processed DataFrame
        header_columns = self.header_dfs[0].columns.tolist()  # Adjust index if needed
        processed_columns = processed_df.columns.tolist()

        # Ensure header has same columns as processed_df, fill missing with NaN
        aligned_header = pd.DataFrame(columns=processed_columns)
        for col in header_columns:
            if col in processed_columns:
                aligned_header[col] = self.header_dfs[0].get(col, np.nan)

        # Combine header rows with processed data
        full_df = pd.concat([aligned_header, processed_df], ignore_index=True)
        return full_df

def save_dataframes_to_excel(dataframes, filename="./mcmaster_excel/test_time_1.xlsx"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not dataframes:
        print("No data to save")
        return

    try:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            for idx, df in enumerate(dataframes, 1):
                df.to_excel(writer, sheet_name=f"Table_{idx}", index=False)
        print(f"Successfully saved to {filename}")
    except Exception as e:
        print(f"Save error: {e}")


if __name__ == "__main__":
   
   
    start_time = time.time()

    # Initialize and process the data
    final_data = FinalDataframe()
    final_data.process_all_tables()
    save_dataframes_to_excel(final_data.processed_dfs)

    # Record the end time
    end_time = time.time()

    # Calculate the processing time
    processing_time = end_time - start_time

    # Print the processing time
    print(f"Processing time: {processing_time:.2f} seconds")