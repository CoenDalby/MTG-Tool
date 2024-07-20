from ttkbootstrap import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as tkagg 

class ManaStatsTab():
    
    def __init__(self, notebook, controller, info):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=600)
        
        failed_additions, total_lands, basics_per_colour, non_basics_per_colour, card_list_str, colour_chart = info
        basics = sum(basics_per_colour.values())
        non_basics = int(total_lands - basics)
        info_string = (
            f"Requested Land total: {str(int(total_lands))}\n \n"
            f"Basics: {basics}\n \n"
            f"Non-basics: {non_basics}\n \n"
            f"Replaced with basics: {failed_additions}\n \n"
            f"New deck list: \n"
            f"{card_list_str}"
        )
        
        #Display completed decklist
        self.decklist_field = Text(self.tab,
                              width = 50, height = 30,
                              wrap = "word")
        self.decklist_field.grid(row=0,column =0, columnspan=3, rowspan=3,
                                padx=5, pady=5, sticky="ew")
        self.decklist_field.insert("1.0", info_string)
        self.decklist_field.config(state="disabled")

        #Scrollbar
        self.deck_scrollbar = Scrollbar(self.tab, command=self.decklist_field.yview)
        self.deck_scrollbar.grid(row=0, column=3, rowspan=3, sticky='nsew')
        self.decklist_field['yscrollcommand'] = self.deck_scrollbar.set

        #Display spell Colour distribution 
        pie = tkagg(colour_chart, master=self.tab)
        pie.draw()
        pie.get_tk_widget().grid(row=0, column=4, padx= 5, pady = 5)
        pie.get_tk_widget().config(width=400, height=270)

        pie2 = tkagg(self.controller.mana_production_pie(), master = self.tab)
        pie2.draw()
        pie2.get_tk_widget().grid(row=1, column=4, padx= 5, pady = 5)
        pie2.get_tk_widget().config(width=480, height=270)
    
    def import_deck(self):
        print("Ding Dong!")
        return