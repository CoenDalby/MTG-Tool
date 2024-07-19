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

    def generate_lands(self, budget, max_card_price, basic_choice):
        #Calculates total amount of coloured pips in all cards' mana costs
        pip_total = {"W":0,"U":0,"B":0,"R":0,"G":0}
        for card in self.decklist:
            card_info = card.get("data")
            if card_info.get("manaCost") != None:
                for i in card_info.get("manaCost"):
                    if i in pip_total.keys(): pip_total[i] += 1
        
        total_lands = self.card_types["Land"]
        deck_colours = len(self.colour_identity)
        if deck_colours <= 2: 
            #2 or less colour decks will use 20% nb lands
            nb_lands = round(0.2*total_lands)
        else: 
            #3 or more will use 0.2*colours - 0.2 nb lands, 
            #meaning five colour decks use 80% nb lands
            nb_lands = round(((deck_colours*0.2)-0.2)*total_lands)
        #Creates a list where each key value is a colour and
        #a number of lands matching the ratio of colour_pips:total_pips
        lpc = {}
        for colour, count in pip_total.items():
            lpc[colour] = round((count/sum(pip_total.values()))*nb_lands)

        #Gets empty dictionary of all colour pairs in identity 
        pairs = self.find_pairs(lpc)
        #Populates dictionary with amount of lands needed for each pair
        pair_counts = self.get_pair_counts(lpc, pairs, nb_lands)
        #Gets lands for each pair without duplicates
        dual_lands = self.recommend_dual_lands(pair_counts, 0, 0)
        print(len(dual_lands))
        return
    
    def find_pairs(self, wubrg):
        print(wubrg)
        #Creates list of all colours > 0
        colours = [key for key, value in wubrg.items() if value > 0]
        result = {}
        if len(colours) > 1:
            #For each colour in colours
            for colour1 in range(len(colours)):
                #Iterate over all colours after it to avoid duplicates
                for colour2 in range(colour1 + 1, len(colours)):
                    key1 = colours[colour1]
                    key2 = colours[colour2]
                    #Store the tuple describing the colour pair
                    result[(key1, key2)] = 0
        else: 
            #Ensures non basics are found for mono decks
            result[colours[0], colours[0]] = 0
        return result

    def get_pair_counts(self, colours, pairs, pair_count):
        #Colours still needing lands
        remaining_colours = colours
        #Pairs of colours that can still be added
        remaining_pairs = [pair for pair in pairs.keys()]
        pair_counts = pairs
        count = 0
        #If there's any possible pairs left and less than the amount needed have been added
        while len(remaining_pairs) > 0 and count <= pair_count:
            #Iterate over the remaining pairs
            for pair in remaining_pairs:
                #Check if this mana combo still needs lands
                if remaining_colours[pair[0]] > 0 and remaining_colours[pair[1]] > 0:
                    #Subtract their mana contribution from remaining colours
                    remaining_colours[pair[0]] -= 0.5
                    remaining_colours[pair[1]] -= 0.5
                    #Increment the corresponding pair count
                    pair_counts[pair] += 1
                    #Increment the amount of lands added so far
                    count += 1
                else:
                    #If they're not needed any more, remove them from the list 
                    remaining_pairs.remove(pair)

        #Returns a dictionary of mana pairs and needed quantity
        return pair_counts
    
    def recommend_dual_lands(self, pair_counts, budget, max_single_price):
        suggestions = []
        current_total = 0.0
        land_dict = {}

        #First gets a list of lands for every
        #colour pair in pair_counts
        for colour_pair in list(pair_counts.keys()):
            not_in_pair = ["W","U","B","R","G"]
            in_pair = []

            #Removes colours in current colour_pair from one list 
            #and appends them to another
            for letter in colour_pair:
                if letter in not_in_pair:
                    not_in_pair.remove(letter)
                    in_pair.append(letter)
            print("Pair: " + str(in_pair))

            #Gets a list of lands that can produce either of the colour pair
            land_dict[colour_pair] = self.model.get_dual_lands("cards_test.db", in_pair, not_in_pair)

            #Removes already suggested cards from colour_pair's list of lands 
            land_dict[colour_pair] = [card for card in land_dict[colour_pair] if card not in suggestions]

            #Adds the first pair_counts[colour_pair] amount 
            #of cards from land_dict[colour_pair] to suggestions list 
            for card in land_dict[colour_pair][:pair_counts[colour_pair]]:
                suggestions.append(card)

        return suggestions    