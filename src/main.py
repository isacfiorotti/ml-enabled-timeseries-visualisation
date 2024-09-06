import tkinter as tk
from app.views.gui import MainWindow
from app.controllers.data_mediator import DataMediator
from app.models.database import SQLiteDB
from app.models.data_processor import DataProcessor

from app.config import FILE_PATH
from app.config import WINDOW_TITLE
from app.config import MP_WINDOW_SIZE
from app.config import MP_THRESHOLD
from app.config import GAP_THRESHOLD
from app.config import BASE_SIGNAL_LENGTH
from app.config import CLUSTER_THRESHOLD

from app.models.matrix_profile_model import MatrixProfile
import threading

def main():
    root = tk.Tk()
    root.geometry('1024x768')
    root.title(WINDOW_TITLE)

    data_processor = DataProcessor(FILE_PATH) 

    matrix_profile_model = MatrixProfile(MP_WINDOW_SIZE, MP_THRESHOLD, GAP_THRESHOLD, BASE_SIGNAL_LENGTH, CLUSTER_THRESHOLD)

    db = SQLiteDB(FILE_PATH, data_processor)
    data_mediator = DataMediator(FILE_PATH, db, data_processor, matrix_profile_model)

    matrix_profile_thread = threading.Thread(target=data_mediator.run_matrix_profile_operations)
    matrix_profile_thread.daemon = True
    matrix_profile_thread.start()

    app = MainWindow(root, data_mediator)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()