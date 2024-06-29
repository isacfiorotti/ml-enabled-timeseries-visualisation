import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator

def main():
    root = tk.Tk()
    root.geometry('800x600')

    relation_manager = DataMediator() #TODO change name to dao to better reflect use

    app = MainWindow(root, relation_manager)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()