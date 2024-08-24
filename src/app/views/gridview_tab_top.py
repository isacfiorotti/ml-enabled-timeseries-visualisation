import tkinter as tk

class GridviewTabTop(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent

        self.canvas = tk.Canvas(self, height=10)
        self.canvas.pack(fill='both', expand=False)

        self.canvas_left = tk.Canvas(self.canvas)
        self.canvas_right = tk.Canvas(self.canvas)

        self.canvas_left.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.canvas_right.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        self.text_id_left = self.canvas_left.create_text(
            0, 0,  # Temporary position
            text='Time Grid with Binned Intervals      Bin Size: 25,000', # change to get binsize
            fill="grey", 
            font=("Helvetica", 10),
            anchor="center"
        )

        self.text_id_right = self.canvas_right.create_text(
            0, 0,  # Temporary position
            text='Status: Currently processing cells...', # change to get cells and total cells
            fill="grey", 
            font=("Helvetica", 10),
            anchor="center"
        )

        self.bind("<Configure>", self.on_resize)

        self.after(10, self.on_resize)

    def on_resize(self, event=None):
        # Update canvas sizes and positions
        self.canvas_left.config(width=self.canvas.winfo_width() * 0.5, height=self.canvas.winfo_height())
        self.canvas_right.config(width=self.canvas.winfo_width() * 0.5, height=self.canvas.winfo_height())
        
        # Update text positions
        self.canvas_left.coords(self.text_id_left, self.canvas_left.winfo_width() * 0.5, self.canvas_left.winfo_height() * 0.5)
        self.canvas_right.coords(self.text_id_right, self.canvas_right.winfo_width() * 0.5, self.canvas_right.winfo_height() * 0.5)
