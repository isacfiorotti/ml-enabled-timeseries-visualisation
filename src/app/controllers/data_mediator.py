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
        self.db = database
        self.file_path = file_path
        self.data_processor = data_processor
        self.current_tab = None
        self.matrix_profile_model = matrix_profile_model
        self.previous_nodes = None
        self.nodes, self.node_count, self.sequence, self.signals = None, None, None, None

    def _load_tab_from_database(self):
        """ Loads the tab from the database """
        nodes = {}
        node_count = {}
        sequence = []
        signals = {}

        conn, cursor = self.db.connect()
        try:
            header = self.db.sanitise(self.current_tab)
            node_table = f'{header}_node_table'
            signal_table = f'{header}_signal_table'

            query1 = f'''
            SELECT * FROM {node_table}
            '''
            cursor.execute(query1)
            result = cursor.fetchall()

            for row in result:
                node_id, signal_ids = row
                nodes[node_id] = signal_ids
                sequence.append(node_id)

            query2 = f'''
            SELECT * FROM {signal_table}
            '''
            cursor.execute(query2)
            result = cursor.fetchall()

            for row in result:
                signal_id, signal_idxs, cell_id = row
                signals[signal_id] = signal_idxs

            #node count is the number of signals in each node
            query3 = f'''
            SELECT node_id, signal_ids_in_node FROM {node_table}
            '''
            cursor.execute(query3)
            result = cursor.fetchall()
            
            for row in result:
                node_id, signal_ids_in_node = row
                signal_ids = signal_ids_in_node.split(',')
                node_count[node_id] = len(signal_ids)

            node_count = list(node_count.values())

        finally:
            conn.close()

        return nodes, node_count, sequence, signals

    def get_signals_in_node(self, node):
        """ Returns the signals in a node """

        signals_in_node = self.nodes[node]
        signals_in_node = signals_in_node.split(',')
        signals_in_node = [int(signal) for signal in signals_in_node]

        return signals_in_node
    
    def get_nodes(self):
        """ Returns a list of nodes
        """
        nodes = self.nodes
        return nodes

    def get_node_counts(self):
        """ Returns list of counts for all nodes
        """
        node_count = self.node_count

        return node_count

    def get_signal_cell(self, signal_id, cursor=None):
        """ Returns the cell that the signal is in
        """
        if cursor is None:
            cursor = self.db.cursor

        query = f'''
        SELECT cell_id FROM {self.db.sanitise(self.current_tab)}_signal_table
        WHERE signal_id = ?
        '''
        cursor.execute(query, (signal_id,))
        result = cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return None

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

    def _check_for_signals(self, cursor):
        """Checks for existing signals in the SQL database and returns the number of the last one"""

        sanitised = self.db.sanitise(self.current_tab)
        signal_table = f'{sanitised}_signal_table'
        query = f'''
        SELECT MAX(signal_id) FROM {signal_table}
        '''
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            last_signal_id = result[0] if result[0] is not None else None
            print('Checking for signals...')
        except sqlite3.OperationalError:
            last_signal_id = None

        return last_signal_id
    
    def _check_for_nodes(self, cursor):
        """Checks for existing nodes in the SQL database and returns the number of the last one"""

        sanitised = self.db.sanitise(self.current_tab)
        node_table = f'{sanitised}_node_table'
        
        query = f'''
        SELECT MAX(node_id) FROM {node_table}
        '''

        cursor.execute(query)
        result = cursor.fetchone()

        last_node_id = result[0] if result[0] is not None else 0
        print('Checking for nodes...')

        return last_node_id

    def _get_signal_blocks(self, cell_id, cursor):
        """ Returns the signal_blocks for a cell """

        last_signal_id = self._check_for_signals(cursor)
        print('Last signal id:', last_signal_id)

        cell_data = self.get_cell_data(cell_id, cursor)
        
        signal_blocks = self.matrix_profile_model.calculate_signal_blocks(cell_data)

        return signal_blocks, cell_data

    def _get_signals(self, cursor):
        """ Returns the signals for a tab """

        sanitised = self.db.sanitise(self.current_tab)
        signal_table = f'{sanitised}_signal_table'

        query = f'''
        SELECT * FROM {signal_table}
        '''

        cursor.execute(query)
        result = cursor.fetchall()

        return result

    def _get_signal_data(self, signal_id, cell_id, cursor):
        """ Queries the database for the signal data of 1 signal"""
            
        sanitised = self.db.sanitise(self.current_tab)
        signal_table = f'{sanitised}_signal_table'

        query = f'''
        SELECT signal_idxs FROM {signal_table}
        WHERE signal_id = ? AND cell_id = ?
        '''
        cursor.execute(query, (signal_id, cell_id))
        result = cursor.fetchone()

        if result is None:
            print('No signal data found')
            return None
        
        else:

            signal_idxs = list(map(int, result[0].strip('[]').split(',')))

            query2 = f'''
            SELECT * FROM {sanitised}_data_table
            WHERE id IN ({', '.join('?' for _ in signal_idxs)})
            '''
            cursor.execute(query2, signal_idxs)

            rows = cursor.fetchall()

            signal_data = pd.DataFrame(rows, columns=['id', 'Time(s)', f'{self.current_tab}'])

        return signal_data

    def _create_signal_df(self, cursor):
        """ Creates a dataframe of signals for a tab """

        signals = self._get_signals(cursor)
        signal_df = pd.DataFrame(signals, columns=['signal_id', 'signal_idxs', 'cell_id'])

        return signal_df

    def _get_signals_in_cell(self, cell_id, cursor=None):
        """ Returns the signals in a cell """
        if cursor is None:
            cursor = self.db.cursor

        signal_df = self._create_signal_df(cursor)
        signals_in_cell = signal_df[signal_df['cell_id'] == cell_id]

        return signals_in_cell

    def run_matrix_profile_operations(self):
        test_sequence = ['cell_0', 'cell_1', 'cell_2', 'cell_3', 'cell_4']

        while True:
            if self.current_tab is not None:
                # Create new connection to database within the thread
                conn, cursor = self.db.connect()
                try:
                    for cell_id in test_sequence: # change to get_cells()
                        
                        print('Processing cell:', cell_id)

                        # add something to check if the cell has already been processed
                        if self._is_cell_processed(cell_id, cursor):
                            print('Cell already processed')
                            self.nodes, self.node_count, self.sequence, self.signals = self._load_tab_from_database()
                            self.previous_nodes = self.nodes
                            continue

                        signal_blocks, cell_data = self._get_signal_blocks(cell_id, cursor)
                        last_signal_id = self._check_for_signals(cursor)
                        signal_id = 0 if last_signal_id is None else last_signal_id + 1

                        for idx, signal_block in enumerate(signal_blocks):
                            start_time = signal_block['Time(s)'].iloc[0]
                            end_time = signal_block['Time(s)'].iloc[-1]
                            signal_data = cell_data[(cell_data['Time(s)'] >= start_time) & (cell_data['Time(s)'] <= end_time)]
                            signal_idxs = list(signal_data['id'])
                            signal_idxs = str(signal_idxs)
                            self.db.insert_signal_data(signal_id + idx, signal_idxs, cell_id, self.current_tab, cursor, conn)

                        self._update_cell_processed(cell_id, cursor, conn)
                        print('Cell processed')

                        last_node_id = self._check_for_nodes(cursor)
                        last_node_id = last_node_id + 1

                        if self.previous_nodes is None:
                            # Create the first set of nodes
                            signals_in_cell = self._get_signals_in_cell(cell_id, cursor)
                            signal_ids = list(signals_in_cell['signal_id'])
                            signal_data = []
                            for signal_id in signal_ids:
                                signal = self._get_signal_data(signal_id, cell_id, cursor)
                                signal_data.append(signal)

                            # Create the nodes
                            print('Creating nodes...')
                            nodes = self.matrix_profile_model.calculate_signal_nodes(signal_data, cell_data, self.current_tab)

                            # Insert the nodes into the database
                            for _, row in nodes.iterrows():
                                # convert signal_ids_in_node to string
                                row['signal_id'] = row['signal_id'].astype(str)
                                print('Inserting node data...')
                                self.db.insert_node_data(row['node_id'], row['signal_id'], self.current_tab, cursor, conn)

                            # Update the previous nodes
                            self.previous_nodes = nodes
                            # self.nodes, self.node_count, self.sequence, self.signals = self._load_tab_from_database()

                        else:

                            test_sequence = ['cell_0', 'cell_1', 'cell_2', 'cell_3', 'cell_4']
                            signals_in_previous_nodes = []  # Placeholder for fetched signal data
                            
                            # Query the database for all signals in previous nodes
                            for cell_id in test_sequence:
                                signals_in_cell = self._get_signals_in_cell(cell_id, cursor)
                                signal_ids = list(signals_in_cell['signal_id'])
                                signals_in_previous_nodes.extend(signal_ids)

                            # Create signal_data variable for all signals in previous nodes
                            signal_data = []
                            for signal_id in signals_in_previous_nodes:
                                signal_cell_id = self.get_signal_cell(signal_id, cursor)
                                signal = self._get_signal_data(signal_id, signal_cell_id, cursor)
                                signal_data.append(signal)

                            # Merge the previous nodes with the current nodes
                            print('Merging nodes...')
                            current_nodes = self.matrix_profile_model.calculate_signal_nodes(signal_data, cell_data, self.current_tab)
                            merged_nodes = self.matrix_profile_model.merge_nodes(self.previous_nodes, current_nodes, signal_data, self.current_tab)

                            # Insert the merged nodes into the database
                            for _, row in merged_nodes.iterrows():
                                # convert signal_ids_in_node to string
                                row['signal_id'] = str(row['signal_id'])
                                self.db.insert_node_data(row['node_id'], row['signal_id'], self.current_tab, cursor, conn)

                            # Update the previous nodes
                            self.previous_nodes = merged_nodes
                            # self.nodes, self.node_count, self.sequence, self.signals = self._load_tab_from_database()

                        time.sleep(0.01)

                    # break once all cells have been processed
                    print('All cells processed')
                    break

                finally:
                    conn.close()

    def _is_cell_processed(self, cell_id, cursor):
        """ Checks if a cell has already been processed """
        query = f'''
        SELECT processed FROM {self.db.sanitise(self.current_tab)}_cell_table
        WHERE cell_id = ?
        '''
        cursor.execute(query, (cell_id,))
        result = cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return False
        
    def _update_cell_processed(self, cell_id, cursor, conn):
        """ Updates the cell to processed """
        query = f'''
        UPDATE {self.db.sanitise(self.current_tab)}_cell_table
        SET processed = TRUE
        WHERE cell_id = ?
        '''
        cursor.execute(query, (cell_id,))
        conn.commit()