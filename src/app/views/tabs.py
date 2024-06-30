import tkinter as tk

class Tabs(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_mediator = data_mediator
        self.canvas = tk.Canvas(self, height=23) # height needs to be consistent with initiation in gui.py
        self.canvas.pack(fill='both', expand=True)
        self.tabs = {}
        self.create_data_tabs(self.data_mediator.get_headers())
        self.current_tab = None

    def on_resize(self):
        #TODO Change tab width based on window width
        pass

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=2, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def create_data_tabs(self, headers):
        rect_width = 120
        rect_height = 20
        x_start = 5
        y_start = 5

        num_rectangles = len(headers)

        for i in range(num_rectangles):
            x1 = x_start + i * (rect_width + 3)
            y1 = y_start
            x2 = x_start + (i + 1) * rect_width + i * 3
            y2 = y_start + rect_height
            
            rect = self.create_rounded_rectangle(
                x1,  # x1 position with 3 pixels space between rectangles
                y1,  # y1 position
                x2,  # x2 position
                y2,  # y2 position
                radius=10,  # Radius for rounded corners
                fill='#DCDCDC',  # Fill color for rectangles
                outline='#DCDCDC'  # Outline color for rectangles
            )

            text_x = (x1 + x2) / 2
            text_y = (y1 + y2) / 2
            
            text = self.canvas.create_text(
                text_x,
                text_y,  
                text=f'{headers[i]}',  # Text content
                fill='grey',  # Text color
                font=('Arial', 10) 
            )
        
            self.tabs[headers[i]] = (rect, text)
            self.canvas.tag_bind(rect, '<Button-1>', lambda e, tab=headers[i]: self.on_click(tab))
            self.canvas.tag_bind(text, '<Button-1>', lambda e, tab=headers[i]: self.on_click(tab))
    
    def on_click(self, tab):
        self.current_tab = tab
        self.vis_mediator.on_tab_click(tab)

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator
