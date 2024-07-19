from view.window import View
from model.model import Model
from control import *

class Controller(StatsControl, DBControl, CardControl, SuggestControl):

    def __init__(self):
        #Create the model/view classes to be used
        self.model = Model()
        self.view = View(self)
        
        #Empty list that will contain dictionaries of card data/quantity
        self.decklist = []
        return
    
    def run(self):
        self.view.run()
        return