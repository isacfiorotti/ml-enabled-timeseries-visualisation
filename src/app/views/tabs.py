import tkinter as tk

class Tabs(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_mediator = data_mediator
        self.canvas = tk.Canvas(self, height=20) # height needs to be consistent with initiation in gui.py
        self.canvas.pack(fill='both', expand=True)
        self.create_data_tabs(self.data_mediator.get_headers())

    def on_resize():
        #TODO Change tab width based on window width
        pass

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
            
            self.canvas.create_rectangle(
                x1,  # x1 position with 3 pixels space between rectangles
                y1,  # y1 position
                x2,  # x2 position
                y2,  # y2 position
                fill='lightgrey',  # Fill color for rectangles
                outline='lightgrey'  # Outline color for rectangles
            )

            text_x = (x1 + x2) / 2
            text_y = (y1 + y2) / 2
            
            self.canvas.create_text(
                text_x,
                text_y,  
                text=f'{headers[i]}',  # Text content
                fill='black',  # Text color
                font=('Arial', 7)
            )
        
    def set_vis_mediator(self, vis_mediator):
        self.vis_midiator = vis_mediator