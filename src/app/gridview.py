import tkinter as tk
from math import ceil, sqrt

class GridView(tk.Frame):
    def __init__(self, parent, grid_size, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=True)
        self.grid_size = grid_size
        self.cells = {}
        self.create_grid()
        self.canvas.bind("<Configure>", self.on_resize)
        self.padding = 3

    def create_grid(self):
        self.cols = int(sqrt(self.grid_size))
        self.rows = ceil(self.grid_size / self.cols)
        
        if self.rows * self.cols < self.grid_size:
            self.cols += 1

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        
        self.cell_width = (self.width - (self.cols + 1) * self.padding) / self.cols
        self.cell_height = (self.height - (self.rows + 1) * self.padding) / self.rows

        self.create_grid_view()
    
    def create_grid_view(self):
        self.canvas.delete("all")

        cell_count = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if cell_count < self.grid_size:
                    x1 = j * (self.cell_width + self.padding) + self.padding
                    y1 = i * (self.cell_height + self.padding) + self.padding
                    x2 = x1 + self.cell_width
                    y2 = y1 + self.cell_height
                    rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="lightblue")
                    
                    cell_name = f'cell{cell_count}'
                    self.canvas.tag_bind(rect, "<Button-1>", lambda event, cell_name=cell_name: self.on_click(event, cell_name))
                    
                    self.cells[cell_name] = rect
                    cell_count += 1

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, cell_name):
        self.set_cell_color(cell_name, 'black')

    def set_cell_color(self, cell_name, color):
        if cell_name in self.cells:
            self.canvas.itemconfig(self.cells[cell_name], fill=color)
            

        


