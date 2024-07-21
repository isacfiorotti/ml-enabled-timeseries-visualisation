import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider

class LineView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas_frame = tk.Frame(self)  # Frame for the canvas
        self.canvas_frame.pack(fill='both', expand=True)
        self.fig = None
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables for scrolling
        self.is_dragging = False
        self.start_drag_x = None
        self.initial_index = 0
        self.last_mouse_x = None
        self.display_count = 500
        self.scroll_speed = 2
        self.update_threshold = 5

    def generate_plot(self, data):
        # Drop first column
        data = data.drop(data.columns[0], axis=1)

        x, y = data.iloc[:, 0], data.iloc[:, 1]

        # Downsample for faster rendering
        x = x[::5]
        y = y[::5]

        self.data_x = x.values
        self.data_y = y.values

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.subplots_adjust(bottom=0.15)  # Adjust the bottom margin

        self.line, = self.ax.plot(self.data_x[:self.display_count], self.data_y[:self.display_count], lw=0.5)
        self.ax.set_xlim(0, self.display_count - 1)
        self.ax.set_ylim(np.min(self.data_y[:self.display_count]), np.max(self.data_y[:self.display_count]))
        self.update_x_axis_labels(0)

        # Connect the events to the handlers
        self.canvas_fig.mpl_connect('button_press_event', self.on_press)
        self.canvas_fig.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas_fig.mpl_connect('button_release_event', self.on_release)

        self.ax_slider_index = plt.axes([0.1, 0.05, 0.8, 0.02], facecolor='lightgoldenrodyellow')
        self.slider_index = Slider(self.ax_slider_index, '', 0, len(self.data_x) - self.display_count, valinit=0, valstep=1)
        self.slider_index.valtext.set_visible(False)  # Hide the value text
        self.slider_index.on_changed(self.slider_index_update)

        return self.fig

    def create_lineview(self, fig):
        self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig = fig
        self.fig.canvas.draw_idle()  # Force a redraw to adjust the layout

    def update_display(self, start_index):
        if start_index < 0 or start_index + self.display_count > len(self.data_x):
            return
        new_data_x = self.data_x[start_index:start_index + self.display_count]
        new_data_y = self.data_y[start_index:start_index + self.display_count]
        self.line.set_data(np.arange(start_index, start_index + self.display_count), new_data_y)
        self.ax.set_xlim(start_index, start_index + self.display_count - 1)
        self.ax.set_ylim(np.min(new_data_y), np.max(new_data_y))
        self.update_x_axis_labels(start_index)
        
        self.fig.canvas.draw_idle()

    def update_x_axis_labels(self, start_index):
        end_index = start_index + self.display_count
        ticks = np.linspace(start_index, end_index - 1, num=10, dtype=int)
        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels([str(self.data_x[t]) for t in ticks], ha='right', fontsize=6)

    def on_press(self, event):
        if event.inaxes == self.ax:
            self.is_dragging = True
            self.start_drag_x = event.xdata
            self.initial_index = int(self.slider_index.val)
            self.last_mouse_x = event.xdata

    def on_motion(self, event):
        if self.is_dragging and event.inaxes == self.ax:
            current_mouse_x = event.xdata
            if abs(current_mouse_x - self.last_mouse_x) >= self.update_threshold:
                delta_x = self.start_drag_x - current_mouse_x
                delta_index = int(delta_x * self.scroll_speed)
                new_start_index = self.initial_index + delta_index
                new_start_index = max(0, min(new_start_index, len(self.data_x) - self.display_count))
                self.update_display(new_start_index)
                self.slider_index.set_val(new_start_index)
                self.last_mouse_x = current_mouse_x

    def on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.start_drag_x = None
            self.last_mouse_x = None

    def slider_index_update(self, val):
        start_index = int(val)
        self.update_display(start_index)