# This script is for the processing of the data and inputing it into the database
import pandas as pd
import dask.dataframe as dd

class DataProcessor():
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = dd.read_csv(file_path)

    def get_data_headers(self):
        return list(self.data.columns)
    
