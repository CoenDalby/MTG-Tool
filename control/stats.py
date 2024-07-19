import matplotlib.pyplot as plt

class Controller:
    def get_charts(self):
        deck_size = 0
        total_cmc = 0

        self.cmcs = {}
        self.colour_counts = {}
        self.card_types = {}
        
        for card in self.decklist:
            card_data = card.get("data")
            card_quantity = card.get("quantity")

            deck_size += card_quantity
            total_cmc += card_quantity*card_data.get("convertedManaCost")

            #Counts each unique CMC in the deck
            if card_data.get("convertedManaCost") in self.cmcs: self.cmcs[card_data.get("convertedManaCost")] += card_quantity
            else: self.cmcs[card_data.get("convertedManaCost")] = card_quantity

            #Counts each unique colour in the deck
            for colour in card_data.get("colorIdentity"): 
                if colour in self.colour_counts: self.colour_counts[colour] += card_quantity
                else: self.colour_counts[colour] = card_quantity
            
            #Counts each unique type in the deck
            for card_type in card_data.get("types"):
                if card_type in self.card_types: self.card_types[card_type] += card_quantity
                else: self.card_types[card_type] = card_quantity


        pie_chart = self.colour_pie(self.colour_counts)
        type_chart = self.type_pie(self.card_types)
        mana_curve = self.mana_curve_chart(self.cmcs)
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