import tkinter as tk
from math import ceil, sqrt
from app.views.gridview_axis_y import GridAxisY
from app.views.gridview_axis_x import GridAxisX

class GridView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.cell_starts = None

        # Create a frame to hold the canvas
        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True, side='top')

        self.axis_y = GridAxisY(self.frame)
        self.axis_y.pack(fill='y', side='left')

        # Create a canvas frame
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(fill='both', expand=True, side='right')

        self.canvas = tk.Canvas(self.canvas_frame, background='white')
        self.canvas.pack(fill='both', expand=True)
        self.cells = {}
        self.grid_size = None  # Start with grid_size as None
        self.padding = 3
        self.canvas.bind("<Configure>", self.on_resize)
        self.vis_mediator = None

        self.axis_x = GridAxisX(self)
        self.axis_x.pack(fill='x', side='bottom')

        self.check_for_processed_cells()

    def create_grid(self):
        if self.grid_size is not None:
            self.cols = int(sqrt(self.grid_size))
            self.rows = ceil(self.grid_size / self.cols)
            
            if self.rows * self.cols < self.grid_size:
                self.cols += 1

            self.calculate_cell_dimensions()

    def calculate_cell_dimensions(self):
        if self.width and self.height:
            self.cell_width = (self.width - (self.cols + 1) * self.padding) / self.cols
            self.cell_height = (self.height - (self.rows + 1) * self.padding) / self.rows

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height

        if self.grid_size is not None:
            self.calculate_cell_dimensions()
            self.create_grid_view()
    
    def create_grid_view(self, cell_starts=None):

        self.canvas.delete("all")

        if cell_starts is not None:
            self.cell_starts = cell_starts

        if self.grid_size is not None:
            cell_count = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    if cell_count < self.grid_size:
                        x1 = j * (self.cell_width + self.padding) + self.padding
                        y1 = i * (self.cell_height + self.padding) + self.padding
                        x2 = x1 + self.cell_width
                        y2 = y1 + self.cell_height
                        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FAF9F6", outline="#FAF9F6")
                        
                        cell_name = f'cell_{cell_count}'
                        self.canvas.tag_bind(rect, "<Button-1>", lambda event, cell_name=cell_name: self.on_click(event, cell_name))
                        
                        self.cells[cell_name] = rect
                        cell_count += 1

            # self.check_for_toggles() #disabled to until fixed way treemaps are created and destroyed
            self.check_for_clicked_cell()

            self.axis_y.update_ticks(self.rows, self.cols, self.padding, self.cell_starts)
            self.axis_x.update_ticks(self.cols, self.padding)

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, cell_name):
        self.vis_mediator.on_grid_view_click(cell_name)

    def set_cell_color(self, cell_name, color):
        if cell_name in self.cells:
            self.canvas.itemconfig(self.cells[cell_name], fill=color)

    def check_for_toggles(self):
        if hasattr(self, 'vis_mediator'):
            self.vis_mediator.resolve_treemap_toggles()
    
    def set_grid_size(self, grid_size):
        self.grid_size = grid_size
        self.create_grid()
        self.cell_width = (self.width - (self.cols + 1) * self.padding) / self.cols
        self.cell_height = (self.height - (self.rows + 1) * self.padding) / self.rows
        self.create_grid_view()

    def check_for_processed_cells(self):
        if self.vis_mediator is not None:
            if not self.vis_mediator.is_hovering:
                self.vis_mediator.color_processed_cells()
        self.after(1, self.check_for_processed_cells)

    def check_for_clicked_cell(self):
        if hasattr(self, 'vis_mediator'):
            self.vis_mediator.resolve_cell_click()

    def set_cell_clicked(self, cell_name):
        if cell_name in self.cells:
            self.canvas.itemconfig(self.cells[cell_name], outline='black')

    def set_cell_unclicked(self, cell_name):
        if cell_name in self.cells:
            self.canvas.itemconfig(self.cells[cell_name], outline='#FAF9F6')
