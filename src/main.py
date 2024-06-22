import tkinter as tk
from app.gui import MainWindow

def main():
    root = tk.Tk()
    root.geometry('800x600')

    # Create instance of signal relation manager and pass into gui

    app = MainWindow(root)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()