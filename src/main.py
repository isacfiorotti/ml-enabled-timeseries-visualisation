import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator
from app.models.database import SQLiteDB
from app.models.data_processor import DataProcessor
from app.config import FILE_PATH
from app.config import WINDOW_TITLE

def main():
    root = tk.Tk()
    root.geometry('800x600')
    root.title(WINDOW_TITLE)

    data_processor = DataProcessor(FILE_PATH) 

    #TODO add function that checks for the data folder and checks if there are already files
    db = SQLiteDB(FILE_PATH, data_processor)

    data_mediator = DataMediator(FILE_PATH, db, data_processor)

    app = MainWindow(root, data_mediator)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()