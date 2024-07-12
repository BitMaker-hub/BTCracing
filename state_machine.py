import threading
import queue
import asyncio
import time
import RPi.GPIO as GPIO
from wallet_listener import main as wallet_listener_main
import gpio_interface as LapCounter
from leds import LEDStripController, strip
from ui import ui_show, UI
import keyboard  # Importar la biblioteca keyboard

#RACE PARAMETERS
FUEL_TIME = 30 # Number of seconds you have fuel
MAX_LAPS = 10

# Deshabilitar advertencias de GPIO
GPIO.setwarnings(False)

# Definir los estados
STATE_WAITING_FOR_PAYMENTS = 0
STATE_GAME_READY = 1
STATE_COUNTDOWN = 2
STATE_GAME_RUNNING = 3
STATE_GAME_OVER = 4

# Pines GPIO
RELAY_PIN_PLAYER1 = 23  # GPIO pin for Player 1 relay
RELAY_PIN_PLAYER2 = 24  # GPIO pin for Player 2 relay

# Variables globales para la pantalla actual y los parámetros
current_screen = None
screen_params = {}
ui_thread_instance = None


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
def change_screen(screen, params=None):
    if params is None:
        params = {}
    command_queue.put((screen, params))

class StateMachine:
    def __init__(self):
        global ui_thread_instance

        self.state = STATE_WAITING_FOR_PAYMENTS
        self.player1_paid = False
        self.player2_paid = False
        self.countdown = 20
        self.relay_timer_player1 = FUEL_TIME  # Time in seconds
        self.relay_timer_player2 = FUEL_TIME  # Time in seconds
        self.lap_count_player1 = 0
        self.lap_count_player2 = 0
        self.time_elapsed_player1 = 0
        self.time_elapsed_player2 = 0
        self.last_time = time.time()
        self.running_task = None  # Para controlar la tarea de update_game_running

        # Configuración de GPIO
        GPIO.cleanup()  # Limpiar configuración anterior
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN_PLAYER1, GPIO.OUT)
        GPIO.setup(RELAY_PIN_PLAYER2, GPIO.OUT)

        # Inicializar contadores de vueltas y registrar callbacks
        LapCounter.initialize_lap_counters()
        LapCounter.set_lap_callback(1, self.lap_detected_player1)
        LapCounter.set_lap_callback(2, self.lap_detected_player2)

        # Inicializar controlador de LED
        self.led_controller = LEDStripController(strip)
        self.led_controller.set_effect(self.led_controller.flashing_leds)

        # Mostrar la primera pantalla
        ui_thread_instance = UIThread(command_queue)
        ui_thread_instance.start()
        change_screen("waiting_payments", {"status": 0})

        # Detección de teclas
        keyboard.on_press_key("1", lambda _: self.payment_received(1))
        keyboard.on_press_key("2", lambda _: self.payment_received(2))

    def payment_received(self, player):
        print(f"Payment received from player {player}")
        if self.state == STATE_GAME_RUNNING:
            if player == 1:
                self.relay_timer_player1 = FUEL_TIME  # Reset the relay timer for Player 1
                GPIO.output(RELAY_PIN_PLAYER1, GPIO.HIGH)  # Reactivar el relé del jugador 1
            elif player == 2:
                self.relay_timer_player2 = FUEL_TIME  # Reset the relay timer for Player 2
                GPIO.output(RELAY_PIN_PLAYER2, GPIO.HIGH)  # Reactivar el relé del jugador 2
        else:
            if player == 1:
                self.player1_paid = True
                self.led_controller.set_effect(self.led_controller.player1_paid)
                change_screen("waiting_payments", {"status": 1})
            elif player == 2:
                self.player2_paid = True
                self.led_controller.set_effect(self.led_controller.player2_paid)
                change_screen("waiting_payments", {"status": 2})
            self.check_payments()

    def check_payments(self):
        if self.player1_paid and self.player2_paid:
            asyncio.run_coroutine_threadsafe(self.change_state(STATE_GAME_READY), self.loop)

    async def change_state(self, new_state):
        print(f"Changing state to: {new_state}")
        self.state = new_state
        self.display_state()

        if self.state == STATE_GAME_READY:
            self.display_game_ready_screen()
            await self.change_state(STATE_COUNTDOWN)
        elif self.state == STATE_COUNTDOWN:
            await self.start_countdown()
        elif self.state == STATE_GAME_RUNNING:
            if self.running_task is not None:
                self.running_task.cancel()  # Cancelar la tarea anterior si existe
            self.start_game_running()
            self.running_task = asyncio.create_task(self.update_game_running())
        elif self.state == STATE_GAME_OVER:
            if self.running_task is not None:
                self.running_task.cancel()  # Cancelar la tarea de actualización del juego
            self.display_game_over_screen()

    def display_state(self):
        state_names = {
            STATE_WAITING_FOR_PAYMENTS: "Waiting for payments",
            STATE_GAME_READY: "Game ready",
            STATE_COUNTDOWN: "Countdown",
            STATE_GAME_RUNNING: "Game running",
            STATE_GAME_OVER: "Game over",
        }
        print(f"Current state: {state_names[self.state]}")

    def display_game_ready_screen(self):
        print("Both players have paid. Game is ready to start!")
        self.led_controller.set_effect(self.led_controller.rainbow)
        self.countdown = 20
        change_screen("countdown", {})


    async def start_countdown(self):
        while self.countdown > 0:
            print(f"Countdown: {self.countdown}")
            if self.countdown == 10:
                self.led_controller.set_effect(self.led_controller.clear_leds)
            elif self.countdown <= 5:
                self.led_controller.set_effect(self.led_controller.countdown)
            await asyncio.sleep(1)
            self.countdown -= 1
        await self.change_state(STATE_GAME_RUNNING)

    def start_game_running(self):
        print("Game is now running!")
        LapCounter.reset_lap_counters()
        GPIO.output(RELAY_PIN_PLAYER1, GPIO.HIGH)
        GPIO.output(RELAY_PIN_PLAYER2, GPIO.HIGH)
        self.last_time = time.time()
        # Preparar los parámetros para change_screen
        params = {
            "laps_player1": 0,
            "fuel_player1": 100,
            "laps_player2": 0,
            "fuel_player2": 100
        }
        change_screen("running", params)

    def display_game_over_screen(self):
        winner = "Player 1" if self.lap_count_player1 > self.lap_count_player2 else "Player 2"
        print(f"Game over! {winner} wins!")
        GPIO.output(RELAY_PIN_PLAYER1, GPIO.LOW)
        GPIO.output(RELAY_PIN_PLAYER2, GPIO.LOW)
        if self.lap_count_player1 > self.lap_count_player2:
            self.led_controller.set_effect(self.led_controller.player1_win)
            change_screen("gameover", {"player": 1})
        else:
            self.led_controller.set_effect(self.led_controller.player2_win)
            change_screen("gameover", {"player": 2})
        asyncio.create_task(self.reset_after_delay(15))

    async def reset_after_delay(self, delay):
        await asyncio.sleep(delay)
        await self.change_state(STATE_WAITING_FOR_PAYMENTS)
        self.relay_timer_player1 = FUEL_TIME
        self.relay_timer_player2 = FUEL_TIME
        self.time_elapsed_player1 = 0
        self.time_elapsed_player2 = 0
        self.lap_count_player1 = 0
        self.lap_count_player2 = 0
        self.player1_paid = False
        self.player2_paid = False
        change_screen("waiting_payments", {"status": 0})
        self.led_controller.set_effect(self.led_controller.flashing_leds)

    def lap_detected_player1(self, laps):
        if self.state == STATE_GAME_RUNNING:
            self.lap_count_player1 = laps
            print(f"Player 1 completed lap {self.lap_count_player1}")
            if self.lap_count_player1 >= MAX_LAPS:
                asyncio.run_coroutine_threadsafe(self.change_state(STATE_GAME_OVER), self.loop)

    def lap_detected_player2(self, laps):
        if self.state == STATE_GAME_RUNNING:
            self.lap_count_player2 = laps
            print(f"Player 2 completed lap {self.lap_count_player2}")
            if self.lap_count_player2 >= MAX_LAPS:
                asyncio.run_coroutine_threadsafe(self.change_state(STATE_GAME_OVER), self.loop)

    async def update_game_running(self):
        try:
            print("Entered update_game_running")
            while self.state == STATE_GAME_RUNNING:
                current_time = time.time()
                elapsed = current_time - self.last_time
                self.time_elapsed_player1 += elapsed * 1000
                self.time_elapsed_player2 += elapsed * 1000
                self.last_time = current_time

                self.relay_timer_player1 -= elapsed
                self.relay_timer_player2 -= elapsed

                if self.relay_timer_player1 <= 0:
                    GPIO.output(RELAY_PIN_PLAYER1, GPIO.LOW)  # Desactivar el relé del jugador 1
                    print("Player 1 is out of fuel!")

                if self.relay_timer_player2 <= 0:
                    GPIO.output(RELAY_PIN_PLAYER2, GPIO.LOW)  # Desactivar el relé del jugador 2
                    print("Player 2 is out of fuel!")

                print(f"Player 1 Time: {self.time_elapsed_player1} ms, Fuel: {self.relay_timer_player1} s")
                print(f"Player 2 Time: {self.time_elapsed_player2} ms, Fuel: {self.relay_timer_player2} s")

                # Calcular el porcentaje de combustible restante
                fuel_player1_percent = max(0, min(100, int((self.relay_timer_player1 / FUEL_TIME) * 100)))
                fuel_player2_percent = max(0, min(100, int((self.relay_timer_player2 / FUEL_TIME) * 100)))

                # Preparar los parámetros para change_screen
                params = {
                    "laps_player1": self.lap_count_player1,
                    "fuel_player1": fuel_player1_percent,
                    "laps_player2": self.lap_count_player2,
                    "fuel_player2": fuel_player2_percent
                }

                # Llamar a change_screen con los parámetros
                change_screen("running", params)

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("update_game_running was cancelled")
            return


    async def run(self):
        self.loop = asyncio.get_running_loop()
        await wallet_listener_main(self.payment_received)

if __name__ == "__main__":
    state_machine = StateMachine()
    asyncio.run(state_machine.run())
