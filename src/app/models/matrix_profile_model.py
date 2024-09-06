import stumpy
import pandas as pd
import numpy as np
import time
import ast
from sklearn.cluster import AgglomerativeClustering

class MatrixProfile():
    """ Class to represent the matrix profile calcation for each cell in the timeseries and output
    the gropued signals in each cell
    """

    def __init__(self, mp_window_size, mp_threshold, gap_threshold, base_signal_length, cluster_threshold):
        self.mp_window_size = mp_window_size
        self.mp_threshold = mp_threshold
        self.gap_threshold = gap_threshold
        self.base_signal_length = base_signal_length
        self.cluster_threshold = cluster_threshold

    def calculate_signals(self, cell_data):
        """ Calculate the matrix profile for the timeseries cell """

        cell_values = cell_data.iloc[:, 2].astype(np.float64)
        
        # Compute the matrix profile
        matrix_profile = stumpy.stump(cell_values, m=self.mp_window_size)
        
        # Prepare time data
        cell_data['Time(s)'] = pd.to_datetime(cell_data['Time(s)'], format='%H:%M:%S.%f')
        
        # Adjust to align with matrix profile without resetting index
        start_index = self.mp_window_size - 1
        adjusted_data = cell_data.iloc[start_index:].copy()
        adjusted_data['Matrix Profile'] = matrix_profile[:, 0]
        
        # Filter significant points
        points_filtered = adjusted_data[adjusted_data['Matrix Profile'] > self.mp_threshold]
        
        # Calculate gaps and group into signals
        gaps = points_filtered['Time(s)'].diff()
        gap_threshold = pd.Timedelta(seconds=0.01) #TODO change this to take in a parameter from config
        
        signals = []
        current_signal = []
        
        for i, gap in enumerate(gaps):
            if i == 0 or gap <= gap_threshold:
                current_signal.append(points_filtered.iloc[i])
            else:
                signals.append(pd.DataFrame(current_signal))
                current_signal = [points_filtered.iloc[i]]
        
        if current_signal:
            signals.append(pd.DataFrame(current_signal))
        
        
        signals = [signal for signal in signals if not signal.empty and len(signal) >= self.base_signal_length]
        
        return signals
    
    def calculate_group_by_length(self, signal_data):
        time_resolution = 0.002
        
        signal_data['signal_length'] = signal_data['signal_idxs'].apply(lambda x: len(ast.literal_eval(x)))
    
        num_bins = int(np.sqrt(len(signal_data)))
        signal_data['bin'], bin_edges = pd.cut(signal_data['signal_length'], bins=num_bins, retbins=True, include_lowest=True)

        def length_to_time_range(bin_edge_left, bin_edge_right):
            start_length = np.floor(bin_edge_left).astype(int) + 1 
            end_length = np.floor(bin_edge_right).astype(int) 
            start_time = (start_length - 1) * time_resolution
            end_time = end_length * time_resolution
            return f'{start_time:.3f}-{end_time:.3f}'

        signal_data['node_id'] = signal_data.apply(lambda x: length_to_time_range(x['bin'].left, x['bin'].right), axis=1)

        clusters_df = pd.DataFrame()

        for node in signal_data['node_id'].unique():
            signals_in_node = signal_data[signal_data['node_id'] == node]
            cluster = self.calculate_group_clusters(signals_in_node)
            clusters_df = pd.concat([clusters_df, cluster], ignore_index=True)

        count_per_group = signal_data.groupby('node_id').size().reset_index(name='count')
        signal_data = signal_data.merge(count_per_group, on='node_id')
        output = signal_data.merge(clusters_df[['signal_id', 'cluster', 'cluster_count']], on='signal_id', how='left')
        output = output[['node_id', 'signal_id', 'count', 'cluster', 'cluster_count']]


        return output

    def calculate_group_by_amplitude(self, signal_data):

        signal_data['amplitude'] = signal_data['data'].apply(lambda x: (max(x) - min(x))/2)

        # Determine number of bins
        num_bins = int(np.sqrt(len(signal_data)))
        signal_data['bin'], bin_edges = pd.cut(signal_data['amplitude'], bins=num_bins, retbins=True, labels=False)

        def amplitude_range(bin_edge_left, bin_edge_right):
            return f'{bin_edge_left:.3f}-{bin_edge_right:.3f}'

        signal_data['node_id'] = signal_data.apply(
            lambda x: amplitude_range(bin_edges[x['bin']], bin_edges[x['bin'] + 1] if x['bin'] + 1 < len(bin_edges) else bin_edges[-1]),
            axis=1
        )

        clusters_df = pd.DataFrame()

        for node in signal_data['node_id'].unique():
            signals_in_node = signal_data[signal_data['node_id'] == node]
            cluster = self.calculate_group_clusters(signals_in_node)
            clusters_df = pd.concat([clusters_df, cluster], ignore_index=True)

        count_per_group = signal_data.groupby('node_id').size().reset_index(name='count')
        signal_data = signal_data.merge(count_per_group, on='node_id')
        output = signal_data.merge(clusters_df[['signal_id', 'cluster', 'cluster_count']], on='signal_id', how='left')
        output = output[['node_id', 'signal_id', 'count', 'cluster', 'cluster_count']]

        return output
    
    def calculate_group_clusters(self, signal_data):
        signal_data = signal_data.copy()

        if len(signal_data) == 1:
            signal_data.loc[:, 'cluster'] = 0
            signal_data.loc[:, 'count'] = 1
            signal_data.rename(columns={'count': 'cluster_count'}, inplace=True)
            return signal_data[['cluster', 'signal_id', 'cluster_count']]

        signal_data.loc[:, 'data'] = signal_data['data'].apply(lambda x: np.array(x))
        signal_data.loc[:, 'signal_length'] = signal_data['data'].apply(lambda x: len(x))

        distance_matrix = np.zeros((len(signal_data), len(signal_data)))

        for i in range(len(signal_data)):
            signal_a = signal_data.iloc[i]['data']
            for j in range(i+1, len(signal_data)):
                signal_b = signal_data.iloc[j]['data']

                if len(signal_a) > len(signal_b):
                    signal_b = np.pad(signal_b, (0, len(signal_a) - len(signal_b)), 'constant')
                elif len(signal_b) > len(signal_a):
                    signal_a = np.pad(signal_a, (0, len(signal_b) - len(signal_a)), 'constant')

                distance = stumpy.mass(signal_a, signal_b)
                distance_matrix[i, j] = distance[0]
                distance_matrix[j, i] = distance[0]

        clustering = AgglomerativeClustering(n_clusters=None, metric='precomputed', linkage='average', distance_threshold=self.cluster_threshold).fit(distance_matrix)
        signal_data.loc[:, 'cluster'] = clustering.labels_

        count_per_group = signal_data.groupby('cluster').size().reset_index(name='cluster_count')
        signal_data = signal_data.merge(count_per_group, on='cluster')
        output = signal_data[['cluster', 'signal_id', 'cluster_count']]

        return output




