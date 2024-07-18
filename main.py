from control import main_controller

class Main:
    @staticmethod
    def run():
        #Initiates the main controller for the tool.
        controller = main_controller.Controller()
        controller.run()
        return
    
if __name__ == "__main__":
    Main.run()