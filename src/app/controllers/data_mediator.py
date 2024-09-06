from app.models.data_processor import DataProcessor
from app.models.matrix_profile_model import MatrixProfile
import pandas as pd
import sqlite3
import re

class DataMediator():
    """ The data mediator class object is to be used to store the logic for operations which require
    accessing the database
    """
    def __init__(self, file_path, database, data_processor, matrix_profile_model):
        self.db = database
        self.file_path = file_path
        self.data_processor = data_processor
        self.current_tab = None
        self.matrix_profile_model = matrix_profile_model
        self.previous_nodes = None
        self.sequence = None

    def _load_nodes(self):
        """ Calculates the node counts """
        query = f'''
        SELECT node_id, COUNT(signal_id) FROM {self.db.sanitise(self.current_tab)}_node_table
        '''
        cursor = self.db.cursor
        cursor.execute(query)
        result = cursor.fetchall()

        nodes = pd.DataFrame(result, columns=['node_id', 'count'])

        return nodes

    def get_node_count_and_labels(self):
        """ Calculate the node counts and returns a list of the number of signals in each node """
        query = f'''
        SELECT node_id, COUNT(signal_id) FROM {self.db.sanitise(self.current_tab)}_node_table
        GROUP BY node_id
        '''
        cursor = self.db.cursor
        cursor.execute(query)
        result = cursor.fetchall()
        
        nodes = pd.DataFrame(result, columns=['node_id', 'count'])
        count = nodes['count'].tolist()
        labels = nodes['node_id'].tolist()

        return count, labels

    def get_signals_in_node(self, node):
        """ Returns the signals in a node """
        signals_in_node = self.previous_nodes[self.previous_nodes['node_id'] == node]
        signals_in_node = signals_in_node['signal_id'].tolist()

        return signals_in_node
    
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
        """ Returns the number of cells in the current tab """
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

    def _get_signal_data(self, signal_id, cursor):
        """ Queries the database for the signal data of 1 signal"""
            
        sanitised = self.db.sanitise(self.current_tab)
        signal_table = f'{sanitised}_signal_table'

        query = f'''
        SELECT signal_idxs FROM {signal_table}
        WHERE signal_id = ?
        '''
        cursor.execute(query, (signal_id,))
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

    def _create_signal_df(self, cursor=None):
        """ Creates a dataframe of signals for a tab """

        if cursor == None:
            cursor = self.db.cursor

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
        
        while True:

            if self.current_tab is not None:
                conn, cursor = self.db.connect()
                self.sequence = self._get_all_cells(cursor)     
                for cell_id in self.sequence:

                    # check if the cell has already been processed
                    if self._is_cell_processed(cell_id, cursor):
                        # query for previous nodes
                        self.previous_nodes = self._get_previous_nodes(cursor, conn)
                        continue

                    # get the cell data and calculate the signals
                    cell_data = self.get_cell_data(cell_id, cursor)
                    signals_in_cell = self.matrix_profile_model.calculate_signals(cell_data)

                    # check if the current cell has no signals
                    if not signals_in_cell:
                        self._update_cell_processed(cell_id, cursor, conn)
                        continue

                    else:
                        # insert the signals into the database
                        last_signal_id = self._check_for_signals(cursor)
                        for signal in signals_in_cell:
                            signal_idxs = str(signal['id'].tolist())   
                            signal_id = last_signal_id + 1 if last_signal_id is not None else 0
                            self.db.insert_signal_data(signal_id, signal_idxs, cell_id, self.current_tab, cursor, conn)
                            last_signal_id = signal_id
                        self._update_cell_processed(cell_id, cursor, conn)
                        self._update_cell_signal(cell_id, cursor, conn)

                print('All cells processed')
                break

        return None
    
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

    def _update_cell_signal(self, cell_id, cursor, conn):
            
        """ Updates the cell to processed """
        query = f'''
        UPDATE {self.db.sanitise(self.current_tab)}_cell_table
        SET has_signal = TRUE
        WHERE cell_id = ?
        '''
        cursor.execute(query, (cell_id,))
        conn.commit()

    def _get_previous_nodes(self, cursor, conn):

        """ Returns the previous nodes """
        query = f'''
        SELECT * FROM {self.db.sanitise(self.current_tab)}_node_table
        '''
        cursor.execute(query)

        result = cursor.fetchall()

        previous_nodes = pd.DataFrame(result, columns=['node_id', 'signal_id'])
        
        return previous_nodes

    def _get_all_cells(self, cursor):
        """ Returns all the cell ids as a list of strings """
        query = f'''
        SELECT cell_id FROM {self.db.sanitise(self.current_tab)}_cell_table
        '''
        cursor.execute(query)
        result = cursor.fetchall()

        cells = [str(cell[0]) for cell in result]

        return cells
    
    def get_processed_cells(self, cursor=None):

        """ Returns all the cells which have been processed """
        if cursor is None:
            cursor = self.db.cursor
        
        query = f'''
        SELECT cell_id FROM {self.db.sanitise(self.current_tab)}_cell_table
        where processed = TRUE
        '''

        cursor.execute(query)
        result = cursor.fetchall()
        
        cells = [str(cell[0]) for cell in result]

        return cells
    
    def get_cells_with_signals(self, cursor=None):
            
        """ Returns all the cells which have signals """
        if cursor is None:
            cursor = self.db.cursor
        
        query = f'''
        SELECT cell_id FROM {self.db.sanitise(self.current_tab)}_cell_table
        where has_signal = TRUE
        '''

        cursor.execute(query)
        result = cursor.fetchall()
        
        cells = [str(cell[0]) for cell in result]

        return cells

    def run_group_by_length(self):
        signal_df = self._create_signal_df()
        signal_data = []

        for signal in signal_df['signal_id']:
            data = self._get_signal_data(signal, cursor=self.db.cursor)
            y_values = data[self.current_tab]
            signal_data.append({'signal_id': signal, 'data': y_values})

        signal_data_df = pd.DataFrame(signal_data)
        signal_data_df = signal_df.merge(signal_data_df, on='signal_id') 

        df = self.matrix_profile_model.calculate_group_by_length(signal_data_df)

        return df
    
    def run_group_by_amplitude(self):
        signal_df = self._create_signal_df()
        signal_data = []

        for signal in signal_df['signal_id']:
            data = self._get_signal_data(signal, cursor=self.db.cursor)
            y_values = data[self.current_tab]
            signal_data.append({'signal_id': signal, 'data': y_values})
        
        signal_data_df = pd.DataFrame(signal_data)
        signal_data_df = signal_df.merge(signal_data_df, on='signal_id')

        df = self.matrix_profile_model.calculate_group_by_amplitude(signal_data_df)

        return df

    def get_line_data(self, df):
        line_data = pd.DataFrame(columns=['node_id', 'cluster', 'data'])
        for node in df['node_id'].unique():
            for cluster in df[df['node_id'] == node]['cluster'].unique():
                # only need 1 signal from each cluster get signal_id
                signal_id = df[(df['node_id'] == node) & (df['cluster'] == cluster)]['signal_id'].iloc[0]
                signal_id = int(signal_id)
                signal_data = self._get_signal_data(signal_id, cursor=self.db.cursor)
                y_values = signal_data[self.current_tab].tolist()
                new_row = pd.DataFrame([{'node_id': node, 'cluster': cluster, 'data': y_values}])
                line_data = pd.concat([line_data, new_row], ignore_index=True)

        return line_data
    
    def extract_start(self, label):
        match = re.match(r'(\d+\.\d+)', label)
        return float(match.group()) if match else float('inf')

    def get_cell_start_as_time(self, cell_id):
        """ Returns the start of the cell """
        query = f'''
        SELECT cell_id_start FROM {self.db.sanitise(self.current_tab)}_cell_table
        WHERE cell_id = ?
        '''
        cursor = self.db.cursor
        cursor.execute(query, (cell_id,))
        result = cursor.fetchone()[0]
        result = int(result) + 1

        query2 = f'''
        SELECT Time_s_ FROM {self.db.sanitise(self.current_tab)}_data_table
        WHERE id = ?
        '''
        cursor.execute(query2, (result,))

        time = cursor.fetchone()[0]

        return time