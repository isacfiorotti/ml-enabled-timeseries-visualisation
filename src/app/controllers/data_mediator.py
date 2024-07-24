from app.models.data_processor import DataProcessor
from app.models.matrix_profile_model import MatrixProfile
import pandas as pd
import sqlite3
import time
import threading

class DataMediator():
    """ The data mediator class object is to be used as a way to cache the data that is to be displayed to prevent repeated queries and store the logic for 
    accessing the database
    """
    def __init__(self, file_path, database, data_processor, matrix_profile_model):
        self.nodes, self.node_count, self.sequence, self.signals = self._load_from_database()
        self.db = database
        self.file_path = file_path
        self.data_processor = data_processor
        self.current_tab = None
        self.matrix_profile_model = matrix_profile_model

    def _load_from_database(self):
        # Test functionality not actual implementation of _load_from_database
        nodes = {
            'node1':['signal1', 'signal2'],
            'node2':['signal3'],
            'node3':['signal4'],
            'node4':['signal5'],
            'node5':['signal6']
        }

        node_count = {
            'node1':2,
            'node2':1,
            'node3':1,
            'node4':1,
            'node5':1
        }

        sequence = {
            'cell_0':['signal1'],
            'cell_1':['signal5'],
            'cell_2':['signal2'],
            'cell_3':['signal3'],
            'cell_4':['signal4']
        }

        signals = {
            'signal1':'cell_0',
            'signal2':'cell_2',
            'signal3':'cell_3',
            'signal4':'cell_4',
            'signal5':'cell_5',
            'signal6':'cell_7'
        }

        return nodes, node_count, sequence, signals

    def get_signals_in_node(self, node):
        """ Returns dictionary containing signals grouped into nodes 
        """
        return list(self.nodes[node])
    
    def get_nodes(self):
        """ Returns a list of nodes
        """
        return list(self.nodes.keys())

    def get_node_counts(self):
        """ Returns list of counts for all nodes
        """
        return list(self.node_count.values())

    def get_signal_cell(self, signal):
        """ Returns the cell associated with a node
        """
        return self.signals[signal]
    
    def get_headers(self):
        headers = self.data_processor.get_headers()
        return headers
    
    def get_grid_size(self):
        sanitised = self.db.sanitise(self.current_tab)
        cursor = self.db.cursor.execute(f'SELECT COUNT(*) FROM {sanitised}_cell_table')
        grid_size = cursor.fetchone()[0]
        return grid_size
    
    def _set_current_tab(self, current_tab):
        self.current_tab = current_tab

    def get_cell_data(self, cell_id, cursor=None):
        """ Returns the data for a cell """

        if cursor is None:
            cursor = self.db.cursor

        sanitised = self.db.sanitise(self.current_tab)

        query1 = f'''
        SELECT cell_id_start, cell_id_end FROM {sanitised}_cell_table
        WHERE cell_id = ?
        '''
        cursor.execute(query1, (cell_id,))
        result = cursor.fetchone()

        cell_id_start, cell_id_end = result

        cell_id_start, cell_id_end = int(cell_id_start), int(cell_id_end)

        query2 = f'''
        SELECT * FROM {sanitised}_data_table
        WHERE id >= ? AND id <= ?
        '''
        cursor.execute(query2, (cell_id_start, cell_id_end))
        rows = cursor.fetchall()

        data = pd.DataFrame(rows, columns=['id', 'Time(s)', f'{self.current_tab}'])

        return data

    def _get_blocks(self, cell_id, cursor):
        """ Returns the blocks for a cell """
        cell_data = self.get_cell_data(cell_id, cursor)
        blocks = self.matrix_profile_model.calculate_signal_blocks(cell_data)
        return blocks, cell_data
    
    def _get_groups(self, blocks, cell_data, current_tab):
        """ Returns the groups for a cell """
        groups = self.matrix_profile_model.calculate_signal_groups(blocks, cell_data, current_tab)
        return groups
    
    def run_matrix_profile_operations(self):
        test_sequence = ['cell_0', 'cell_1', 'cell_2', 'cell_3', 'cell_4']

        while True:
            if self.current_tab is not None:
                # Create new connection to database within the thread
                conn, cursor = self.db.connect()
                try:
                    for cell_id in test_sequence:
                        blocks, cell_data = self._get_blocks(cell_id, cursor)
                        groups = self._get_groups(blocks, cell_data, self.current_tab)
                        time.sleep(1)
                finally:
                    conn.close() 


