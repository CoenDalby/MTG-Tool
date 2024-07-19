from ttkbootstrap import *
from view.stats_tab import StatsTab
from view.new_mana_tab import ManaTab

class DeckTab():
    
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=600)

        #Deck title and label
        self.deck_title = StringVar()
        self.title_entry = Entry(self.tab, textvariable=self.deck_title)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.title_label = Label(self.tab, text="Deck Name:")
        self.title_label.grid(row=0, column=0, padx=5, pady=5)

        #Success label
        self.success_label = Label(self.tab, text = "Enter a list to import. \n"
                                                    "Enter a title to save deck list.")
        self.success_label.grid(row=0, column=2)
        
        #Decklist field
        self.decklist_field = Text(self.tab,
                              width = 50, height = 30,
                              wrap = "word")
        self.decklist_field.grid(row=1,column =0, columnspan=3, rowspan=3,
                                padx=5, pady=5, sticky="ew")
        self.decklist_field.insert("1.0", "Enter cards as [quantity] [name]")
        
        
        #Decklist scrollbar
        self.deck_scrollbar = Scrollbar(self.tab, command=self.decklist_field.yview)
        self.deck_scrollbar.grid(row=1, column=3, rowspan=3, sticky='nsew')
        self.decklist_field['yscrollcommand'] = self.deck_scrollbar.set
        
        #Import button
        self.import_button = Button(self.tab, text = "Import from list",
                               command = self.import_deck)
        self.import_button.grid(row=4, column=2,padx=5, pady=5)
        self.tab_count = 0

        #Clear button
        self.clear_button = Button(self.tab, text = "Clear",
                                   command = self.clear_field)
        self.clear_button.grid(row=4, column=1, padx=5, pady=5)
        self.tab_count = 0

        #Dropdown for deck loading
        self.dropdown_value = StringVar()
        self.dropdown_value.set("Select saved deck list")
        self.dropdown_menu = OptionMenu(self.tab, self.dropdown_value, [])
        self.dropdown_menu.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Load Deck button
        self.load_button = Button(self.tab, text="Load Deck", command = None)
        self.load_button.grid(row=5, column=2, padx=5, pady=5)
    
    def import_deck(self):
        titles_to_keep = ["Import Deck", "Database"]
        #Deletes all other tabs as they are using old data
        tab_list = self.notebook.tabs()
        for tab_id in tab_list:
            # Get the title of the tab
            tab_title = self.notebook.tab(tab_id, 'text')

            # Check if the tab title is not in the list of titles to keep
            if tab_title not in titles_to_keep:
                self.notebook.forget(tab_id)  # Delete the tab
        
        #Sets the decklist to be used by the controller
        decklist = self.decklist_field.get("1.0", "end-1c")
        decklist = decklist.splitlines()
        self.controller.set_decklist(decklist, self.deck_title.get())

        #Creates the new stats tab that will display graphs
        new_tab = StatsTab(self.notebook, self.controller)
        self.notebook.add(new_tab.tab, text = "Deck Stats")

        #Creates the new tab for getting landbases
        new_tab = ManaTab(self.notebook, self.controller)
        self.notebook.add(new_tab.tab, text = "Generate Landbase")

        #Update success label
        self.success_label.config(text = "Deck imported!                  ")
        self.success_label.after(3000, lambda: self.success_label.config(text="Enter a list to import. \n"
                                                                              "Enter a title to save deck list."))

    
    def clear_field(self):
        self.decklist_field.delete('1.0', END)