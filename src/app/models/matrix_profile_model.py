import stumpy
import pandas as pd
import numpy as np
import time


class MatrixProfile():
    """ Class to represent the matrix profile calcation for each cell in the timeseries and output
    the gropued signals in each cell
    """
    def __init__(self, mp_window_size, mp_threshold, gap_threshold, base_signal_length, mp_merge_sensitivity):
        self.mp_window_size = mp_window_size
        self.mp_threshold = mp_threshold
        self.gap_threshold = gap_threshold
        self.base_signal_length = base_signal_length
        self.mp_merging_sensitivity = mp_merge_sensitivity

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

    def calculate_signal_nodes(self, signal_data, current_tab, last_signal_id=None):
        """ Calculate the signal nodes for the cell """
        # Initialize variables
        signal_mass_scores = {}
        signal_nodes = pd.DataFrame(columns=['node_id', 'signal_id'])

        # Calculate pairwise distances and store in signal_mass_scores
        for i in range(len(signal_data)):
            for j in range(i + 1, len(signal_data)):
                signal_i = signal_data[i][current_tab].values
                signal_j = signal_data[j][current_tab].values

                # Pad the shorter signal with zeros to make them the same length
                if len(signal_i) > len(signal_j):
                    signal_j = np.pad(signal_j, (0, len(signal_i) - len(signal_j)), 'constant')
                else:
                    signal_i = np.pad(signal_i, (0, len(signal_j) - len(signal_i)), 'constant')

                # Compute distance using STUMPY mass
                distance = stumpy.mass(signal_i, signal_j)

                # If there is a match, store the match in signal_mass_scores
                if distance < self.mp_merging_sensitivity:
                    signal_mass_scores[(i, j)] = distance

        # Assign signals to nodes based on signal_mass_scores
        node_id = 0
        signal_to_node = {}

        for i in range(len(signal_data)):
            # Check if the signal is already assigned to a node
            assigned_node = None

            for (sig_i, sig_j), dist in signal_mass_scores.items():
                if i == sig_i or i == sig_j:
                    if sig_i in signal_to_node:
                        assigned_node = signal_to_node[sig_i]
                    elif sig_j in signal_to_node:
                        assigned_node = signal_to_node[sig_j]
                    break

            # If the signal has a match, assign it to the same node as its match
            if assigned_node is not None:
                signal_to_node[i] = assigned_node
            else:
                # Otherwise, create a new node
                signal_to_node[i] = node_id
                node_id += 1

            # Add the signal to the DataFrame
            new_row = pd.DataFrame({'node_id': [signal_to_node[i]], 'signal_id': [i]})
            signal_nodes = pd.concat([signal_nodes, new_row], ignore_index=True)

        return signal_nodes

    def merge_nodes(self, previous_nodes, prev_signal_data, curr_signal_data, current_tab):
        """ Merge the previous nodes with the current nodes """

        result_df = previous_nodes.copy()

        last_node_id = previous_nodes['node_id'].max()
        last_signal_id = previous_nodes['signal_id'].max()

        # Assign signal IDs to the new signals by creating a dictionary
        signal_id_dict = {}
        current_signal_id = last_signal_id

        for idx, signal_df in enumerate(curr_signal_data):
            current_signal_id += 1
            signal_id_dict[idx] = current_signal_id
            signal_df['signal_id'] = current_signal_id

        matched_signals = set()

        # Iterate through each node in previous_nodes
        for node in previous_nodes['node_id'].unique():
            # Select the first signal in the node
            representative_signal = prev_signal_data[0]

            for idx, signal in enumerate(curr_signal_data):

                if idx in matched_signals:
                    continue  # Skip if already matched

                signal_i = representative_signal[current_tab].values
                signal_j = signal[current_tab].values

                # Pad the shorter signal with zeros to make them the same length
                if len(signal_i) > len(signal_j):
                    signal_j = np.pad(signal_j, (0, len(signal_i) - len(signal_j)), 'constant')
                else:
                    signal_i = np.pad(signal_i, (0, len(signal_j) - len(signal_i)), 'constant')

                # Compute distance using STUMPY mass
                distance = stumpy.mass(signal_i, signal_j)

                # If there is a match, merge the signals
                if distance < self.mp_merging_sensitivity:
                    # Get the signal ID from the dictionary using the current index
                    signal_id = signal_id_dict[idx]
                    
                    # Merge the signals by inserting into the DataFrame
                    new_row = pd.DataFrame({'node_id': [node], 'signal_id': [signal_id]})
                    result_df = pd.concat([result_df, new_row], ignore_index=True)
                    print(f'Merged signal {signal_id} into node {node}')
                    matched_signals.add(idx)  # Mark signal as matched
                    
        # If no match is found, create a new node for each signal not already in a node
        node_id = last_node_id + 1
        for idx, signal in enumerate(curr_signal_data):
            # Get the signal ID from the dictionary using the current index
            signal_id = signal_id_dict[idx]
            
            if signal_id not in result_df['signal_id'].values:
                new_row = pd.DataFrame({'node_id': [node_id], 'signal_id': [signal_id]})
                result_df = pd.concat([result_df, new_row], ignore_index=True)
                print(f'Created new node {node_id} for signal {signal_id}')
                node_id += 1

        return result_df