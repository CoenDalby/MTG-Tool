from ttkbootstrap import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as tkagg 

class StatsTab():
    
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.tab = Frame(notebook)
        self.tab.grid_propagate(False)
        self.tab.config(width=960, height=600)

        self.charts = controller.get_charts()

        #Display Chart 1
        pie = tkagg(self.charts[0], master=self.tab)
        pie.draw()
        pie.get_tk_widget().grid(row=0, column=0, padx= 5, pady = 5)
        pie.get_tk_widget().config(width=480, height=270)

        #Display Chart 2
        pie = tkagg(self.charts[1], master=self.tab)
        pie.draw()
        pie.get_tk_widget().grid(row=0, column=1, padx= 5, pady = 5)
        pie.get_tk_widget().config(width=480, height=270)

        #Display Chart 3
        pie = tkagg(self.charts[2], master=self.tab)
        pie.draw()
        pie.get_tk_widget().grid(row=1, column=0, columnspan = 2, padx= 5, pady = 5)
        pie.get_tk_widget().config(width=960, height=270)

