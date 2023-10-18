import random
import tkinter as tk
# import winsound
import time
import matplotlib.pyplot as plt
from playsound import playsound
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
import threading

colormap = {
    "ocean_blue": "#0077B6",
    "grass_green": "#4CAF50",
    "monkey": "#8B4513"
}

ikkuna = tk.Tk()
ikkuna.title("Exercise 8")
window_width, window_height = 700, 700
ikkuna.geometry(f"{window_width}x{window_height}")

canvas = tk.Canvas(ikkuna, width=window_width, height=window_height, bg=colormap["ocean_blue"])
canvas.grid(row=1, column=0, columnspan=6)
point_button = []
islands = []


class Monkey:
    def __init__(self, canvas, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.canvas = canvas
        self.wander_interval= 1000

    def draw(self):
        self.shape = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.size, self.y + self.size, fill=colormap["monkey"]
        )
        self.wander()

    def wander(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right, Left, Down, Up
        dx, dy = random.choice(directions)
        new_x = self.x + dx * self.size
        new_y = self.y + dy * self.size

        if 0 <= new_x < window_width - self.size and 0 <= new_y < window_height - self.size:
            self.canvas.move(self.shape, dx * self.size, dy * self.size)

        # Schedule the next wandering step
        self.canvas.after(self.wander_interval, self.wander)


class Island:
    def __init__(self, canvas):
        self.width = random.randint(50, 80)
        self.height = random.randint(50, 80)
        self.x = random.randint(0, window_width - self.width)
        self.y = random.randint(0, window_height - self.height)
        self.color = colormap["grass_green"]
        self.canvas = canvas
        self.sound_thread = threading.Thread(target=self.sound_timer)
        self.flag = threading.Event()

    def draw(self):
        self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)
        self.generate_monkeys()
        # self.sound_thread.start()

    def stop_thread(self):
        self.flag.set()

    def sound_timer(self):
        while not self.flag.is_set():
            time.sleep(10)
            playsound("sounds/monkey_noise.wav")

    def generate_monkeys(self):
        monkeys = []
        for _ in range(10):
            small_square_width = random.randint(2, 2)
            small_square_x = random.randint(self.x, self.x + self.width - small_square_width)
            small_square_y = random.randint(self.y, self.y + self.height - small_square_width)
            monkey = Monkey(self.canvas, small_square_x, small_square_y, small_square_width)
            monkey.draw()
            monkeys.append(monkey)
        return monkeys


def i_suppose_i_have_earned_so_much_points(amount_of_points):
    for i in range(5):
        point_button[i].configure(bg='gray')
    time.sleep(1)
    for i in range(amount_of_points):
        point_button[i].configure(bg='green')
        playsound("sounds/point_earned.wav")


def check_collision(islands, new_island):
    for island in islands:
        if (
            new_island.x < island.x + island.width and
            new_island.x + new_island.width > island.x and
            new_island.y < island.y + island.height and
            new_island.y + new_island.height > island.y
        ):
            return True
    return False


def create_island():
    if len(islands) < 10:
        new_island = Island(canvas)
        while check_collision(islands, new_island):
            new_island = Island(canvas)

        new_island.draw()
        islands.append(new_island)


def clear_islands():
    canvas.delete("all")
    for island in islands:
        island.stop_thread()
    islands.clear()


for i in range(5):
    button_temp = tk.Button(ikkuna, text="Points: " + str(i + 1), padx=40)
    button_temp.grid(row=0, column=i + 1)
    point_button.append(button_temp)


button_new_island = tk.Button(ikkuna, text="New Island", command=lambda: create_island())
button_new_island.grid(row=2, column=1)
clear_button = tk.Button(ikkuna, text="Clear Islands", command=lambda: clear_islands())
clear_button.grid(row=2, column=2)

ikkuna.grid_rowconfigure(1, weight=1)
ikkuna.grid_columnconfigure(0, weight=1)
ikkuna.mainloop()
