# This script is for the processing of the data and sending it to the database to be input
import pandas as pd
import dask.dataframe as dd
import os
from app.models.matrix_profile import MatrixProfile
from app.config import CHUNK_SIZE

class DataProcessor():
    def __init__(self, file_path):
        self.file_path = file_path
        self.chunk_size = CHUNK_SIZE
        self._generate_metadata()
        self.matrix_profile = MatrixProfile()

    def get_headers(self):
        """Returns the headers of the data file without Time (s)"""
        headers = pd.read_csv(self.meta_data_path, header=None).values.tolist()
        flattened_headers = [header[0] for header in headers]
        return flattened_headers[1:]

    def _read_data(self):
        data = pd.read_csv(self.file_path, chunksize=self.chunk_size)
        return data

    def get_cells_data(self, header):
        """Function to input data for cells in db. The function should check metadata
            to see which files have already been parsed into the db.
        """
        chunks = self._read_data()
        cell_ids = []
        cell_id_starts = []
        cell_id_ends = []
        signal_ids = []

        for i, chunk in enumerate(chunks):
            cell_ids.append(f"cell_{i}")
            cell_id_starts.append(chunk.index[0])
            cell_id_ends.append(chunk.index[-1])
            signal_ids.append('signal1') # change to get signal ids from matrix profile

        return cell_ids, cell_id_starts, cell_id_ends, signal_ids


    def _generate_metadata(self):
        data = pd.read_csv(self.file_path)
        base, ext = os.path.splitext(self.file_path)
        self.meta_data_path = f"{base}_metadata{ext}"
        if os.path.exists(self.meta_data_path):
            return
        else:
            column_list = data.columns.tolist()
            meta_data_df = pd.DataFrame(column_list)
            meta_data_df.to_csv(self.meta_data_path, index=False, header=False)

    def read_chunk(self, start, end):
        start = int(start)
        end = int(end)
        data = pd.read_csv(self.file_path, skiprows=range(1, start), nrows=end-start, header=None)
        headers = self.get_headers()
        headers.insert(0, 'Time(s)')
        data.columns = headers
        return data

    def read_data(self):
        data = pd.read_csv(self.file_path)
        return data