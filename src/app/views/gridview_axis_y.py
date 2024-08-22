import tkinter as tk

class GridAxisY(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.canvas = tk.Canvas(self, width=10)
        self.canvas.pack(fill='both', expand=True)

        self.bind('<Configure>', self.on_resize)

        self.add_text()
        self.after(10, self.on_resize)
        
    def on_resize(self, event=None):
        self.canvas.coords(self.text_id, self.canvas.winfo_width() * 0.5, self.canvas.winfo_height() * 0.5)

    def add_text(self):
        self.text_id = self.canvas.create_text(
            self.canvas.winfo_width() * 0.5, 
            self.canvas.winfo_height() * 0.5,
            text="----------- Time ----------->",
            fill="grey", 
            font=("Helvetica", 10),
            anchor="center",
            angle=270
        )