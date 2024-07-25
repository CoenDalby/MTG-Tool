import json
import os
import requests
import sqlite3
import lzma
import io
import datetime

class Model:
    def __init__(self):

        db_location = os.path.join("model")
        card_db_exist = os.path.exists(os.path.join(db_location, "cards.db"))

        self.connection = sqlite3.connect("model/cards.db")

        if not card_db_exist:
            print("No card database.")
            self.refresh_database()


    def __del__(self):
        self.connection.close()

    def get_card_info(self, name):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT *
            FROM cards
            WHERE name = ?
        ''', (name,))

        fields = [
            'foreignData','identifiers',
            'legalities','colorIdentity',
            'colors','printings',
            'subtypes','supertypes','types'
        ]

        column_names = [description[0] for description in cursor.description]
        results = dict(zip(column_names, cursor.fetchone()))

        for field in fields:
            results[field] = self.json_to_list(results[field])

        return results

    def refresh_database(self):
        self.populate_cards(self.download_json("https://mtgjson.com/api/v5/AtomicCards.json"))
        self.populate_prices(self.download_json("https://mtgjson.com/api/v5/AllPrices.json.xz"),
                             self.download_json("https://mtgjson.com/api/v5/AllPrintings.json.xz"))
        
        total_cards, unique_printings, percent_valid, last_update = self.get_db_stats()
        print("Total Cards: " + str(total_cards))
        print("Unique Printings: " + str(unique_printings))
        print("Percentage Valid: {:.2f}%".format(percent_valid))
        print("Last Update: " + last_update)
        return

    def get_db_stats(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM stats")
        row = cursor.fetchone()
        if row:
            total_cards, unique_printings, percent_valid, last_update = row
        return total_cards, unique_printings, percent_valid, last_update
    
    def get_card_price(self, name):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT price
            FROM prices
            WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
        if result == None: return None
        else: return result[0]
    
    def get_dual_lands(self,db_name, include_texts, exclude_texts):
        cursor = self.connection.cursor()
        
        #Colours to include
        include_conditions = " OR ".join([f"text LIKE '%{{{text}}}%'" for text in include_texts])
        
        #Colours to exclude
        exclude_conditions = " AND ".join([f"text NOT LIKE '%{{{text}}}%'" for text in exclude_texts])
        
        #Makes sure only lands are returned
        type_condition = "json_extract(types, '$') LIKE '%land%'"

        #Defines the query
        query = f"""
            SELECT * FROM cards
            WHERE ({include_conditions})
            AND {exclude_conditions}
            AND {type_condition}
        """

        #Executes query and generates results dict
        cursor.execute(query)

        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        #Sorts results by edhrecRank
        results = [card for card in results if card.get("edhrecRank") is not None]
        results_sorted = sorted(results, key=lambda card: card.get("edhrecRank"))
        
        return results_sorted
    
    def list_to_json(self, items):
        return json.dumps(items)

    def json_to_list(self, items):
        return json.loads(items)

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
        cursor = self.connection.cursor()

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
            foreign_data = self.list_to_json(card_info.get('foreignData', []))
            identifiers = self.list_to_json(card_info.get('identifiers', {}))
            legalities = self.list_to_json(card_info.get('legalities', {}))
            colorIdentity = self.list_to_json(card_info.get('colorIdentity', []))
            colors = self.list_to_json(card_info.get('colors', []))
            printings = self.list_to_json(card_info.get('printings', []))
            subtypes = self.list_to_json(card_info.get('subtypes', []))
            supertypes = self.list_to_json(card_info.get('supertypes', []))
            types = self.list_to_json(card_info.get('types', []))
            
            #Inserts appropriate card info into table
            cursor.execute('''
                    INSERT OR REPLACE INTO cards (
                        name, colorIdentity, colors, convertedManaCost, edhrecRank, edhrecSaltiness,
                        firstPrinting, foreignData, identifiers, layout, legalities, manaCost,
                        manaValue, printings, subtypes, supertypes, text, type, types
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    card_info.get('name'),
                    colorIdentity,
                    colors,
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
                    printings,
                    subtypes,
                    supertypes,
                    card_info.get('text'),
                    card_info.get('type'),
                    types
                ))
        
        print("Card table done")

        #Commits to database
        self.connection.commit()
    
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

        print("Populating price info")
        #connects to cards.db
        cursor = self.connection.cursor()

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


        #Calculate database stats
        total_cards = len(name_to_cheapest)
        valid_count = sum(1 for price in name_to_cheapest.values() if price is not None)
        percentage_valid = (valid_count / total_cards) * 100
        unique_printings = len(prices_json["data"])

        current_date = datetime.datetime.now().strftime('%Y-%m-%d')


        #Delete old stats table 
        cursor.execute('DROP TABLE IF EXISTS stats')
        #Create stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                total_cards INTEGER,
                unique_printings INTEGER,
                percent_valid REAL,
                last_update DATE
            )
        ''')
        #Inserts data 
        cursor.execute('''
            INSERT INTO stats (total_cards, unique_printings, percent_valid, last_update)
            VALUES (?, ?, ?, ?)
        ''', (total_cards, unique_printings, percentage_valid, current_date))

        self.connection.commit()

    def save_deck(self, decklist, title):
        cursor = self.connection.cursor()
        print(title)
        print(decklist)
        #Defines card prices table
        cursor.execute("CREATE TABLE IF NOT EXISTS decks (title TEXT PRIMARY KEY, decklist TEXT)")
        #Inserts data 
        cursor.execute("INSERT OR REPLACE INTO decks (title, decklist) VALUES (?, ?)", (str(title), str(decklist)))

        self.connection.commit()
        return
    
    def get_decks(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT title FROM decks")
        result = cursor.fetchall()

        if not result:
            return [""]
        else:
            return [row[0] for row in result]

    def load_deck(self, title):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT decklist
            FROM decks
            WHERE title = ?
        ''', (title,))
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    