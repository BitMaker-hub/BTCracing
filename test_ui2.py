import threading
import queue
import time
from ui import ui_show, UI

# Crear una cola para los comandos de la UI
command_queue = queue.Queue()

# Clase para manejar el hilo de la UI
class UIThread(threading.Thread):
    def __init__(self, command_queue):
        super().__init__()
        self.command_queue = command_queue
        self.daemon = True

    def run(self):
        ui_show(self.command_queue)

# Función para cambiar la pantalla
def change_screen(screen):
    command_queue.put(screen)

# Menú de opciones para probar la UI
def main():
    ui_thread_instance = UIThread(command_queue)
    ui_thread_instance.start()

    change_screen("waiting_payments")
    time.sleep(4)
    change_screen("countdown")
    time.sleep(4)

if __name__ == "__main__":
    main()
