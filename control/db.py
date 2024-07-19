class Controller:
    def refresh_database(self):
        self.model.refresh_database()
        return self.get_db_stats()

    def get_db_stats(self):
        total_cards, unique_printings, percent_valid, last_update = self.model.get_db_stats()
        return total_cards, unique_printings, percent_valid, last_update