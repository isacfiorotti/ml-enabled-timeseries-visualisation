import tkinter as tk
from app.gui import MainWindow
from app.signal_relation_manager import SignalRelationManager
from app.vis_mediator import VisMediator

def main():
    root = tk.Tk()
    root.geometry('800x600')

    relation_manager = SignalRelationManager() # change name to dao to better reflect use

    app = MainWindow(root, relation_manager)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()