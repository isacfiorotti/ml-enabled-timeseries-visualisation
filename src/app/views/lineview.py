import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

class LineView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, *kwargs)
        self.canvas_frame = tk.Frame(self)  # Frame for the canvas
        self.canvas_frame.pack(fill='both', expand=True)
        self.fig = None
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_plot(self, data):

        #drop first col
        data = data.drop(data.columns[0], axis=1)

        x, y = data.iloc[:, 0], data.iloc[:, 1]
        
        # downsample
        x = x[:1000]
        y = y[:1000]

        x = x[::5]
        y = y[::5]

        fig = plt.Figure(figsize=(5, 4), dpi=100, facecolor='#D3D3D3')

        ax = fig.add_subplot(111)
        ax.plot(x, y, color='#2C3E50', linewidth=1)

        # Remove the top and right spines (outlines)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Customize the color of the bottom and left spines
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')

        # Customize the color of the tick labels and ticks
        ax.tick_params(axis='x', colors='gray')
        ax.tick_params(axis='y', colors='gray')

        # Set the color of the axis labels if needed
        ax.xaxis.label.set_color('#C0C0C0')
        ax.yaxis.label.set_color('#C0C0C0')

        # Set the color of the title if needed
        ax.title.set_color('lightgrey')

        # Set the background color of the axis
        ax.set_facecolor('#D3D3D3')

        ax.grid(True, color='gray', linestyle='--', linewidth=0.5)

        return fig

    def create_lineview(self, fig):
        self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        

    