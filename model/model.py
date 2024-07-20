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

    def save_deck(self, string, title):
        cursor = self.connection.cursor()

        #Defines card prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                title TEXT PRIMARY KEY,
                decklist TEXT,
            )
        ''')
        #Inserts data 
        cursor.execute('''
            INSERT INTO decks (title, decklist)
            VALUES (?, ?)
        ''', (title, string))

        self.connection.commit()
        return
    

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
    