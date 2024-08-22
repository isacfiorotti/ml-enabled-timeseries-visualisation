import tkinter as tk

class GridAxisX(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.canvas = tk.Canvas(self, height=10)
        self.canvas.pack(fill='both', expand=False)

        # Bind the Configure event for resizing
        self.bind('<Configure>', self.on_resize)

        # Initially add the text to the canvas
        self.add_text()
        self.after(10, self.on_resize)
        
    def on_resize(self, event=None):
        # Adjust the text position using relative coordinates
        self.canvas.coords(self.text_id, self.canvas.winfo_width() * 0.5, self.canvas.winfo_height() * 0.5)

    def add_text(self):
        # Create the text at the center of the canvas using relative positioning
        self.text_id = self.canvas.create_text(
            self.canvas.winfo_width() * 0.5, 
            self.canvas.winfo_height() * 0.5,
            text="---------- Time ---------->",
            fill="grey", 
            font=("Helvetica", 10),
            anchor="center"  # Center the text around the given point
        )