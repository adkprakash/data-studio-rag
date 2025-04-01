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
            header_df = self.header_dfs[i].copy()
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

            head_row_len = header_df.shape[0]
            no_cols = header_df.shape[1]

            # Convert new columns to 'object' dtype before assignment
            for i, key in enumerate(keys):
                new_column_name = str(no_cols + 1)
                header_df[new_column_name] = np.nan
                header_df[new_column_name] = header_df[new_column_name].astype('object')
                header_df.loc[head_row_len - 1, new_column_name] = key
                no_cols += 1

            # Merge header and body
            combined = pd.concat([header_df.iloc[[-1]], body_df], ignore_index=True)
            combined.columns = combined.iloc[0]  # Set new column headers
            combined = combined.drop(0).reset_index(drop=True)  # Drop the first row
            combined.columns = combined.columns.str.strip()  # Clean column names

            return combined
        except Exception as e:
            print(f"Error adding header: {e}")
            return None

    @staticmethod
    def assign_thread_size(data_dict, dataframe):
        thread_sizes = set(data_dict.get('thread_size', []))  # Convert list to set for fast lookup
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
        materials = set(data_dict.get('material_surface', []))  # Convert list to set
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
    def merge_header(header_df, processed_df):
        try:
            header_columns = header_df.columns.tolist()
            assign_columns = processed_df.columns.tolist()

            # Create a mapping between the header and processed columns
            column_mapping = {header_col: assign_col for header_col, assign_col in zip(header_columns, assign_columns)}

            # Rename header columns
            header_df_renamed = header_df.rename(columns=column_mapping)

            # Merge both DataFrames
            merged_df = pd.concat([header_df_renamed, processed_df], axis=0, ignore_index=True)

            # Rename columns numerically
            merged_df.columns = range(len(merged_df.columns))

            return merged_df
        except Exception as e:
            print(f"Error merging header: {e}")
            return None


def save_dataframes_to_excel(dataframes, filename="./mcmaster_excel/test_time_1.xlsx"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not dataframes:
        print("No data to save")
        return

    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for idx, df in enumerate(dataframes, 1):
                if not df.empty:
                    sheet_name = f"Table_{idx}"[:31]  # Ensure sheet name doesn't exceed Excel limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    print(f"Skipping empty DataFrame at index {idx}")
        print(f"Successfully saved to {filename}")
    except Exception as e:
        print(f"Save error: {e}")


if __name__ == "__main__":
    start_time = time.time()

    final_data = FinalDataframe()
    final_data.process_all_tables()
    save_dataframes_to_excel(final_data.processed_dfs)

    end_time = time.time()
    print(f"Processing time: {end_time - start_time:.2f} seconds")
