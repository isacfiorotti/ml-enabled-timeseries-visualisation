import tkinter as tk
from app.gui import MainWindow

def main():
    root = tk.Tk()
    root.geometry('800x600')

    app = MainWindow(root)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()