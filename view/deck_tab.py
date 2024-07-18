from ttkbootstrap import *
from view.stats_tab import StatsTab

class DeckTab():
    
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=600)

        #Decklist field
        self.decklist_field = Text(self.tab,
                              width = 50, height = 35,
                              wrap = "word")
        self.decklist_field.grid(row=0,column = 0, columnspan=3, rowspan = 3,
                                padx = 5, pady = 5)
        self.decklist_field.insert("1.0", "Enter cards as [quantity] [name]")
        
        #Decklist scrollbar
        self.deck_scrollbar = Scrollbar(self.tab, command=self.decklist_field.yview)
        self.deck_scrollbar.grid(row=0, column=3, rowspan = 3, sticky='nsew')
        self.decklist_field['yscrollcommand'] = self.deck_scrollbar.set
        
        #Import button
        self.import_button = Button(self.tab, text = "Import",
                               command = self.import_deck)
        self.import_button.grid(row=3, column =2,padx = 5, pady = 5)
        self.tab_count = 0

        #Clear button
        self.clear_button = Button(self.tab, text = "Clear",
                                   command = self.clear_field)
        self.clear_button.grid(row=3, column =1, padx = 5, pady = 5)
        self.tab_count = 0
        
        self.success_label = Label(self.tab, text = "Awaiting new list.")
        self.success_label.grid(row = 1, column = 4)
    
    def import_deck(self):
        #Deletes all other tabs as they are using old data
        tab_list = self.notebook.tabs()
        for tab_id in tab_list:
            if tab_id != str(self.tab):
                self.notebook.forget(tab_id)
        
        #Sets the decklist to be used by the controller
        decklist = self.decklist_field.get("1.0", "end-1c")
        decklist = decklist.splitlines()
        self.controller.set_decklist(decklist)

        #Creates the new stats tab that will display graphs
        new_tab = StatsTab(self.notebook, self.controller)
        self.notebook.add(new_tab.tab, text = "Stats Tab")

        #Update success label
        self.success_label.config(text = "Deck imported!")
        self.success_label.after(3000, lambda: self.success_label.config(text="Awaiting new list."))

    
    def clear_field(self):
        self.decklist_field.delete('1.0', END)