from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import time
import asyncio
import queue

MAX_LAPS = 10

# Variables globales
current_screen = None
paymentStatus = None
isNewData = False
laps_player1 = 0
fuel_player1 = 100
laps_player2 = 0
fuel_player2 = 100

class UI:
    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.root = Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # Ocultar la barra de título
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.canvas = Canvas(self.root, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.pack()

        self.running_screen_initialized = False
        self.start_time = None
        self.running = False
        self.time_text_player1 = None
        self.lap_text_player1 = None
        self.fuel1_player1 = None

        self.time_text_player2 = None
        self.lap_text_player2 = None
        self.fuel1_player2 = None

        self.background_image = None
        self.background_photo = None

        self.update_screen()
        self.check_command_queue()

    def exit_fullscreen(self, event=None):
        self.canvas.delete("all")
        self.root.quit()
        self.root.destroy()

    def clear_screen(self):
        self.canvas.delete("all")

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def show_waiting_payments(self, status):
        global current_screen, paymentStatus

        paymentStatus = status
        if current_screen != "waiting_payments":
            self.clear_screen()
            self.background_image = Image.open("waiting_payments.png")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.canvas.create_image(0, 0, image=self.background_photo, anchor=NW)
            
            rect_color = "#B77B15"
            rect_width = 176
            rect_height = 50
            font_size = 30
            font_name = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"

            x1, y1 = 518, 162
            x2, y2 = 768, 162

            self.rect1 = self.create_rounded_rectangle(x1, y1, x1+rect_width, y1+rect_height, radius=10, fill=rect_color, outline="", width=2, tags="rect1")
            self.text1 = self.canvas.create_text(x1+rect_width//2, y1+rect_height//2, text="PAY", fill="white", font=(font_name, font_size), tags="text1")
            self.rect2 = self.create_rounded_rectangle(x2, y2, x2+rect_width, y2+rect_height, radius=10, fill=rect_color, outline="", width=2, tags="rect2")
            self.text2 = self.canvas.create_text(x2+rect_width//2, y2+rect_height//2, text="PAY", fill="white", font=(font_name, font_size), tags="text2")

            self.root.after(1000, self.blink_rectangles)

        if paymentStatus == 1:
            self.canvas.itemconfig(self.rect1, fill="green")
            self.canvas.itemconfig(self.text1, text="READY")
        elif paymentStatus == 2:
            self.canvas.itemconfig(self.rect2, fill="green")
            self.canvas.itemconfig(self.text2, text="READY")

        current_screen = "waiting_payments" 
        #self.root.mainloop()

    def blink_rectangles(self):
        global paymentStatus

        if paymentStatus == 0:
            if self.canvas.itemcget(self.rect1, "fill") == "#B77B15":
                self.canvas.itemconfig("rect1", fill="#F5F5F5")
                self.canvas.itemconfig("text1", fill="#F5F5F5")
                self.canvas.itemconfig("rect2", fill="#F5F5F5")
                self.canvas.itemconfig("text2", fill="#F5F5F5")
            else:
                self.canvas.itemconfig("rect1", fill="#B77B15")
                self.canvas.itemconfig("text1", fill="white")
                self.canvas.itemconfig("rect2", fill="#B77B15")
                self.canvas.itemconfig("text2", fill="white")
        elif paymentStatus == 1:
            if self.canvas.itemcget(self.rect2, "fill") == "#B77B15":
                self.canvas.itemconfig("rect2", fill="#F5F5F5")
                self.canvas.itemconfig("text2", fill="#F5F5F5")
            else:
                self.canvas.itemconfig("rect2", fill="#B77B15")
                self.canvas.itemconfig("text2", fill="white")
        elif paymentStatus == 2:
            if self.canvas.itemcget(self.rect1, "fill") == "#B77B15":
                self.canvas.itemconfig("rect1", fill="#F5F5F5")
                self.canvas.itemconfig("text1", fill="#F5F5F5")
            else:
                self.canvas.itemconfig("rect1", fill="#B77B15")
                self.canvas.itemconfig("text1", fill="white")

        if current_screen == "waiting_payments":  # Verificar la bandera antes de actualizar 
            self.root.after(1000, self.blink_rectangles)

    def show_countdown(self):
        global paymentStatus

        paymentStatus=0
        self.clear_screen()
        self.background_image = Image.open("ui_countdown.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor=NW)
        
        font_size = 122
        font_name = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
        
        countdown_text = self.canvas.create_text(750 + 80, 366 + 70, text="19", fill="white", font=(font_name, font_size))
        
        for i in range(19, -1, -1):
            self.canvas.itemconfig(countdown_text, text=str(i))
            self.root.update()
            time.sleep(1)


    def show_running(self):
        global current_screen, laps_player1, fuel_player1, laps_player2, fuel_player2, isNewData
    
        if current_screen != "running":
            self.clear_screen()
            print(f"Initialize UI running")  # Debug print statement
            self.background_image = Image.open("ui_running.png")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.canvas.create_image(0, 0, image=self.background_photo, anchor=NW)

            font_size = 40
            font_name = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"

            # Player 1 UI elements
            self.time_text_player1 = self.canvas.create_text(320, 224, text="00:00:00", fill="white", font=(font_name, font_size))
            self.lap_text_player1 = self.canvas.create_text(280, 340, text=f"{laps_player1} / {MAX_LAPS}", fill="white", font=(font_name, font_size))
            self.fuel1_player1 = self.canvas.create_rectangle(210, 429, 402, 463, fill="green", outline="", width=2)

            # Player 2 UI elements
            self.time_text_player2 = self.canvas.create_text(870, 224, text="00:00:00", fill="white", font=(font_name, font_size))
            self.lap_text_player2 = self.canvas.create_text(830, 340, text=f"{laps_player2} / {MAX_LAPS}", fill="white", font=(font_name, font_size))
            self.fuel1_player2 = self.canvas.create_rectangle(760, 429, 952, 463, fill="green", outline="", width=2)

            self.start_time = time.time()
            self.running_screen_initialized = True

            current_screen = "running"
            self.update_running()
            self.update_time()


    def update_running(self):
        global laps_player1, fuel_player1, laps_player2, fuel_player2, isNewData
            
        if isNewData == True:
            isNewData = False
            if laps_player1 is not None:
                #print(f"Updating Player 1 laps: {laps_player1}")
                self.canvas.itemconfig(self.lap_text_player1, text=f"{laps_player1} / 10")
            
            if fuel_player1 is not None:
                try:
                    fuel_player1 = int(fuel_player1)
                    #print(f"Updating Player 1 fuel: {fuel_player1}")
                    if fuel_player1 > 50:
                        color = "green"
                    elif fuel_player1 > 30:
                        color = "yellow"
                    else:
                        color = "red"
                    width = 192 * (fuel_player1 / 100)
                    self.canvas.coords(self.fuel1_player1, 210, 429, 210 + width, 463)
                    self.canvas.itemconfig(self.fuel1_player1, fill=color)
                except ValueError:
                    print(f"Invalid value for fuel_player1: {fuel_player1}")
            
            if laps_player2 is not None:
                #print(f"Updating Player 2 laps: {laps_player2}")
                self.canvas.itemconfig(self.lap_text_player2, text=f"{laps_player2} / 10")
            
            if fuel_player2 is not None:
                try:
                    fuel_player2 = int(fuel_player2)
                    #print(f"Updating Player 2 fuel: {fuel_player2}")
                    if fuel_player2 > 50:
                        color = "green"
                    elif fuel_player2 > 30:
                        color = "yellow"
                    else:
                        color = "red"
                    width = 192 * (fuel_player2 / 100)
                    self.canvas.coords(self.fuel1_player2, 760, 429, 760 + width, 463)
                    self.canvas.itemconfig(self.fuel1_player2, fill=color)
                except ValueError:
                    print(f"Invalid value for fuel_player2: {fuel_player2}")

    def update_time(self):
        global current_screen, laps_player1, fuel_player1, laps_player2, fuel_player2, isNewData

        if current_screen == "running":  # Verificar la bandera antes de actualizar
            elapsed_time = int((time.time() - self.start_time) * 100)
            minutes = (elapsed_time // 6000) % 60
            seconds = (elapsed_time // 100) % 60
            milliseconds = elapsed_time % 100
            time_str = f"{minutes:02}:{seconds:02}:{milliseconds:02}"

            self.canvas.itemconfig(self.time_text_player1, text=time_str)
            self.canvas.itemconfig(self.time_text_player2, text=time_str)

            # Update fuel and laps from global variables
            self.update_running()

            self.root.after(10, self.update_time)

    def show_gameover(self, Player=None):
        self.clear_screen()
        self.background_image = Image.open("ui_gameover.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor=NW)
        
        font_size = 80
        font_name = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
        
        self.winner = self.canvas.create_text(650, 265, text=f"PLAYER {Player}", fill="white", font=(font_name, font_size))

        #self.root.mainloop()

    def check_command_queue(self):
        try:
            command = self.command_queue.get_nowait()
            screen, params = command
            self.update_screen(screen, params)
        except queue.Empty:
            pass
        self.root.after(100, self.check_command_queue)

    def update_screen(self, screen=None, params=None):
        global current_screen, laps_player1, fuel_player1, laps_player2, fuel_player2, isNewData

        if screen == "waiting_payments":
            status = params.get("status", 0)
            self.show_waiting_payments(status)
        elif screen == "countdown":
            current_screen = screen
            self.show_countdown()
        elif screen == "running":
            isNewData = True
            laps_player1 = params.get("laps_player1", 0)
            fuel_player1 = params.get("fuel_player1", 100)
            laps_player2 = params.get("laps_player2", 0)
            fuel_player2 = params.get("fuel_player2", 100)
            self.show_running()
        elif screen == "gameover":
            player = params.get("player", None)
            self.show_gameover(player)
        elif screen == "clear_screen":
            self.clear_screen()


def ui_show(command_queue):
    app = UI(command_queue)
    app.root.mainloop()
    return app


if __name__ == "__main__":
    ui_show("waiting_payments", {"status": 0})