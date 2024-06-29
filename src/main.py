import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator
from app.models.database import SQLiteDB

def main():
    root = tk.Tk()
    root.geometry('800x600')

    #TODO database should be created dynamically based on files which are in the data directory
    #TODO add function that checks for the data folder and checks if there are already files
    db = SQLiteDB('tkinter-health-data-visualisation/src/app/data/data.csv')

    data_mediator = DataMediator()

    app = MainWindow(root, data_mediator)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()