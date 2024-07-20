class Model:
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
    
    def get_decks(self):
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT title FROM decks")

        result = cursor.fetchall()

        if result == None: return [""]
        else: [row[0] for row in result]