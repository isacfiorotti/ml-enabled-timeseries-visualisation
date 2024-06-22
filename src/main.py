import tkinter as tk
from app.gui import MainWindow
from app.relation_manager import RelationManager
from app.vis_mediator import VisMediator

def main():
    root = tk.Tk()
    root.geometry('800x600')

    relation_manager = RelationManager() # change name to dao to better reflect use

    app = MainWindow(root, relation_manager)
    app.pack(fill='both', expand=True)
    app.mainloop()

if __name__ == "__main__":
    main()