import tkinter as tk
import squarify # reference in work
import re

class TreemapView(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.data_mediator = data_mediator
        self.nodes = {}
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=True)

    def create_treemap(self, width=None, height=None, node_counts_df=None, labels=None, map_colors=None, cluster_df=None, line_data=None):
        self.canvas.delete('all')

        # color mapping
        color_map = {}
        sorted_labels = sorted(labels, key=self.extract_start)
        color_map = {label: color for label, color in zip(sorted_labels, map_colors)}

        node_counts_sorted = node_counts_df['count'].sort_values(ascending=False)
        node_counts_df = node_counts_df.loc[node_counts_sorted.index]

        labels = node_counts_df['node_id'].tolist()
        node_counts = node_counts_df['count'].tolist()

        colors = [color_map[label] for label in labels]

        if width is None or height is None:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        
        self.canvas.config(width=width, height=height)

        norm_node_counts = squarify.normalize_sizes(node_counts, width, height)
        rects = squarify.squarify(norm_node_counts, 0, 0, width, height)

        for rect, label, color in zip(rects, labels, colors):
            x0, y0, x1, y1 = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            
            if cluster_df is not None:
                rect_line_data = line_data[line_data['node_id'] == label] if line_data is not None else None
                self.draw_children(x0, y0, x1, y1, label, cluster_df, color, rect_line_data)


    def draw_children(self, x0, y0, x1, y1, parent_label, cluster_df, color, line_data=None):

        children_df = cluster_df[cluster_df['node_id'] == parent_label]
        children_df = children_df[['cluster', 'cluster_count']].drop_duplicates()
        
        if not children_df.empty:
            child_counts_sorted = children_df['cluster_count'].sort_values(ascending=False)
            child_counts_df = children_df.loc[child_counts_sorted.index]
            child_labels = child_counts_df['cluster'].tolist()
            child_counts = child_counts_df['cluster_count'].tolist()
    
            child_colors = [color] * len(child_labels)

            self.create_treemap_within(x0, y0, x1, y1, child_counts, child_labels, child_colors, line_data, parent_label)

    def create_treemap_within(self, x0, y0, x1, y1, node_counts, labels, child_colors, line_data=None, parent_label=None):

        norm_node_counts = squarify.normalize_sizes(node_counts, x1 - x0, y1 - y0)
        rects = squarify.squarify(norm_node_counts, x0, y0, x1 - x0, y1 - y0)

        for rect, label, color in zip(rects, labels, child_colors):
            x0_rect, y0_rect, x1_rect, y1_rect = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            rect_id = self.canvas.create_rectangle(x0_rect, y0_rect, x1_rect, y1_rect, fill=color, outline="white")


            if line_data is not None:
                data = line_data[line_data['cluster'] == label]['data'].iloc[0]
                self.draw_line_inside(x0_rect, y0_rect, x1_rect, y1_rect, data)

            self.nodes[rect_id] = {
                'rect_id': rect_id,
                'parent': parent_label,
                'cluster': label,
                'color': color,
                'toggle': False
            }
            
            self.canvas.tag_bind(rect_id, '<Enter>', lambda event, rect_id=rect_id: self.on_enter(event, rect_id))
            self.canvas.tag_bind(rect_id, '<Leave>', self.on_leave)
        

    def draw_line_inside(self, x0, y0, x1, y1, data):
        x0 = x0 + 0.05 * (x1 - x0)
        x1 = x1 - 0.05 * (x1 - x0)
        y0 = y0 + 0.05 * (y1 - y0)
        y1 = y1 - 0.05 * (y1 - y0)

        num_points = len(data)
        step_x = (x1 - x0) / (num_points - 1)
        scaled_data = [(x0 + i * step_x, y1 - (data[i] / max(data)) * (y1 - y0)) for i in range(num_points)]

        self.canvas.create_line(scaled_data, fill='black', width=1)

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, label):
        pass

    def on_enter(self, event, rect_id):
        parent_label = self.nodes[rect_id]['parent']
        color = self.nodes[rect_id]['color']
        label = self.nodes[rect_id]['cluster']
        self.vis_mediator.on_treemap_enter(label, color, parent_label)
        

    def on_leave(self, event):
        self.vis_mediator.on_treemap_leave()
            
    def extract_start(self, label):
        match = re.match(r'(\d+\.\d+)', label)
        return float(match.group()) if match else float('inf')

