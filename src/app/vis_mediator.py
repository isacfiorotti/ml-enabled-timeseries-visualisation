class VisMediator():
    def __init__(self, relation_manager, treemap, grid_view, line_view):
        self.relation_manager = relation_manager
        self.treemap = treemap
        self.grid_view = grid_view
        self.line_view = line_view
        self.toggled_nodes = {} # By creating a toggled node dict we can improve efficiency instead of checking for all nodes every time

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
        signals_in_node = self.relation_manager.get_signals_in_node(node)
        for signal in signals_in_node:
            #find which cell that signal is in and color it
            cell = self.relation_manager.get_signal_cell(signal)
            self.grid_view.set_cell_color(cell, color)

    def on_treemap_leave(self):
        self.grid_view.create_grid_view()
        
    def resolve_treemap_toggles(self): # This code is similar to treemap enter consider separating it into different things
        for node in self.toggled_nodes:
            signals_in_node = self.relation_manager.get_signals_in_node(node)
            for signal in signals_in_node:
                cell = self.relation_manager.get_signal_cell(signal)
                color = self.toggled_nodes[node]['color']
                self.grid_view.set_cell_color(cell, color)

    def on_grid_view_click(self, cell_name):
        fig = self.line_view.generate_plot()
        self.line_view.create_lineview(fig)
