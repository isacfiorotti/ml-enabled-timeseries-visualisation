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
            "#E74C3C",  # Red
            "#3498DB",  # Blue
            "#27AE60",  # Green
            "#9B59B6",  # Purple
            "#E67E22",  # Orange
            "#F39C12",  # Yellow
            "#1ABC9C",  # Teal
            "#2ECC71",  # Light Green
            "#8E44AD",  # Dark Purple
            "#2980B9",  # Dark Blue
            "#D35400",  # Dark Orange
            "#C0392B",  # Dark Red
            "#16A085",  # Dark Teal
            "#F1C40F",  # Bright Yellow
            "#BDC3C7",  # Light Gray
            "#7F8C8D",  # Gray
            "#34495E",  # Dark Blue-Grey
            "#ECF0F1",  # Off White
            "#95A5A6",  # Muted Gray
            "#2C3E50"   # Dark Slate
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

    def on_treemap_enter(self, node, color):
        # self.grid_view.create_grid_view()
        # self.color_processed_cells()
        self.is_hovering = True
       
        if self.current_treemap_tab != 'All':
            for signal in self.current_data[self.current_data['node_id'] == node]['signal_id']:
                #find which cell that signal is in and color it
                cell = self.data_mediator.get_signal_cell(signal)
                self.grid_view.set_cell_color(cell, color)
        else:
            cell = self.data_mediator.get_signal_cell(node)
            self.grid_view.set_cell_color(cell, color)

    def on_treemap_leave(self):
        # self.grid_view.create_grid_view()
        # self.color_processed_cells()
        self.is_hovering = False
        
        
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
        self.data_mediator._set_current_tab(current_tab)
        grid_size = self.data_mediator.get_grid_size()
        self.grid_view.set_grid_size(grid_size)
        self.grid_view.create_grid_view()

        # first check if the matrix profile has already been calculated

        # if it has been calculated then we can just create the treemap

        # if it hasn't been calculated then we need to start the subthread to calculate the matrix profile

        # once a mp for a cell has been calculated we need to store it in the database and update the treemap

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
        if tab == 'All':
            self.current_treemap_tab = tab
            self.display_all_signals()
        if tab == 'Length':
            self.display_by_length()
            self.current_treemap_tab = tab
        if tab == 'Amplitude':
            self.current_treemap_tab = tab
            self.display_by_amplitude()

    def display_all_signals(self):
        # get all signals in the database
        df = self.data_mediator._create_signal_df()

        self.current_data = df

        self.treemap_legend.clear_legend()        
        # they don't have "nodes" so we need to give them one
        df['count'] = 1
        # send as normal to the 
        self.treemap.create_treemap(node_counts=df['count'], labels=df['signal_id'], map_colors=['#29465B'])

    def display_by_length(self):
        df = self.data_mediator.run_group_by_length()
        self.current_data = df

        self.set_current_color_mapping()

        data = df[['node_id', 'count']].drop_duplicates()
        self.treemap.create_treemap(node_counts=data['count'], labels=data['node_id'], map_colors=self.colors)
        self.create_treemap_legend(labels=data['node_id'].tolist())

    def display_by_amplitude(self):
        df = self.data_mediator.run_group_by_amplitude()
        self.current_data = df

        self.set_current_color_mapping()

        data = df[['node_id', 'count']].drop_duplicates()
        self.treemap.create_treemap(node_counts=data['count'], labels=data['node_id'], map_colors=self.colors)
        self.create_treemap_legend(labels=data['node_id'].tolist())

    def create_treemap_legend(self, labels):
        self.treemap_legend.draw_legend(colors=self.colors, labels=labels)
    
    def set_current_color_mapping(self):
        # take the current data and create a mapping of node_id to color
        self.current_color_mapping = {}
        for i, node in enumerate(self.current_data['node_id'].drop_duplicates()):
            self.current_color_mapping[node] = self.colors[i % len(self.colors)]
