import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

class LineView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, *kwargs)
        self.canvas = tk.Canvas(self)
        self.fig = self.generate_plot()
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.canvas.pack(fill='both', expand=True)

    def generate_plot(self):
        #random line plot for testing purposes

        fig = plt.Figure(figsize=(5, 4), dpi=100)
        x = np.linspace(0, 10, 100)
        y = np.random.rand(100)
        fig.add_subplot(111).plot(x, y)

        return fig

    def create_lineview(self, fig):
        self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(fig, master=self.canvas)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        

    