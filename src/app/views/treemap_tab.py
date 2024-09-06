import tkinter as tk

class TreemapTab(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.canvas = tk.Canvas(self, height=23)
        self.canvas.pack(fill='both', expand=True)
        self.tabs = {}
        self.current_tab = None
        self.headers = ['Duration (s)', 'Amplitude']
        self.create_tabs(self.headers)

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

    def create_tabs(self, headers, color='#DCDCDC'):
        rect_width = 120
        rect_height = 15
        x_start = 3
        y_start = 5


        num_rectangles = len(self.headers)

        for i in range(num_rectangles):
            x1 = x_start + i * (rect_width + 3)
            y1 = y_start
            x2 = x_start + (i + 1) * rect_width + i * 3
            y2 = y_start + rect_height
            
            rect = self.create_rounded_rectangle(
                x1,
                y1, 
                x2,
                y2,
                radius=10,
                fill=color,
                outline=color 
            )

            text_x = (x1 + x2) / 2
            text_y = (y1 + y2) / 2
            
            text = self.canvas.create_text(
                text_x,
                text_y,  
                text=f'{headers[i]}',
                fill='grey', 
                font=('Arial', 10) 
            )
        
            self.tabs[headers[i]] = (rect, text)
            self.canvas.tag_bind(rect, '<Button-1>', lambda e, tab=headers[i]: self.on_click(tab))
            self.canvas.tag_bind(text, '<Button-1>', lambda e, tab=headers[i]: self.on_click(tab))
    
    def on_click(self, tab):
        self.set_current_tab_color(tab)
        self.vis_mediator.on_treemap_tab_click(tab)

    def set_current_tab_color(self, tab):
        if self.current_tab:
            prev_rect, prev_text = self.tabs[self.current_tab]
            self.canvas.itemconfig(prev_rect, fill='#DCDCDC', outline='#DCDCDC')
            self.canvas.itemconfig(prev_text, fill='grey')

        self.current_tab = tab
        rect, text = self.tabs[tab]

        self.canvas.itemconfig(rect, fill='#A9A9A9', outline='#A9A9A9')
        self.canvas.itemconfig(text, fill='#F0F0F0')

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator