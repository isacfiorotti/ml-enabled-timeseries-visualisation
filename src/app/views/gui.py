import tkinter as tk
from app.views.lineview import LineView
from app.views.treemap import TreemapView
from app.views.gridview import GridView
from app.views.tabs import Tabs
from app.controllers.vis_mediator import VisMediator
from app.views.gridview_tab_top import GridviewTabTop
from app.views.treemap_tab import TreemapTab
from app.views.treemap_legend import TreemapLegend


class MainWindow(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.data_mediator = data_mediator
        self.init_ui()
    
    def init_ui(self):

        #window
        self.window = tk.Frame(self, background='grey')
        self.window.pack(fill='both', expand=True)

        #horizontal tab
        self.tab_frame = tk.Frame(self.window, background='#ECECEC', height=20) # tab height
        self.tab_frame.pack(fill='x')

        #tabs
        self.tabs = Tabs(self.tab_frame, self.data_mediator)
        self.tabs.pack(fill='both', expand=True)

        #vertical_paned_window
        self.vertical_paned_window = tk.PanedWindow(self.window, orient='vertical')
        self.vertical_paned_window.pack(fill='both', expand=True)

        #top frame
        self.top = tk.PanedWindow(self.window, orient='horizontal') # Top frame is a paned window for dividing left and right
        self.top.pack(fill='both', expand=True)
        self.vertical_paned_window.add(self.top, stretch='always', minsize=300)

        #grid_view
        self.grid_frame = tk.Frame(self.top)
        self.top.add(self.grid_frame, stretch='always')
        
        self.gridview_tab_top = GridviewTabTop(self.grid_frame)
        self.gridview_tab_top.pack(fill='x', expand=False)
        
        self.grid_view = GridView(self.grid_frame)
        self.grid_view.pack(fill='both', expand=True)

        #treemap
        self.treemap_frame = tk.Frame(self.top)
        self.top.add(self.treemap_frame, stretch='always', minsize=385)

        self.treemap_tab = TreemapTab(self.treemap_frame)
        self.treemap_tab.pack(side='top', fill='x', expand=False)

        self.treemap_legend = TreemapLegend(self.treemap_frame)
        self.treemap_legend.pack(side='right', fill='y', expand=False)

        self.treemap = TreemapView(self.treemap_frame, self.data_mediator)
        self.treemap.pack(fill='both', expand=True)
        
        #bottom frame
        self.bottom = tk.Frame(self.window, background='light green')
        self.bottom.pack(side='bottom', fill='both', expand=True)
        self.vertical_paned_window.add(self.bottom, stretch='always')
        
        #lineview
        self.line_view = LineView(self.bottom, self.data_mediator) # put the line view into a frame
        self.line_view.pack(fill='both', expand=True)

        #vis mediator
        vis_mediator = VisMediator(self.data_mediator, self.tabs, self.treemap, self.grid_view, self.line_view, self.treemap_tab, self.treemap_legend)
        self.tabs.set_vis_mediator(vis_mediator)
        self.treemap.set_vis_mediator(vis_mediator)
        self.grid_view.set_vis_mediator(vis_mediator)
        self.treemap_tab.set_vis_mediator(vis_mediator)
        self.treemap_legend.set_vis_mediator(vis_mediator)
        


        

