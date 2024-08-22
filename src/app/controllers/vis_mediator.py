class VisMediator():
    def __init__(self, data_mediator, tabs, treemap, grid_view, line_view):
        self.data_mediator = data_mediator
        self.tabs = tabs
        self.treemap = treemap
        self.grid_view = grid_view
        self.line_view = line_view
        self.toggled_nodes = {} # By creating a toggled node dict we can improve efficiency instead of checking for all nodes every time
        self.clicked_cell = None

    def on_treemap_click(self, node, toggle):
        if toggle == False:
            self.treemap.nodes[node]['toggle'] = True
            self.toggled_nodes[node] = self.treemap.nodes[node]
        else:
            if self.treemap.nodes[node] == self.toggled_nodes[node]:
                del self.toggled_nodes[node]
            self.treemap.nodes[node]['toggle'] = False

    def on_treemap_enter(self, node, color):
        self.grid_view.create_grid_view()
        self.color_processed_cells()
        signals_in_node = self.data_mediator.get_signals_in_node(node)
        for signal in signals_in_node:
            #find which cell that signal is in and color it
            cell = self.data_mediator.get_signal_cell(signal)
            self.grid_view.set_cell_color(cell, color)

    def on_treemap_leave(self):
        self.grid_view.create_grid_view()
        self.color_processed_cells()
        
    def resolve_treemap_toggles(self): # This code is similar to treemap enter consider separating it into different things
        for node in self.toggled_nodes:
            signals_in_node = self.data_mediator.get_signals_in_node(node)
            for signal in signals_in_node:
                cell = self.data_mediator.get_signal_cell(signal)
                color = self.toggled_nodes[node]['color']
                self.grid_view.set_cell_color(cell, color)

    def on_grid_view_click(self, cell_id):
        data = self.data_mediator.get_cell_data(cell_id)
        fig = self.line_view.generate_plot(data, cell_id, data)
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
            if processed_cells is not None:
                for cell in processed_cells:
                    self.grid_view.set_cell_color(cell, '#D3D3D3')

    def resolve_cell_click(self):
        if self.clicked_cell is not None:
            self.grid_view.set_cell_clicked(cell_name=self.clicked_cell)