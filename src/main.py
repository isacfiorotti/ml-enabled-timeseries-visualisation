import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator
from app.models.database import SQLiteDB
from app.models.data_processor import DataProcessor
from app.config import FILE_PATH
from app.config import WINDOW_TITLE
from app.models.matrix_profile_model import MatrixProfile
import threading

def main():
    root = tk.Tk()
    root.geometry('1024x768')
    root.title(WINDOW_TITLE)

    data_processor = DataProcessor(FILE_PATH) 

    matrix_profile_model = MatrixProfile(100, 3, 0.01, 80, 15)

    #TODO add function that checks for the data folder and checks if there are already files
    db = SQLiteDB(FILE_PATH, data_processor)
    data_mediator = DataMediator(FILE_PATH, db, data_processor, matrix_profile_model)

    # Start a background thread for the matrix profile model operations
    matrix_profile_thread = threading.Thread(target=data_mediator.run_matrix_profile_operations)
    matrix_profile_thread.daemon = True  # Daemonize thread to ensure it exits when the main program exits
    matrix_profile_thread.start()

    app = MainWindow(root, data_mediator)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()