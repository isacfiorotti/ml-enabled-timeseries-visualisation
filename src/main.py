import tkinter as tk
from app.gui import MainWindow
from app.signal_relation_manager import SignalRelationManager

def main():
    root = tk.Tk()
    root.geometry('800x600')

    # Create instance of signal relation manager and pass into gui
    relation_manager = SignalRelationManager()

    app = MainWindow(root, relation_manager)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()