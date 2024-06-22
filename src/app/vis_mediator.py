class VisMediator():
    def __init__(self, relation_manager, treemap, grid_view, line_view):
        self.relation_manager = relation_manager
        self.treemap = treemap
        self.grid_view = grid_view
        self.line_view = line_view

    def on_treemap_click(self):
        self.grid_view.set_cell_color('cell1', 'red')

    def on_treemap_enter(self, node):
        self.grid_view.create_grid_view()
        signals_in_node = self.relation_manager.get_signals_in_node(node)
        for signal in signals_in_node:
            #find which cell that signal is in and color it
            cell = self.relation_manager.get_signal_cell(signal)
            self.grid_view.set_cell_color(cell, 'red')

