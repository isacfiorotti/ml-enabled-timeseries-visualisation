class SignalRelationManager():
    def __init__(self):
        self.nodes, self.node_count, self.sequence = self._load_from_database()
    
    def _load_from_database(self):
        # Test functionality not actual implementation of _load_from_database
        nodes = {
            'node1':['signal1', 'signal2'],
            'node2':['signal3'],
            'node3':['signal4']
        }

        node_count = {
            'node1':2,
            'node2':1,
            'node3':1
        }

        sequence = {
            'cell1':['signal1'],
            'cell2':[],
            'cell3':['signal2'],
            'cell4':['signal3'],
            'cell5':['signal4']
        }

        return nodes, node_count, sequence
        
    def get_related_signals(self, signal):
        """ Returns list of signals in the same node
        """
        

    def get_signals_in_node(self, node):
        """ Returns dictionary containing signals grouped into nodes 
        """
        return self.nodes[node]
    
    def get_nodes(self):
        """ Returns a list of nodes
        """
        return list(self.nodes.keys())

    def get_node_counts(self):
        """ Returns list of values
        """
        return list(self.node_count.values())

        
