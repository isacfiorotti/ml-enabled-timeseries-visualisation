import tkinter as tk
from app.lineview import LineView
from app.treemap import TreemapView
from app.gridview import GridView
from app.vis_mediator import VisMediator

class MainWindow(tk.Frame):
    def __init__(self, parent, relation_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.relation_manager = relation_manager
        self.init_ui()
    
    def init_ui(self):

        #RENAME this variabel
        #window
        self.window = tk.Frame(self)
        self.window.pack(fill='both', expand=True)

        #vertical_paned_window
        self.vertical_paned_window = tk.PanedWindow(self.window, orient='vertical')
        self.vertical_paned_window.pack(fill='both', expand=True)

        #top frame
        self.top = tk.PanedWindow(self.window, orient='horizontal') # Top frame is a paned window for dividing left and right
        self.top.pack(side='top', fill='both', expand=True)
        self.vertical_paned_window.add(self.top, stretch='always')

        #grid_view
        self.grid_frame = tk.Frame(self.top)
        self.top.add(self.grid_frame, stretch='always')
        self.grid_view = GridView(self.grid_frame, grid_size=90) # change to take input grid size from data
        self.grid_view.pack(fill='both', expand=True)

        #treemap
        self.treemap_frame = tk.Frame(self.top)
        self.top.add(self.treemap_frame, stretch='always')
        self.treemap = TreemapView(self.treemap_frame, self.relation_manager)
        self.treemap.pack(fill='both', expand=True)
        
        #bottom frame
        self.bottom = tk.Frame(self.window, background='light green')
        self.bottom.pack(side='bottom', fill='both', expand=True)
        self.vertical_paned_window.add(self.bottom, stretch='always')
        
        #lineview
        self.line_view = LineView(self.bottom)
        self.line_view.pack(fill='both', expand=True)

        #vis mediator
        vis_mediator = VisMediator(self.treemap, self.grid_view, self.line_view)
        self.treemap.set_vis_mediator(vis_mediator)
        self.grid_view.set_vis_mediator(vis_mediator)

