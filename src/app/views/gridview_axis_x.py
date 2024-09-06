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

        self.canvas.create_text(width / 2, height / 2, text="Time", anchor='center', font=('Arial', 7), fill='grey')
