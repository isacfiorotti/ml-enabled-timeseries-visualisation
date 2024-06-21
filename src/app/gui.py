import tkinter as tk
from math import sqrt, ceil
from app.lineplot import LineView

class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        
        #background
        self.bg = tk.Frame(self)
        self.bg.pack(fill='both', expand=True)

        #window
        self.window = tk.PanedWindow(self.bg, orient='vertical')
        self.window.pack(fill='both', expand=True)

        #top frame
        self.top = tk.PanedWindow(self.bg, orient='horizontal')
        self.top.pack(side='top', fill='both', expand=True)
        self.window.add(self.top, stretch='always')

        #grid_view
        self.grid_view = GridView(self.top, grid_size=7) # change this to dynamically update grid_size
        self.top.add(self.grid_view, stretch='always')

        #treemap
        self.treemap = tk.Frame(self.top, bg='yellow')
        self.top.add(self.treemap, stretch='always')

        #bottom frame
        self.bottom = tk.Frame(self.bg, bg='light green')
        self.window.add(self.bottom, stretch='always')

        #lineview
        self.line_view = LineView(self.bottom)
        self.line_view.pack(fill='both', expand=True)
        
# Possibly migrate this to a different script and import the functions as needed

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
