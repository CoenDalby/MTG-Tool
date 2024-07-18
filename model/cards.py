import json
import os
import requests
import sqlite3

class Model:
    def __init__(self):
        #CHECK IF DATABASE DOESN'T EXIST
        ##IF NO DATABASE: DOWNLOAD JSONS AND SET UP NEW DATABASE
        db_location = os.path.join("model")

        card_db_exist = os.path.exists(os.path.join(db_location, "cards.db"))
        price_db_exist =  os.path.exists(os.path.join(db_location, "prices.db"))

        if not card_db_exist:
            print("No card database.")
            self.populate_card_db(self.download_json("https://mtgjson.com/api/v5/AtomicCards.json"))

        if not price_db_exist:
            print("No price database.")
            
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
    
    def download_json(self, url):
        #Gets json from file server
        print("Downloading JSON")
        response = requests.get(url)
        print("Downloaded")
        
        return response.json()
    
    def populate_card_db(self, cards_json):
        print("Connecting to database")
        #Creates or connects to cards.db
        connection = sqlite3.connect("model/cards.db")
        cursor = connection.cursor()

        #Defines card info table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                name TEXT PRIMARY KEY,
                colorIdentity TEXT,
                colors TEXT,
                convertedManaCost REAL,
                edhrecRank INTEGER,
                edhrecSaltiness REAL,
                firstPrinting TEXT,
                foreignData TEXT,
                identifiers TEXT,
                layout TEXT,
                legalities TEXT,
                manaCost TEXT,
                manaValue REAL,
                printings TEXT,
                subtypes TEXT,
                supertypes TEXT,
                text TEXT,
                type TEXT,
                types TEXT
            )
        ''')

        print("Populating card info")
        card_data = cards_json["data"]
        #Iterates over every card
        for card_key, card_value in card_data.items():
            #Each value is a dictionary containing card info
            card_info = card_value[0]

            #Changes some values into json formats where needed
            foreign_data = json.dumps(card_info.get('foreignData', []))
            identifiers = json.dumps(card_info.get('identifiers', {}))
            legalities = json.dumps(card_info.get('legalities', {}))

            #Inserts appropriate card info into table
            cursor.execute('''
                    INSERT OR REPLACE INTO cards (
                        name, colorIdentity, colors, convertedManaCost, edhrecRank, edhrecSaltiness,
                        firstPrinting, foreignData, identifiers, layout, legalities, manaCost,
                        manaValue, printings, subtypes, supertypes, text, type, types
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    card_info.get('name'),
                    ','.join(card_info.get('colorIdentity', [])),
                    ','.join(card_info.get('colors', [])),
                    card_info.get('convertedManaCost'),
                    card_info.get('edhrecRank'),
                    card_info.get('edhrecSaltiness'),
                    card_info.get('firstPrinting'),
                    foreign_data,
                    identifiers,
                    card_info.get('layout'),
                    legalities,
                    card_info.get('manaCost'),
                    card_info.get('manaValue'),
                    ','.join(card_info.get('printings', [])),
                    ','.join(card_info.get('subtypes', [])),
                    ','.join(card_info.get('supertypes', [])),
                    card_info.get('text'),
                    card_info.get('type'),
                    ','.join(card_info.get('types', []))
                ))
        
        print("Card db done")
        #Commits to database and closes connection
        connection.commit()
        connection.close()