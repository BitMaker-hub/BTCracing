import sys
import termios
import tty
from leds import LEDStripController, strip

def get_key():
    """Lee una tecla presionada en la terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == "__main__":
    controller = LEDStripController(strip)
    try:
        print("Press 1-6 to test different LED functions:")
        print("1: Rainbow effect")
        print("2: Flashing LEDs effect")
        print("3: Countdown effect")
        print("4: Set LED 1 green")
        print("5: Clear LEDs")
        print("6: Exit")
        while True:
            key = get_key()
            if key == '1':
                print("Running rainbow effect")
                controller.set_effect(controller.rainbow)
            elif key == '2':
                print("Running flashing LEDs effect")
                controller.set_effect(controller.flashing_leds)
            elif key == '3':
                print("Running countdown effect")
                controller.set_effect(controller.countdown)
            elif key == '4':
                print("Setting LED 1 to green")
                controller.set_effect(lambda: controller.set_led_green(0))
            elif key == '5':
                print("Clearing LEDs")
                controller.set_effect(controller.clear_leds)
            elif key == '6':
                print("Exiting...")
                controller.stop()
                break
            else:
                print("Invalid key. Press 1-6 to test different LED functions.")
    except KeyboardInterrupt:
        controller.stop()
