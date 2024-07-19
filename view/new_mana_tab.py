from ttkbootstrap import *


class ManaTab():
    
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=540)

        #Budget tickbox and entry
        self.budget_var = BooleanVar(value=False)
        self.budget_checkbutton = Checkbutton(self.tab, text="Budget ($):", variable=self.budget_var)
        self.budget_checkbutton.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.budget_price = DoubleVar()
        self.budget_entry = Entry(self.tab, textvariable=self.budget_price)
        self.budget_entry.grid(row=1, column=2, padx=5, pady=5)

        #Max card price tickbox and entry 
        self.card_max_var = BooleanVar(value=False)
        self.card_max_checkbutton = Checkbutton(self.tab, text="Max Card Price ($):", variable=self.card_max_var)
        self.card_max_checkbutton.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.max_price = DoubleVar()
        self.max_entry = Entry(self.tab, textvariable=self.max_price)
        self.max_entry.grid(row=2, column=2, padx=5, pady=5)

        #Basic Land Percentage tickbox and slider
        self.basic_land_choice = IntVar(value=1)

        self.basic_land_default = Radiobutton(self.tab, text="Suggest Basic Land %", variable=self.basic_land_choice, value=1)
        self.basic_land_default.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.basic_land_default_label = Label(self.tab, text="(100 - (Colours * 20))%"+" of lands will be basic.")
        self.basic_land_default_label.grid(row=3, column=2, padx=5, pady=5)

        self.basic_land_custom = Radiobutton(self.tab, text="Custom Basic Land %:", variable=self.basic_land_choice, value=2)
        self.basic_land_custom.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.basic_land_slider = Scale(self.tab, from_=0, to=100, orient="horizontal", command=self.update_slider_label)
        self.basic_land_slider.grid(row=4, column=2, padx=5, pady=5)
        self.slider_value_label = Label(self.tab, text="0%")
        self.slider_value_label.grid(row=4, column=3, padx=5, pady=5)

        #Radio buttons for ratio options
        self.land_count_choice = IntVar(value=1)

        self.match_land_count = Radiobutton(self.tab, text="Match Current Land Count", variable=self.land_count_choice, value=1)
        self.match_land_count.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.new_land_count = Radiobutton(self.tab, text="Use New Land Count:", variable=self.land_count_choice, value=2)
        self.new_land_count.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        self.chosen_lands = IntVar()
        self.land_entry = Entry(self.tab, textvariable=self.chosen_lands)
        self.land_entry.grid(row=6, column=2, padx=5, pady=5)
        #Generate lands button
        self.generate_lands_button = Button(self.tab, text="Get Recommended Lands", command=self.generate_lands)
        self.generate_lands_button.grid(row=8, column=1, padx=5, pady=5)
    
    def update_slider_label(self, value):
        self.slider_value_label.config(text=f"{int(float(value))}%")

    def generate_lands(self):
        if self.budget_var.get(): budget = self.budget_entry.get()
        else: budget = float("inf")

        if self.card_max_var.get(): max_card_price = self.max_entry.get()
        else: max_card_price = float("inf")

        if self.basic_land_choice.get() == 1: basic_choice = -1
        else: basic_choice = self.basic_land_slider.get()

        if self.land_count_choice.get() == 1: land_count = -1
        else: land_count = self.chosen_lands.get()

        self.controller.generate_lands(budget, max_card_price, basic_choice)
        return