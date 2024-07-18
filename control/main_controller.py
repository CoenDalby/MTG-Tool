from view.window import View
from model.cards import Model
import matplotlib.pyplot as plt

class Controller:

    def __init__(self):
        #Create the model/view classes to be used
        self.model = Model()
        self.view = View(self)
        
        #Empty list that will contain cards
        #[Name, Quantity, Cost, CMC, Types]
        self.decklist = []
        return
    
    def run(self):
        self.view.run()
        return

    def set_decklist(self, decklist_string):
        #Clears the old decklist
        self.decklist = []
        #Splits up each line of the string into quantity/card name
        for card in decklist_string:
            card = card.split(" ", 1)
            name, quantity = card[1], card[0]
            colours, cmc, card_type = self.model.get_card_info(name)
            card_dict = {"name": name, 
                         "quantity": float(quantity), 
                         "colours":colours, 
                         "cmc":cmc, 
                         "type":card_type}
            self.decklist.append(card_dict)
        return
    
    def get_charts(self):
        deck_size = 0
        total_cmc = 0
        cmcs = {}
        colours = {}
        card_types = {}
        for card in self.decklist:
            deck_size += card["quantity"]
            total_cmc += card["quantity"]*card["cmc"]

            #Counts each unique CMC in the deck
            if card["cmc"] in cmcs: cmcs[card["cmc"]] += card["quantity"]
            else: cmcs[card["cmc"]] = card["quantity"]

            #Counts each unique colour in the deck
            for colour in card["colours"]: 
                if colour in colours: colours[colour] += card["quantity"]
                else: colours[colour] = card["quantity"]
            
            #Counts each unique type in the deck
            for card_type in card["type"]:
                if card_type in card_types: card_types[card_type] += card["quantity"]
                else: card_types[card_type] = card["quantity"]


        pie_chart = self.colour_pie(colours)
        type_chart = self.type_pie(card_types)
        mana_curve = self.mana_curve_chart(cmcs)
        return [pie_chart, type_chart, mana_curve]

    def colour_pie(self, colours):
        labels = list(colours.keys())
        sizes = list(colours.values())
        pie = plt.figure(figsize=(8,8))
        plt.pie(sizes, labels = labels, autopct= "%1.1f%%", textprops={"fontsize":10})
        plt.axis("equal")
        plt.title("Colour Distribution")
        return pie
    
    def type_pie(self, card_types):
        labels = list(card_types.keys())
        sizes = list(card_types.values())
        pie = plt.figure(figsize=(8,8))
        plt.pie(sizes, labels = labels, autopct= "%1.1f%%", textprops={"fontsize":10})
        plt.axis("equal")
        plt.title("Type Distribution")
        return pie
    
    def mana_curve_chart(self, cmcs):
        sorted_dict = {key: cmcs[key] for key in sorted(cmcs)}
        labels = list(sorted_dict.keys())
        sizes = list(sorted_dict.values())
        line = plt.figure(figsize=(8,8))
        plt.plot(labels, sizes)
        plt.xlabel('Costs')
        plt.ylabel('Quantity')
        plt.title("Mana Curve")
        return line
    
