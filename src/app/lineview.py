import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

class LineView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, *kwargs)
        self.fig = self.generate_plot()
        self.canvas = self.create_lineview(self.fig)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def generate_plot(self):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        return fig

    def create_lineview(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        return canvas
