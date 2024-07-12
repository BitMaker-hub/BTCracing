import threading
import time
from ui import ui_show, UI

# Variables globales para la pantalla actual y los parámetros
current_screen = None
screen_params = {}
ui_thread_instance = None

# Función para cambiar la pantalla
def change_screen(screen, params):
    global current_screen, screen_params, ui_thread_instance
    current_screen = screen
    screen_params = params

    if ui_thread_instance and ui_thread_instance.is_alive():
        # Terminar el hilo actual
        ui_thread_instance.join(timeout=1)
    
    # Crear e iniciar un nuevo hilo
    ui_thread_instance = UIThread(current_screen, screen_params)
    ui_thread_instance.start()

# Clase para manejar el hilo de la UI
class UIThread(threading.Thread):
    def __init__(self, screen, params):
        super().__init__()
        self.screen = screen
        self.params = params
        self.daemon = True

    def run(self):
        ui_show(self.screen, self.params)

# Menú de opciones para probar la UI
def main():
    while True:
        print("1. Show waiting payments (status 0)")
        print("2. Show waiting payments (status 1)")
        print("3. Show waiting payments (status 2)")
        print("4. Show countdown")
        print("5. Show running")
        print("6. Show game over (player 1)")
        print("7. Show game over (player 2)")
        print("8. Exit")
        
        option = input("Enter option number: ")
        
        if option == "1":
            change_screen("waiting_payments", {"status": 0})
        elif option == "2":
            change_screen("waiting_payments", {"status": 1})
        elif option == "3":
            change_screen("waiting_payments", {"status": 2})
        elif option == "4":
            change_screen("countdown", {})
        elif option == "5":
            laps_player1 = int(input("Enter number of laps for player 1: "))
            fuel_player1 = int(input("Enter fuel percentage for player 1: "))
            laps_player2 = int(input("Enter number of laps for player 2: "))
            fuel_player2 = int(input("Enter fuel percentage for player 2: "))
            change_screen("running", {"laps_player1": laps_player1, "fuel_player1": fuel_player1, "laps_player2": laps_player2, "fuel_player2": fuel_player2})
        elif option == "6":
            change_screen("gameover", {"player": 1})
        elif option == "7":
            change_screen("gameover", {"player": 2})
        elif option == "8":
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
