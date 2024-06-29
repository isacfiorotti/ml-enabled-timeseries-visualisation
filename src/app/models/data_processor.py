# This script is for the processing of the data and inputing it into the database
import pandas as pd
import dask.dataframe as dd
import os

class DataProcessor():
    def __init__(self, file_path):
        self.file_path = file_path
        self._generate_metadata()

    def get_headers(self):
        """Returns the headers of the data file without Time (s)"""
        headers = pd.read_csv(self.meta_data_path, header=None).values.tolist()
        flattened_headers = [header[0] for header in headers]
        return flattened_headers[1:]

    def read_data(self):
        data = dd.read_csv(self.file_path)
        return data

    def _generate_metadata(self):
        base, ext = os.path.splitext(self.file_path)
        self.meta_data_path = f"{base}_metadata{ext}"
        if os.path.exists(self.meta_data_path):
            return
        else:
            data = self.read_data()
            column_list = data.columns.tolist()
            meta_data_df = pd.DataFrame(column_list)
            meta_data_df.to_csv(self.meta_data_path, index=False, header=False)