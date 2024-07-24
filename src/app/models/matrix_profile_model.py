import stumpy
import pandas as pd
import numpy as np
import time


class MatrixProfile():
    """ Class to represent the matrix profile calcation for each cell in the timeseries and output
    the gropued signals in each cell
    """
    def __init__(self, mp_window_size, mp_threshold, gap_threshold, base_signal_length, mp_grouping_sensitivity):
        self.mp_window_size = mp_window_size
        self.mp_threshold = mp_threshold
        self.gap_threshold = gap_threshold
        self.base_signal_length = base_signal_length
        self.mp_grouping_sensitivity = mp_grouping_sensitivity

    def calculate_signal_blocks(self, cell_data):
        """ Calculate the matrix profile for the timeseries cell """
        
        cell_values = cell_data.iloc[:, 2].astype(np.float64)
        
        # Compute the matrix profile
        matrix_profile = stumpy.stump(cell_values, m=self.mp_window_size)
        
        # Prepare time data
        cell_data['Time(s)'] = pd.to_datetime(cell_data['Time(s)'], format='%H:%M:%S.%f')
        cell_data = cell_data.iloc[self.mp_window_size - 1:].reset_index(drop=True)
        points = pd.DataFrame({'Time(s)': cell_data['Time(s)'], 'Matrix Profile': matrix_profile[:, 0]})
        points_filtered = points[points['Matrix Profile'] > self.mp_threshold]
        
        # Calculate gaps and group into blocks
        gaps = points_filtered['Time(s)'].diff()
        gap_threshold = pd.Timedelta(seconds=0.01)
        
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

    def calculate_signal_groups(self, blocks, cell_data, current_tab):
        """ Calculate the groups of signals within the cell """
        sleep_interval = 0.01 # Sleep interval for checking if the column exists

        if current_tab in cell_data.columns:
            block_mass_scores = {}

            for i in range(len(blocks)):
                block_a = blocks[i]
                block_data_a = cell_data.loc[block_a.index, current_tab].values
                for j in range(i + 1, len(blocks)):
                    block_b = blocks[j]
                    block_data_b = cell_data.loc[block_b.index, current_tab].values

                    # Pad the shorter signal with zeros
                    if len(block_data_a) > len(block_data_b):
                        block_data_b = np.pad(block_data_b, (0, len(block_data_a) - len(block_data_b)), 'constant')
                    elif len(block_data_b) > len(block_data_a):
                        block_data_a = np.pad(block_data_a, (0, len(block_data_b) - len(block_data_a)), 'constant')

                    distance = stumpy.mass(block_data_a, block_data_b)
                    
                    # Only consider pairs with a distance below the threshold
                    if distance[0] <= self.mp_grouping_sensitivity:
                        block_mass_scores[(i, j)] = distance[0]

            sorted_block_pairs = sorted(block_mass_scores.items(), key=lambda x: x[1])

            groups = []
            assigned_blocks = set()

            #build groups based on sorted similarity scores
            for (i, j), score in sorted_block_pairs:
                if i not in assigned_blocks and j not in assigned_blocks:
                    groups.append({i, j})
                    assigned_blocks.update([i, j])
                elif i in assigned_blocks and j not in assigned_blocks:
                    for group in groups:
                        if i in group:
                            group.add(j)
                            assigned_blocks.add(j)
                            break
                elif j in assigned_blocks and i not in assigned_blocks:
                    for group in groups:
                        if j in group:
                            group.add(i)
                            assigned_blocks.add(i)
                            break

            # Convert sets to lists for final output
            final_groups = [list(group) for group in groups]

            # Include any unassigned blocks as their own groups
            for i in range(len(blocks)):
                if i not in assigned_blocks:
                    final_groups.append([i])

            print(f"Groups: {final_groups}") # delete this print statement

            return final_groups

        else:
            print(f"Column '{current_tab}' not found. Checking again...")
            time.sleep(sleep_interval)  # Small pause before checking again