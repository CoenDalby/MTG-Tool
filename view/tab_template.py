from ttkbootstrap import *


class TabTemplate():
    
    def __init__(self, notebook):
        self.notebook = notebook
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=540)

        #Import button
        self.import_button = Button(self.tab, text = "Import",
                               command = self.import_deck)
        self.button.grid(row=0, column =2,padx = 5, pady = 5)
    
    def import_deck(self):
        print("Ding Dong!")
        return