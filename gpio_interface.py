from gpiozero import Button
import time

# Pines GPIO para las entradas
LAP_PIN_PLAYER1 = 27
LAP_PIN_PLAYER2 = 22

# Configuración de GPIO usando gpiozero con resistencias "pull-down"
button_player1 = Button(LAP_PIN_PLAYER1, pull_up=False)
button_player2 = Button(LAP_PIN_PLAYER2, pull_up=False)

# Contadores de vueltas
laps_player1 = 0
laps_player2 = 0

# Tiempo de la última vuelta
last_lap_time_player1 = 0
last_lap_time_player2 = 0

# Filtro antirebotes (en segundos)
debounce_time = 3

# Callbacks de vueltas
lap_callback_player1 = None
lap_callback_player2 = None

def input_callback_player1():
    global laps_player1, last_lap_time_player1
    current_time = time.time()
    if current_time - last_lap_time_player1 >= debounce_time:
        laps_player1 += 1
        last_lap_time_player1 = current_time
        print(f"Player 1 lap detected. Total laps: {laps_player1}")
        if lap_callback_player1:
            lap_callback_player1(laps_player1)

def input_callback_player2():
    global laps_player2, last_lap_time_player2
    current_time = time.time()
    if current_time - last_lap_time_player2 >= debounce_time:
        laps_player2 += 1
        last_lap_time_player2 = current_time
        print(f"Player 2 lap detected. Total laps: {laps_player2}")
        if lap_callback_player2:
            lap_callback_player2(laps_player2)

def reset_lap_counters():
    global laps_player1, laps_player2, last_lap_time_player1, last_lap_time_player2
    laps_player1 = 0
    laps_player2 = 0
    last_lap_time_player1 = 0
    last_lap_time_player2 = 0
    print("Lap counters reset.")

def set_lap_callback(player, callback):
    global lap_callback_player1, lap_callback_player2
    if player == 1:
        lap_callback_player1 = callback
    elif player == 2:
        lap_callback_player2 = callback

def initialize_lap_counters():
    button_player1.when_pressed = input_callback_player1
    button_player2.when_pressed = input_callback_player2

if __name__ == "__main__":
    initialize_lap_counters()
    print("Waiting for input...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
