class Controller:
    def refresh_database(self):
        self.model.refresh_database()
        return self.get_db_stats()

    def get_db_stats(self):
        total_cards, unique_printings, percent_valid, last_update = self.model.get_db_stats()
        return total_cards, unique_printings, percent_valid, last_update
    
    def get_decklist_titles(self):
        titles = self.model.get_decks()
        return titles
    
    def save_decklist(self, decklist, title):
        self.model.save_deck(decklist, title)

    def load_decklist(self, title):
        decklist = self.model.load_deck(title)
        
        # Replace commas with newlines
        cleaned_decklist = decklist.replace('"', "'").replace("['", "").replace("', '", " \n").replace("']", "")

        return cleaned_decklist
