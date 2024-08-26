import tkinter as tk
import squarify # reference in work

class TreemapView(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.data_mediator = data_mediator
        self.nodes = {}
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=True)
        # self.update_treemap()
        # self.canvas.bind('<Configure>', self.on_resize)
        self.canvas.bind('<Leave>', self.on_leave)

    def on_resize(self, event):
        pass
        # The function will not work since create_treemaps needs a node_count and and label, we could store these in self from the create treemap function
        # and just update based on the last available values.

    def create_treemap(self, width=None, height=None, node_counts=None, labels=None, map_colors=None):
        self.canvas.delete('all')

        # node_counts, labels = self.data_mediator.get_node_count_and_labels()

        colors = [map_colors[i % len(map_colors)] for i in range(len(labels))]


        if width is None or height is None:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        
        self.canvas.config(width=width, height=height)

        # Squarify is used to find the optimal arrangement for the treemap.
        norm_node_counts = squarify.normalize_sizes(node_counts, width, height)
        rects = squarify.squarify(norm_node_counts, 0, 0, width, height)
        
        for rect, label, color in zip(rects, labels, colors):
            x0, y0, x1, y1 = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            node_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")
            text = self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill="lightgrey")
            
            self.nodes[label] = {'color':color, 'toggle':False} # keeps track of whether button has been toggled 

            self.canvas.tag_bind(node_id, '<Button-1>', lambda event, label=label: self.on_click(event, label))
            self.canvas.tag_bind(text, '<Button-1>', lambda event, label=label: self.on_click(event, label))
            self.canvas.tag_bind(node_id, '<Enter>', lambda event, label=label: self.on_enter(event, label))
            self.canvas.tag_bind(text, '<Enter>', lambda event, label=label: self.on_enter(event, label))



    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, label):
        # toggle = self.nodes[label]['toggle']
        # self.vis_mediator.on_treemap_click(label, toggle)
        pass

    def on_enter(self, event, label):
        color = self.nodes[label]['color']
        self.vis_mediator.on_treemap_enter(label, color)
        

    def on_leave(self, event):
        self.vis_mediator.on_treemap_leave()
        

    # def update_treemap(self):
    #     # Check if there's new data to process
    #     if self.data_mediator.previous_nodes is not None:
    #         self.create_treemap(self.canvas.winfo_width(), self.canvas.winfo_height())
    #     # Schedule the next update
    #     self.after(1000, self.update_treemap)  # Update every 1000 ms (1 second)

    