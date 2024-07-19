class Controller:

    def set_decklist(self, decklist_string, title_entry):
        #Clears the current deck info
        self.decklist = []
        self.colour_identity = []
        #Splits up each line of the string into quantity/card name
        for card in decklist_string:
            #Ignores lines with ### at the start, used for comments/dividers
            if card.startswith("###"):
                continue
            #Splits the line into quantity and card name
            card = card.split(" ", 1)
            name, quantity = card[1], card[0]
            #Gets info about the card
            card_info = self.model.get_card_info(name)
            card_dict = {"data": card_info, 
                            "quantity": float(quantity)}
            #Appends it and its quantity to the dictionary
            self.decklist.append(card_dict)
            #Updates colour identity if new one found
            for colour in card_info["colorIdentity"]:
                if colour not in self.colour_identity: self.colour_identity.append(colour)
        return

