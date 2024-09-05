import tkinter as tk

class GridAxisX(tk.Frame):
    def __init__(self, parent, columns=0, padding=0, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.columns = columns
        self.padding = padding
        self.parent = parent
        self.canvas = tk.Canvas(self, height=10)  # Adjust height as needed for labels
        self.canvas.pack(fill='both', expand=True)

        self.bind('<Configure>', self.on_resize)
        
    def on_resize(self, event=None):
        self.update_ticks()

    def update_ticks(self, columns=None, padding=None):

        self.canvas.delete('all')
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # For now just draw a text centered in the middle of the canvas
        self.canvas.create_text(width / 2, height / 2, text="Time", anchor='center', font=('Arial', 7), fill='grey')

        # self.canvas.delete('all')
        # width = self.canvas.winfo_width()
        # height = self.canvas.winfo_height()

        # if columns is not None:
        #     self.columns = columns
        
        # if padding is not None:
        #     self.padding = padding

        # # Update ticks only if columns are defined
        # if self.columns > 0:
        #     col_width = (width - (self.columns + 1) * self.padding) / self.columns
            
        #     for i in range(self.columns):
        #         x = i * (col_width + self.padding) + self.padding + (col_width / 2)
        #         self.canvas.create_line(x, 0, x, height, fill='grey', width=1)
        #         self.canvas.create_text(x, height - 1, text=str(i + 1), anchor='s')
