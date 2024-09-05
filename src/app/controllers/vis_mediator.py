import time
import re

class VisMediator():
    def __init__(self, data_mediator, tabs, treemap, grid_view, line_view, treemap_tab, treemap_legend):
        self.data_mediator = data_mediator
        self.tabs = tabs
        self.treemap = treemap
        self.grid_view = grid_view
        self.line_view = line_view
        self.toggled_nodes = {} # By creating a toggled node dict we can improve efficiency instead of checking for all nodes every time
        self.clicked_cell = None
        self.treemap_tab = treemap_tab
        self.treemap_legend = treemap_legend
        self.current_data = None
        self.is_hovering = False
        self.colors = [
            "#6DBE45",  # Fresh Green
            "#9ACD32",  # Yellow Green
            "#FFE666",  # Light Gold
            "#FFD500",  # Golden Yellow
            "#FFAD00",  # Deep Orange
            "#FF8C00",  # Dark Orange
            "#CC3500",  # Darker Orange
            "#661A00",  # Very Dark Orange
            "#007FFF",  # Vivid Sky Blue
            "#3399FF",  # Bright Blue
            "#0033CC",  # Medium Blue
            "#A64D79",  # Light Purple
            "#9B4F7D",  # Medium Purple
            "#6D3F6C",  # Dark Purple
            "#2E2A80",  # Very Dark Purple
        ]
        self.current_color_mapping = None
        self.current_treemap_tab = None

    def on_treemap_click(self, node, toggle):
        if toggle == False:
            self.treemap.nodes[node]['toggle'] = True
            self.toggled_nodes[node] = self.treemap.nodes[node]
        else:
            if self.treemap.nodes[node] == self.toggled_nodes[node]:
                del self.toggled_nodes[node]
            self.treemap.nodes[node]['toggle'] = False

    def on_treemap_enter(self, cluster, color, node):
        # self.grid_view.create_grid_view()
        self.color_processed_cells()
        self.is_hovering = True
       
        signals_in_node = self.current_data[self.current_data['node_id'] == node]

        signals_in_cluster = signals_in_node[signals_in_node['cluster'] == cluster]

        for signal in signals_in_cluster.iterrows():
            signal_id = signal[1]['signal_id']
            cell = self.data_mediator.get_signal_cell(signal_id)
            self.grid_view.set_cell_color(cell, color)


    def on_treemap_leave(self):
        # self.grid_view.create_grid_view()
        # self.color_processed_cells()
        self.is_hovering = False
        self.grid_view.create_grid_view()
        
        
    def resolve_treemap_toggles(self): # This code is similar to treemap enter consider separating it into different things
        for node in self.toggled_nodes:
            signals_in_node = self.data_mediator.get_signals_in_node(node)
            for signal in signals_in_node:
                cell = self.data_mediator.get_signal_cell(signal)
                color = self.toggled_nodes[node]['color']
                self.grid_view.set_cell_color(cell, color)

    def on_grid_view_click(self, cell_id):
        data = self.data_mediator.get_cell_data(cell_id)

        # get all signals in the cell
        signals = self.data_mediator._get_signals_in_cell(cell_id)
        colors = []
        if len(signals) > 0:
            for signal in signals.iterrows():
                signal_id = signal[1]['signal_id']
                node_id = self.current_data[self.current_data['signal_id'] == signal_id]['node_id'].values[0]
                color = self.current_color_mapping[node_id]
                colors.append(color)

        fig = self.line_view.generate_plot(data, cell_id, data, colors)
        self.line_view.create_lineview(fig)
        if self.clicked_cell is not None:
            self.grid_view.set_cell_unclicked(self.clicked_cell)
        self.clicked_cell = cell_id
        self.grid_view.set_cell_clicked(cell_id)

    def on_tab_click(self, current_tab):

        # End any previous subthreads

        # Start the subthread to calculate the matrix profile

        self.data_mediator._set_current_tab(current_tab)
        grid_size = self.data_mediator.get_grid_size()
        self.grid_view.set_grid_size(grid_size)
        # access the grid view row and column values 
        rows = self.grid_view.rows
        cols = self.grid_view.cols

        cell_starts = []
        for i in range(rows):
            # always get the first cell in the row
            cell_name = f'cell_{i * cols}'
            cell_starts.append(self.data_mediator.get_cell_start_as_time(cell_name))

        self.grid_view.create_grid_view(cell_starts)


    def color_processed_cells(self):
        if self.data_mediator.current_tab is not None:
            processed_cells = self.data_mediator.get_processed_cells()
            cells_with_signals = self.data_mediator.get_cells_with_signals()
            if processed_cells is not None:
                for cell in processed_cells:
                    self.grid_view.set_cell_color(cell, '#D3D3D3')
            if cells_with_signals is not None:
                for cell in cells_with_signals:
                    self.grid_view.set_cell_color(cell, '#CFFDBC')

    def resolve_cell_click(self):
        if self.clicked_cell is not None:
            self.grid_view.set_cell_clicked(cell_name=self.clicked_cell)

    def on_treemap_tab_click(self, tab):
        # if tab == 'All':
        #     start_time = time.time()
        #     self.current_treemap_tab = tab
        #     self.display_all_signals()
        #     end_time = time.time()
        #     print(f'function display_all_signals took: {end_time - start_time}')
        if tab == 'Duration (s)':
            self.current_treemap_tab = tab
            self.display_by_length()
        if tab == 'Amplitude':
            self.current_treemap_tab = tab
            self.display_by_amplitude()



    # def display_all_signals(self):
    #     # get all signals in the database
    #     df = self.data_mediator._create_signal_df()

    #     self.current_data = df

    #     self.treemap_legend.clear_legend()        
    #     # they don't have "nodes" so we need to give them one
    #     df['count'] = 1
    #     # send as normal to the 
    #     self.treemap.create_treemap(node_counts=df['count'], labels=df['signal_id'], map_colors=['#29465B'])

    def display_by_length(self):
        df = self.data_mediator.run_group_by_length() # make this funciton also return the leaves of the tree
        self.current_data = df

        self.set_current_color_mapping()

        line_data = self.data_mediator.get_line_data(df)

        data = df[['node_id', 'count']].drop_duplicates()
        self.treemap.create_treemap(node_counts_df=data[['count', 'node_id']], labels=data['node_id'], map_colors=self.colors, cluster_df=df, line_data=line_data)
        self.create_treemap_legend(labels=data['node_id'].tolist())


    def display_by_amplitude(self):
        df = self.data_mediator.run_group_by_amplitude()
        self.current_data = df

        self.set_current_color_mapping()

        line_data = self.data_mediator.get_line_data(df)

        data = df[['node_id', 'count']].drop_duplicates()
        self.treemap.create_treemap(node_counts_df=data[['count', 'node_id']], labels=data['node_id'], map_colors=self.colors, cluster_df=df, line_data=line_data)
        self.create_treemap_legend(labels=data['node_id'].tolist())

    def create_treemap_legend(self, labels):
        self.treemap_legend.draw_legend(colors=self.colors, labels=labels, title=self.current_treemap_tab)
    
    def set_current_color_mapping(self, colors=None):
        if colors is None:
            colors = self.colors
        labels = self.current_data['node_id'].unique()
        sorted_labels = sorted(labels, key=self.extract_start)
        self.current_color_mapping = {label: color for label, color in zip(sorted_labels, colors)}

    def extract_start(self, label):
        match = re.match(r'(\d+\.\d+)', label)
        return float(match.group()) if match else float('inf')