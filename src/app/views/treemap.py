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
        self.bind('<Configure>', self.on_resize)
        self.canvas.bind('<Leave>', self.on_leave)

    def on_resize(self, event):

        #TODO Move this to the create_treemap function to allow for better readability
        node_counts = self.data_mediator.get_node_counts()
        labels = self.data_mediator.get_nodes()

        colors = ["#E74C3C", "#3498DB", "#27AE60", "#9B59B6", "#E67E22"] # Modern high-contrast palette for light grey background

        self.width = event.width
        self.height = event.height
        self.canvas.config(width=self.width, height=self.height)

        # Squarify is used to find the optimal arrangement for the treemap.
        norm_node_counts = squarify.normalize_sizes(node_counts, self.width, self.height)
        rects = squarify.squarify(norm_node_counts, 0, 0, self.width, self.height)

        self.create_treemap(rects, labels, colors)

    def create_treemap(self, rects, labels, colors):
        self.canvas.delete('all')
        
        for rect, label, color in zip(rects, labels, colors):
            x0, y0, x1, y1 = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            node_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")
            text = self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill="lightgrey")
            
            self.nodes[label] = {'color':color, 'toggle':False} # keeps track of whether button has been toggled 

            self.canvas.tag_bind(node_id, '<Button-1>', lambda event, label=label: self.on_click(event, label))
            self.canvas.tag_bind(text, '<Button-1>', lambda event, label=label: self.on_click(event, label))

            self.canvas.tag_bind(node_id, '<Enter>', lambda event, label=label: self.on_enter(event, label))
    

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, label):
        toggle = self.nodes[label]['toggle']
        self.vis_mediator.on_treemap_click(label, toggle)

    def on_enter(self, event, label):
        color = self.nodes[label]['color']
        self.vis_mediator.on_treemap_enter(label, color)

    def on_leave(self, event):
        self.vis_mediator.on_treemap_leave()
