import tkinter as tk

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