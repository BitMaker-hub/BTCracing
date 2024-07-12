import time
from rpi_ws281x import PixelStrip, Color
import threading

# Configuración de los LED
LED_COUNT = 4        # Número de LED en la tira
LED_PIN = 18         # GPIO pin conectado a la tira de LED (Debe ser 18 o 10 para hardware PWM)
LED_FREQ_HZ = 800000  # Frecuencia de señal LED (Generalmente 800kHz)
LED_DMA = 10          # DMA channel para generar la señal (Cualquiera entre 0 y 14)
LED_BRIGHTNESS = 255  # Brillo de la tira de LED (0-255)
LED_INVERT = False    # Invertir la señal de la tira de LED
LED_CHANNEL = 0       # Canal de la tira de LED

# Inicializar la tira de LED
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

class LEDStripController:
    def __init__(self, strip):
        self.strip = strip
        self.current_effect = self.clear_leds
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def set_effect(self, effect):
        with self.lock:
            self.current_effect = effect

    def run(self):
        while self.running:
            with self.lock:
                effect = self.current_effect
            effect()

    def stop(self):
        self.running = False
        self.thread.join()

    def clear_leds(self, wait_ms=20):
        """Apaga todos los LEDs."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        time.sleep(wait_ms / 1000.0)

    def rainbow(self, wait_ms=20):
        """Muestra un arco iris de colores."""
        for j in range(256):
            if self.current_effect != self.rainbow:
                return
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def flashing_leds(self, wait_ms=500):
        """Parpadea el primer y último LED en color naranja."""
        while self.current_effect == self.flashing_leds:
            self.strip.setPixelColor(0, Color(255, 165, 0))  # Naranja
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(255, 165, 0))  # Naranja
            self.strip.setPixelColor(1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(2, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            self.strip.setPixelColor(0, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def set_led_green(self, position, wait_ms=20):
        """Establece un LED en color verde."""
        self.strip.setPixelColor(position, Color(0, 255, 0))  # Verde
        self.strip.show()
        time.sleep(wait_ms / 1000.0)

    def countdown(self, wait_ms=1000):
        """Cuenta regresiva de 5 segundos."""
        self.clear_leds()
        colors = [Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 255, 0), Color(0, 0, 0), Color(255, 0, 0)]
        for i in range(4):
            if self.current_effect != self.countdown:
                return
            self.strip.setPixelColor(i, colors[i])
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
        for i in range(4):
            self.strip.setPixelColor(i, colors[4])
        self.strip.show()
        time.sleep(wait_ms / 1000.0)
        for i in range(4):
            self.strip.setPixelColor(i, colors[5])
        self.strip.show()
        # Mantener los LEDs en verde
        while self.current_effect == self.countdown:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(255, 0, 0))  # Verde
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def player1_paid(self, wait_ms=500):
        """Parpadea el primer LED en amarillo y mantiene el último en rojo."""
        while self.current_effect == self.player1_paid:
            self.strip.setPixelColor(0, Color(255, 255, 0))  # Amarillo
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(255, 0, 0))  # Rojo fijo
            self.strip.setPixelColor(1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(2, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            self.strip.setPixelColor(0, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def player2_paid(self, wait_ms=500):
        """Parpadea el último LED en amarillo y mantiene el primero en rojo."""
        while self.current_effect == self.player2_paid:
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(255, 255, 0))  # Amarillo
            self.strip.setPixelColor(0, Color(255, 0, 0))  # Rojo fijo
            self.strip.setPixelColor(1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(2, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def player1_win(self, wait_ms=500):
        """Parpadea el último LED en rojo."""
        while self.current_effect == self.player1_win:
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(255, 0, 0))  # Rojo
            self.strip.setPixelColor(0, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(2, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def player2_win(self, wait_ms=500):
        """Parpadea el primer LED en rojo."""
        while self.current_effect == self.player2_win:
            self.strip.setPixelColor(0, Color(255, 0, 0))  # Rojo
            self.strip.setPixelColor(self.strip.numPixels() - 1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(1, Color(0, 0, 0))  # Apagado
            self.strip.setPixelColor(2, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            self.strip.setPixelColor(0, Color(0, 0, 0))  # Apagado
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def wheel(self, pos):
        """Genera colores arco iris en la posición dada."""
        if pos < 85:
            return Color(pos * 3, 0, 255 - pos * 3)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

# Ejemplo de uso
if __name__ == "__main__":
    controller = LEDStripController(strip)
    try:
        while True:
            cmd = input("Enter effect (rainbow, flashing, countdown, green, clear, player1_paid, player2_paid, player1_win, player2_win, exit): ").strip()
            if cmd == "rainbow":
                controller.set_effect(controller.rainbow)
            elif cmd == "flashing":
                controller.set_effect(controller.flashing_leds)
            elif cmd == "countdown":
                controller.set_effect(controller.countdown)
            elif cmd == "green":
                controller.set_effect(lambda: controller.set_led_green(0))
            elif cmd == "clear":
                controller.set_effect(controller.clear_leds)
            elif cmd == "player1_paid":
                controller.set_effect(controller.player1_paid)
            elif cmd == "player2_paid":
                controller.set_effect(controller.player2_paid)
            elif cmd == "player1_win":
                controller.set_effect(controller.player1_win)
            elif cmd == "player2_win":
                controller.set_effect(controller.player2_win)
            elif cmd == "exit":
                controller.stop()
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        controller.stop()
