import tkinter as tk
from PIL import Image, ImageTk

class SettingsIcon(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.add_icon_path = '/Users/isacfiorotti/Documents/COMP4031 - Personal Project/timeseries-visualisation-software/src/app/assets/settings.png'
        self.add_icon_pil = Image.open(self.add_icon_path)
        
        # Calculate the aspect ratio
        aspect_ratio = self.add_icon_pil.width / self.add_icon_pil.height
        new_height = 20
        new_width = int(new_height * aspect_ratio)
        
        # Resize the image while keeping the aspect ratio
        self.add_icon_pil = self.add_icon_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.add_icon = ImageTk.PhotoImage(self.add_icon_pil)
        
        # Create the label with the resized icon
        self.add_icon_label = tk.Label(self.parent, image=self.add_icon, background='#ECECEC', width=new_width, height=new_height)
        self.add_icon_label.pack(side='right', padx=5, pady=2)