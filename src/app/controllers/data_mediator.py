from app.models.data_processor import DataProcessor
import pandas as pd

class DataMediator():
    """ The data mediator class object is to be used as a way to cache the data that is to be displayed to prevent repeated queries and store the logic for 
    accessing the database
    """
    def __init__(self, file_path, database, data_processor):
        self.nodes, self.node_count, self.sequence, self.signals = self._load_from_database()
        self.db = database
        self.file_path = file_path
        self.data_processor = data_processor
        self.current_tab = ''
    
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
            'cell0':['signal1'],
            'cell1':['signal5'],
            'cell2':['signal2'],
            'cell3':['signal3'],
            'cell4':['signal4']
        }

        signals = {
            'signal1':'cell0',
            'signal2':'cell2',
            'signal3':'cell3',
            'signal4':'cell4',
            'signal5':'cell5',
            'signal6':'cell7'
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
    
    def get_grid_size(self, current_tab):
        sanitised = self.db.sanitise(current_tab)
        cursor = self.db.cursor.execute(f'SELECT COUNT(*) FROM {sanitised}_cell_table')
        grid_size = cursor.fetchone()[0]
        return grid_size

    

