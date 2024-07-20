class Controller:

    def generate_lands(self, budget, max_card_price, basic_choice, lands):
        #These values will be infinite unless specified by user
        total = budget
        max_single = max_card_price

        #Overrides land count with user input if needed
        if lands > 0: total_lands = lands
        else: total_lands = self.card_types["Land"]

        deck_colours = len(self.colour_identity)
        print("Calculating non-basics")
        #Calculates amount of non-basic lands to suggest
        if basic_choice > 0:
            nb_lands = round((basic_choice/100)*total_lands)
        elif deck_colours <= 2: 
            #2 or less colour decks will use 20% nb lands
            nb_lands = round(0.2*total_lands)
        else: 
            #3 or more will use 0.2*colours - 0.2 nb lands, 
            #meaning five colour decks use 80% nb lands
            nb_lands = round(((deck_colours*0.2)-0.2)*total_lands)
        print("Calculating pip totals")
        #Calculates total amount of coloured pips in all cards' mana costs
        pip_total = {"W":0,"U":0,"B":0,"R":0,"G":0}
        for card in self.decklist:
            card_info = card.get("data")
            if card_info.get("manaCost") != None:
                for i in card_info.get("manaCost"):
                    if i in pip_total.keys(): pip_total[i] += 1
        
        #Creates a list where each key value is a colour and
        #a number of lands matching the ratio of colour_pips:total_pips
        non_basics_per_colour = self.get_land_distribution(pip_total, nb_lands)

        #Gets empty dictionary of all colour pairs in identity 
        pairs = self.find_pairs(non_basics_per_colour)
        #Populates dictionary with amount of lands needed for each pair
        pair_counts = self.get_pair_counts(non_basics_per_colour, pairs, nb_lands)
        #Gets lands for each pair without duplicates
        suggested_lands, total = self.optimise_lands(pair_counts, total, max_single)
        #Counts and removes failed card additions (where no more budget was left)
        failed_additions = suggested_lands.count(None)
        suggested_lands = [card for card in suggested_lands if card is not None]

        ##Fill up remaining land slots with basics 
        #Gets amount of remaining lands to be added
        remaining_lands = total_lands - nb_lands + failed_additions
        basics_per_colour = self.get_land_distribution(pip_total, remaining_lands)
        basics = {"W":self.model.get_card_info("Plains"),
                  "U":self.model.get_card_info("Island"),
                  "B":self.model.get_card_info("Swamp"),
                  "R":self.model.get_card_info("Mountain"),
                  "G":self.model.get_card_info("Forest")}
        
        #Appends basic lands onto the end of the suggested list 
        for colour, count in basics_per_colour.items():
            while count > 0:
                if len(suggested_lands) < total_lands: 
                    suggested_lands += [basics[colour]]
                count -= 1

        charts = self.get_charts()
        card_list_str = self.list_to_text_suggested(suggested_lands)

        return (failed_additions, total_lands, basics_per_colour, non_basics_per_colour, card_list_str, charts[0])

    def get_land_distribution(self, pip_total, lands):
        lands_per_colour = {}
        for colour, count in pip_total.items():
            lands_per_colour[colour] = round((count/sum(pip_total.values()))*lands)
        
        return lands_per_colour
    
    def find_pairs(self, wubrg):
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
    
    def optimise_lands(self, pair_counts, budget, max_single_price):
        suggestions = []
        land_dict = {}
        max_total = float(budget)
        running_total = 0.0

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

            #Gets a list of lands that can produce either of the colour pair
            land_dict[colour_pair] = self.model.get_dual_lands("cards_test.db", in_pair, not_in_pair)
            #Removes already suggested cards from colour_pair's list of lands 
            land_dict[colour_pair] = [card for card in land_dict[colour_pair] if card not in suggestions]
            
            #Gets a dictionary of prices for all cards, replacing None values with 0.0
            price_lookup = {card.get("name"):self.model.get_card_price(card.get("name")) for card in land_dict[colour_pair]}
            price_lookup = {name:price if price is not None else 0.0 for name,price in price_lookup.items()}

            #Removes all cards above max single price
            land_dict[colour_pair] = [card for card in land_dict[colour_pair] if price_lookup[card.get("name")] < max_single_price]



            #List to hold new cards
            cards_in_budget = []
            #Float to store current total of colour pair 
            pair_total = 0.0
            #The portion of the total that can be spent on this pair
            adjusted_max_total = max_total*(pair_counts[colour_pair]/sum(pair_counts.values()))
            #Iterates over all found cards

            for card in land_dict[colour_pair]:

                #Gets the card price
                price = price_lookup[card.get("name")]
                #Only add if its price wouldn't put the total past the max,
                #and if there is space in the list of suggestions.
                if pair_total + price < adjusted_max_total and len(cards_in_budget) < pair_counts[colour_pair]: 
                    cards_in_budget.append(card)
                    pair_total += price
            
            #Adds None to pad space if not enough cards were found
            while len(cards_in_budget) < pair_counts[colour_pair]:
                cards_in_budget += [None]
            #Adds new cards to suggestions list and updates running total  
            suggestions += cards_in_budget
            running_total += pair_total

        return suggestions, running_total