import tkinter as tk
from math import sqrt, ceil
from app.lineplot import LineView
from app.treemap import TreemapView

class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        
        #window
        self.window = tk.Frame(self)
        self.window.pack(fill='both', expand=True)

        #background
        self.background = tk.PanedWindow(self.window, orient='vertical')
        self.background.pack(fill='both', expand=True)

        #top frame
        self.top = tk.PanedWindow(self.window, orient='horizontal') # Top frame is a paned window for dividing left and right
        self.top.pack(side='top', fill='both', expand=True)
        self.background.add(self.top, stretch='always')

        #grid_view
        self.grid_frame = tk.Frame(self.top)
        self.top.add(self.grid_frame, stretch='always')
        self.grid_view = tk.Canvas(self.grid_frame, background='red')
        self.grid_view.pack(fill='both', expand=True)

        #treemap
        self.treemap_frame = tk.Frame(self.top)
        self.top.add(self.treemap_frame, stretch='always')
        self.treemap = TreemapView(self.treemap_frame)
        self.treemap.pack(fill='both', expand=True)
        
        #bottom frame
        self.bottom = tk.Frame(self.window, background='light green')
        self.bottom.pack(side='bottom', fill='both', expand=True)
        self.background.add(self.bottom, stretch='always')
        
        #lineview
        self.line_view = LineView(self.bottom)
        self.line_view.pack(fill='both', expand=True)

