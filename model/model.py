import os
import sqlite3
from model import *

class Model(refreshModel, getModel):
    def __init__(self):

        db_location = os.path.join("model")
        card_db_exist = os.path.exists(os.path.join(db_location, "cards.db"))

        self.connection = sqlite3.connect("model/cards.db")

        if not card_db_exist:
            print("No card database.")
            self.refresh_database()


    def __del__(self):
        self.connection.close()

    def save_deck(self, deck, title):
        cursor = self.connection.cursor()
        #Defines deck table
        cursor.execute("CREATE TABLE IF NOT EXISTS decks (title TEXT PRIMARY KEY, decklist TEXT)")
        #Inserts data 
        cursor.execute("INSERT OR REPLACE INTO decks (title, decklist) VALUES (?, ?)", (str(title), str(deck)))

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
    