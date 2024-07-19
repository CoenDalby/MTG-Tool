
#External Libraries
import tkinter as tk
import ttkbootstrap as ttk

#View classes
from view.deck_tab import DeckTab
from view.database_tab import DBTab

class View:
    def __init__(self, controller):
        self.controller = controller

        #Sets up the main window
        self.window = tk.Tk()
        self.window.eval('tk::PlaceWindow . center')
        self.window.title("MTG Deck Tool")
        self.window.resizable(False,False)

        #Creates the notebook to contain tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(pady=5,padx=5)

        #Adds starting tabs
        self.db_tab = DBTab(self.notebook, self.controller)
        self.notebook.add(self.db_tab.tab, text = "Database")

        self.main_tab = DeckTab(self.notebook, self.controller)
        self.notebook.add(self.main_tab.tab, text = "Import Deck")

        #Opens window with deck tab selected
        self.notebook.select(self.main_tab.tab)

        return
    
    def run(self):
        self.window.mainloop()
        return
        
