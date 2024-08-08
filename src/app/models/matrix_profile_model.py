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

    def calculate_signal_blocks(self, cell_data):
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
        
        # Calculate gaps and group into blocks
        gaps = points_filtered['Time(s)'].diff()
        gap_threshold = pd.Timedelta(seconds=0.01) #TODO change this to take in a parameter from congit
        
        blocks = []
        current_block = []
        
        for i, gap in enumerate(gaps):
            if i == 0 or gap <= gap_threshold:
                current_block.append(points_filtered.iloc[i])
            else:
                blocks.append(pd.DataFrame(current_block))
                current_block = [points_filtered.iloc[i]]
        
        if current_block:
            blocks.append(pd.DataFrame(current_block))
        
        # Clear empty blocks and those below the base signal length
        blocks = [block for block in blocks if not block.empty and len(block) >= self.base_signal_length]
        
        return blocks


    def calculate_signal_nodes(self, signals, cell_data, current_tab):
        """ Calculate the signal nodes for the cell """
        sleep_time = 0.01

        if current_tab in cell_data.columns:

            signal_mass_scores = []

            # Compute pairwise distances using STUMPY mass, signals is a list of dataframes
            for i in range(len(signals)):
                for j in range(i + 1, len(signals)):
                    # Extract the 'Arterial pressure (mmHg)' column values
                    signal_i = signals[i][current_tab].values
                    signal_j = signals[j][current_tab].values

                    # Pad the shorter signal with zeros to make them the same length
                    if len(signal_i) > len(signal_j):
                        signal_j = np.pad(signal_j, (0, len(signal_i) - len(signal_j)), 'constant')
                    else:
                        signal_i = np.pad(signal_i, (0, len(signal_j) - len(signal_i)), 'constant')

                    # Compute distance using STUMPY mass
                    distance = stumpy.mass(signal_i, signal_j).mean()
                    signal_mass_scores.append((i, j, distance))
            
            # Sort by distance
            signal_mass_scores.sort(key=lambda x: x[2])

            # Ensure that the signals are not assigned to multiple groups
            groups = []
            assigned_signals = set()

            # Build groups based on sorted similarity scores
            for i, j, distance in signal_mass_scores:
                if i not in assigned_signals and j not in assigned_signals:
                    groups.append([i, j])
                    assigned_signals.add(i)
                    assigned_signals.add(j)
                elif i not in assigned_signals:
                    for group in groups:
                        if j in group:
                            group.append(i)
                            assigned_signals.add(i)
                            break
                elif j not in assigned_signals:
                    for group in groups:
                        if i in group:
                            group.append(j)
                            assigned_signals.add(j)
                            break
            
            # Include any unassigned signals as their own groups
            for i in range(len(signals)):
                if i not in assigned_signals:
                    groups.append([i])

            # Create the output DataFrame
            node_id = []
            signal_ids_in_node = []
            for node_idx, group in enumerate(groups):
                for signal_id in group:
                    node_id.append(node_idx)
                    signal_ids_in_node.append(signal_id)

            result_df = pd.DataFrame({'node_id': node_id, 'signal_id': signal_ids_in_node})
            
            return result_df


    def merge_nodes(self, previous_nodes, current_nodes, signals, current_tab):
        """ Merge the previous nodes with the current nodes """
        previous_node_groups = previous_nodes.groupby('node_id')['signal_id'].apply(list).to_dict()
        current_node_groups = current_nodes.groupby('node_id')['signal_id'].apply(list).to_dict()

        new_node_id = max(previous_nodes['node_id']) + 1

        merged_nodes = []

        for prev_node_id, prev_signals in previous_node_groups.items():
            matched = False
            for curr_node_id, curr_signals in current_node_groups.items():
                for prev_signal in prev_signals:
                    for curr_signal in curr_signals:
                        # Retrieve signal data
                        signal_prev = signals[prev_signal][current_tab].values
                        signal_curr = signals[curr_signal][current_tab].values

                        # Pad shorter signal with zeros
                        if len(signal_prev) > len(signal_curr):
                            signal_curr = np.pad(signal_curr, (0, len(signal_prev) - len(signal_curr)), 'constant')
                        else:
                            signal_prev = np.pad(signal_prev, (0, len(signal_curr) - len(signal_prev)), 'constant')

                        # Compute distance using STUMPY mass
                        distance = stumpy.mass(signal_prev, signal_curr).mean()

                        if distance < self.mp_merging_sensitivity:  # Define an appropriate threshold for similarity
                            merged_nodes.append((prev_node_id, curr_signals))
                            matched = True
                            break
                    if matched:
                        break
                if matched:
                    break

            if not matched:
                merged_nodes.append((prev_node_id, prev_signals))

        for curr_node_id, curr_signals in current_node_groups.items():
            if all(curr_signal not in previous_nodes['signal_id'].values for curr_signal in curr_signals):
                merged_nodes.append((new_node_id, curr_signals))
                new_node_id += 1

        # Create the output DataFrame
        node_id = []
        signal_ids_in_node = []
        for node_idx, signals_in_node in merged_nodes:
            for signal_id in signals_in_node:
                node_id.append(node_idx)
                signal_ids_in_node.append(signal_id)

        merged_result_df = pd.DataFrame({'node_id': node_id, 'signal_id': signal_ids_in_node})
        print(merged_result_df)
        
        return merged_result_df
