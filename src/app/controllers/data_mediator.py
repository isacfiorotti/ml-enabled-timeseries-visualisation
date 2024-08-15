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
        self.sequence = ['cell_0', 'cell_1', 'cell_2']

    def _load_tab_from_database(self):
        """ Loads the tab from the database """
        pass

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
        # TODO FIX THIS
        """ Returns the signals in a node """

        signals_in_node = self.nodes[node]
        signals_in_node = signals_in_node.split(',')
        signals_in_node = [int(signal) for signal in signals_in_node]

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
        
        while True:

            if self.current_tab is not None:      
                conn, cursor = self.db.connect()       
                for cell_id in self.sequence:
                    
                    print('Processing cell:', cell_id)

                    # check if the cell has already been processed
                    if self._is_cell_processed(cell_id, cursor):
                        print('Cell already processed:', cell_id)
                        # query for previous nodes
                        self.previous_nodes = self._get_previous_nodes(cursor, conn)
                        continue

                    # get the cell data and calculate the signals
                    cell_data = self.get_cell_data(cell_id, cursor)
                    signals_in_cell = self.matrix_profile_model.calculate_signals(cell_data)

                    # check if the current cell has no signals
                    if not signals_in_cell:
                        print('No signals in cell:', cell_id)
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

                        # calculate the signal nodes if there are no previous nodes
                        if self.previous_nodes is None:
                            # Query the node tabele to see if there are any nodes
                            signals = self._get_signals_in_cell(cell_id, cursor)
                            signal_data = []
                            for signal_id in signals['signal_id']:
                                signal_data.append(self._get_signal_data(signal_id, cursor))
                            
                            curr_nodes = self.matrix_profile_model.calculate_signal_nodes(signal_data, self.current_tab)
                            #TODO insert the nodes into the database
                            
                            self.db.insert_node_data(curr_nodes, self.current_tab, cursor, conn)
                            
                            self.previous_nodes = curr_nodes
                            self._update_cell_processed(cell_id, cursor, conn)

                        else:
                            # get the previous nodes and the signals in them
                            prev_signal_data = []
                            for prev_signal in self.previous_nodes['signal_id']:
                                prev_signal_data.append(self._get_signal_data(prev_signal, cursor))
                            
                            # get the current signals found and then attempt to merge them with the previous nodes, if they are not merged then add them as new nodes
                            curr_signal_data = signals_in_cell
                            merged_nodes = self.matrix_profile_model.merge_nodes(self.previous_nodes, prev_signal_data, curr_signal_data, self.current_tab)
                            #TODO insert the nodes into the database
                            self.db.insert_node_data(merged_nodes, self.current_tab, cursor, conn)
                            
                            self.previous_nodes = merged_nodes
                            self._update_cell_processed(cell_id, cursor, conn)


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

    def _get_previous_nodes(self, cursor, conn):
        """ Returns the previous nodes """
        query = f'''
        SELECT * FROM {self.db.sanitise(self.current_tab)}_node_table
        '''
        cursor.execute(query)

        result = cursor.fetchall()

        previous_nodes = pd.DataFrame(result, columns=['node_id', 'signal_id'])
        
        return previous_nodes