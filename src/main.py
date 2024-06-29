import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator

def main():
    root = tk.Tk()
    root.geometry('800x600')

    data_mediator = DataMediator()

    app = MainWindow(root, data_mediator)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()