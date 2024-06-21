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
        
# Possibly migrate this to a different script and import the functions as needed and change to canvas instead of buttons for better results

class GridView(tk.Frame):
    def __init__(self, parent, grid_size, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_size = grid_size
        self.create_grid()

    def create_grid(self):
        self.cols = int(sqrt(self.grid_size))
        self.rows = ceil(self.grid_size / self.cols)

        if self.rows * self.cols < self.grid_size:
            self.cols += 1
        
        cell_count = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if cell_count < self.grid_size:
                    button = tk.Button(self, relief='flat')
                    button.grid(row=i, column=j, sticky="nsew")
                    self.grid_columnconfigure(j, weight=1)
                    cell_count += 1
            self.grid_rowconfigure(i, weight=1)

