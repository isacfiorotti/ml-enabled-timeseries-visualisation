import tkinter as tk
import squarify # reference in work

class TreemapView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.data = data (add param to __init__)
        self.parent = parent
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=True)
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        # Sample data
        data = [500, 300, 200, 100, 50]
        labels = ["A", "B", "C", "D", "E"]
        colors = ["red", "blue", "green", "purple", "orange"]

        self.width = event.height
        self.height = event.width
        self.canvas.config(width=self.width, height=self.height)

        norm_data = squarify.normalize_sizes(data, self.width, self.height)
        rects = squarify.squarify(norm_data, 0, 0, self.width, self.height)

        self.create_treemap(rects, labels, colors)

    def create_treemap(self, rects, labels, colors):
        self.canvas.delete("all")  # Clear the canvas before drawing
        
        for rect, label, color in zip(rects, labels, colors):
            x0, y0, x1, y1 = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill="black")

