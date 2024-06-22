class VisMediator():
    def __init__(self, treemap, grid_view, line_view):
        self.treemap = treemap
        self.grid_view = grid_view
        self.line_view = line_view

    def on_treemap_click(self):
        self.grid_view.set_cell_color('cell1', 'red')