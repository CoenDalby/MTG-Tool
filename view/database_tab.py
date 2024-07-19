from ttkbootstrap import *
from tkinter import messagebox

class DBTab():
    
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=540)

        self.total_cards, self.unique_printings, self.percent_valid, self.last_update = self.controller.get_db_stats()

        #Labels for database info
        self.total_cards_label = Label(self.tab, text = "Total Cards: " + str(self.total_cards))
        self.total_cards_label.grid(row = 1, column = 1)

        self.unique_printings_label = Label(self.tab, text = "Unique Printings: " + str(self.unique_printings))
        self.unique_printings_label.grid(row = 2, column = 1)

        self.percent_valid_label = Label(self.tab, text = "Cards With Prices: " + "{:.2f}%".format(self.percent_valid))
        self.percent_valid_label.grid(row = 3, column = 1)

        self.last_update_label = Label(self.tab, text = "Last Update: " + self.last_update)
        self.last_update_label.grid(row = 4, column = 1)

        #Import button
        self.refresh_db_button = Button(self.tab, text = "Refresh Database",
                               command = self.refresh_db)
        self.refresh_db_button.grid(row=5, column =1, padx = 5, pady = 5)
    
    def update_labels(self):
        self.total_cards_label.config(text="Total Cards: " + str(self.total_cards))
        self.unique_printings_label.config(text="Unique Printings: " + str(self.unique_printings))
        self.percent_valid_label.config(text="Cards With Prices: " + "{:.2f}%".format(self.percent_valid))
        self.last_update_label.config(text="Last Update: " + self.last_update)

    def refresh_db(self):
        #Show confirmation dialog
        response = messagebox.askyesno("Confirm Refresh", "Are you sure? Refreshing the database may take a few minutes.")
        if response:
            self.total_cards, self.unique_printings, self.percent_valid, self.last_update = self.controller.refresh_database()
            self.update_labels()
            messagebox.showinfo("Refresh Complete", "Database Refreshed!")
        return