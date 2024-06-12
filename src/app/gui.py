import tkinter as tk
from PIL import Image, ImageTk

class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        
        #background
        self.bg = tk.Frame(self)
        self.bg.pack(fill='both', expand=True)

        #top frame
        self.top = tk.Frame(self.bg)
        self.top.pack(side='top', fill='both', expand=True)

        #grid_view
        self.grid_view = tk.Frame(self.top, bg='light blue')
        self.grid_view.pack(padx=5, pady=5, side='left', fill='both', expand=True)

        #treemap
        self.treemap = tk.Frame(self.top, bg='yellow')
        self.treemap.pack(padx=5, pady=5, side='right', fill='both', expand=True)

        #bottom frame
        self.bottom = tk.Frame(self.bg)
        self.bottom.pack(side='bottom', fill='both', expand=True)
