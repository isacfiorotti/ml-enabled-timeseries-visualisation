import tkinter as tk

class GridAxisY(tk.Frame):
    def __init__(self, parent, rows=0, cols=0, padding=0, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self.cell_starts = None
        self.parent = parent
        self.canvas = tk.Canvas(self, width=45)
        self.canvas.pack(fill='both', expand=True)

        self.bind('<Configure>', self.on_resize)
        
    def on_resize(self, event=None):
        self.update_ticks(self.rows, self.cols, self.padding, self.cell_starts)

    def update_ticks(self, rows=None, cols=None, padding=None, cell_starts=None):
        self.canvas.delete('all')
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.cell_starts = cell_starts

        if rows is not None:
            self.rows = rows

        if cols is not None:
            self.cols = cols
        
        if padding is not None:
            self.padding = padding

        # Update ticks only if rows are defined
        if self.rows > 0:
            row_height = (height - (self.rows + 1) * self.padding) / self.rows
            
            if cell_starts is not None:
                for i in range(self.rows):
                    y = i * (row_height + self.padding) + self.padding + (row_height / 2)
                    self.canvas.create_text(width / 1.4, y, text=f"{cell_starts[i][:-4]}", anchor='center', font=('Arial', 5, 'bold'), fill='grey')
                    self.canvas.create_text(width / 2.8, y, text=f"{i*self.cols}", anchor='center', font=('Arial', 6), fill='grey')



        # Draw the Y-axis label but at an offset to not overlap with the grid lines
        offset = 20
        self.canvas.create_text(width / 2 - offset, height / 2, text="First Row Cell ID and  Start Time", anchor='center', font=('Arial', 7), fill='grey', angle=90)