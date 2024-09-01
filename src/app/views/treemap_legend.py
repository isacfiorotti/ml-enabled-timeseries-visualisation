import tkinter as tk

class TreemapLegend(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.canvas = tk.Canvas(self, width=120)
        self.canvas.pack(fill='both', expand=False)

        self.bind('<Configure>', self.on_resize)

    def draw_legend(self, colors, labels):
        self.canvas.delete("all")

        title = "Treemap Legend"
        self.canvas.create_text(60, 10, text=title, fill="grey", font=("Arial", 10, "bold"))

        # Starting y position for the first legend item
        y_position = 30

        for color, label in zip(colors, labels):
            self.canvas.create_rectangle(10, y_position, 30, y_position + 20, fill=color, outline=color)
            self.canvas.create_text(50, y_position + 10, anchor='w', text=label, fill="grey", font=("Arial", 8))
            y_position += 30

    def on_resize(self, event):
        self.height = event.height
        self.canvas.config(height=self.height)

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator