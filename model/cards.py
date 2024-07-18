import json

class Model:
    def __init__(self):
        with open("model/AtomicCards.json", "r", encoding="utf-8") as file:
            self.card_JSON = json.load(file)
            self.card_data = self.card_JSON["data"]
        self.keys = list(self.card_data.keys())
    
    def get_card_info(self, name):
        card_info = self.card_data[name][0]
        cmc = int(card_info["convertedManaCost"])
        card_type = card_info["types"]
        colours = card_info["colors"]
        return [colours, cmc, card_type]