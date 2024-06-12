import tkinter as tk
from app.gui import MainApp

def main():
    root = tk.Tk()
    root.geometry('800x600')

    app = MainApp(root)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()