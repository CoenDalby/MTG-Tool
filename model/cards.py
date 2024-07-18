import json
import os
import requests
import sqlite3
import lzma
import io


class Model:
    def __init__(self):
        #CHECK IF DATABASE DOESN'T EXIST
        ##IF NO DATABASE: DOWNLOAD JSONS AND SET UP NEW DATABASE
        db_location = os.path.join("model")

        card_db_exist = os.path.exists(os.path.join(db_location, "cards.db"))

        if not card_db_exist:
            print("No card database.")
            self.populate_cards(self.download_json("https://mtgjson.com/api/v5/AtomicCards.json"))
            self.populate_prices(self.download_json("https://mtgjson.com/api/v5/AllPrices.json.xz"),
                                 self.download_json("https://mtgjson.com/api/v5/AllPrintings.json.xz")
                                 )
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
        print("Downloading: " + url)
        response = requests.get(url)
        print("Downloaded.")

        if url.endswith(".xz"):
            print("Converting .xz to json.")
            with lzma.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as xz_file:
                # Read the decompressed JSON data
                json_data = json.load(xz_file)
        else:
            json_data = response.json()

        return json_data
        
    def populate_cards(self, cards_json):
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
        
        print("Card table done")
        #Commits to database and closes connection
        connection.commit()
        connection.close()
    
    def populate_prices(self, prices_json, printings_json):
        #Get every unique printing ID for each card
        #Partially adapted from 
        #https://rentry.org/mtgjson-tut#looking-up-price-by-card-name
        name_to_uuid = {}
        for set_id in printings_json["data"].keys():
            for card in printings_json["data"][set_id]["cards"]:
                if card["name"] not in name_to_uuid:
                    name_to_uuid[card["name"]] = []
                name_to_uuid[card["name"]].append(card["uuid"])

        def get_cheapest_printing(paper_prices):
            cheapest_price = float("inf")  
            for retailer in paper_prices:
                if retailer in ["tcgplayer", "cardkingdom"]:
                            for date in paper_prices[retailer]["retail"]["normal"]:
                                price = paper_prices[retailer]["retail"]["normal"][date]
                                if price < cheapest_price:
                                    cheapest_price = price
            
            return cheapest_price if cheapest_price != float('inf') else None
    
        #Get cheapest printing for every unique card
        name_to_cheapest = {name: None for name in name_to_uuid.keys()}
        for name, uuid_list in name_to_uuid.items():
            cheapest = None
            for uuid in uuid_list:
                try: cheapest = get_cheapest_printing(prices_json["data"][uuid]["paper"])
                except: pass
            name_to_cheapest[name] = cheapest



        total_items = len(name_to_cheapest)
        none_count = sum(1 for price in name_to_cheapest.values() if price is not None)
        percentage_none = (none_count / total_items) * 100

        print("Unique printings: " + str(len(prices_json["data"])))
        print("Unique cards: " + str(total_items))
        # Print the percentage
        print(f"Percentage of cards with prices: {percentage_none:.2f}%")

        print("Populating price info")
        #connects to cards.db
        conn = sqlite3.connect("model/cards.db")
        cursor = conn.cursor()

        #Defines card prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                name TEXT PRIMARY KEY,
                price REAL
            )
        ''')


        #Populates the table with all card prices
        for name, price in name_to_cheapest.items():
            cursor.execute('''
                INSERT OR REPLACE INTO prices (name, price)
                VALUES (?, ?)
            ''', (name, price))

        print("Price table done")
        #Commits to database and closes connection
        conn.commit()
        conn.close()