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
        self.wander_interval = 1000
        self.shape = 0
        self.island_death_timer_counter = 0
        self.death_sound_flag = threading.Event()
        self.death_sound_thread = threading.Thread(target=self.death_sound_timer)
        self.death_type = ""
        self.is_dead = False

    def stop_death_thread(self):
        self.death_sound_flag.set()
        self.is_dead = True

    def death_sound_timer(self):
        while not self.death_sound_flag.is_set():
            if self.death_type == "sea":
                playsound("sounds/water_splash.wav")
                time.sleep(5)
                self.stop_death_thread()
            if self.death_type == "land":
                playsound("sounds/monkey_laugh.wav")
                time.sleep(5)
                self.stop_death_thread()


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
        self.monkeys = []

    def draw(self):
        self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)
        self.generate_monkeys()
        self.sound_thread.start()

    def stop_thread(self):
        self.flag.set()

    def sound_timer(self):
        while not self.flag.is_set():
            time.sleep(10)
            playsound("sounds/monkey_noise.wav")

    def generate_monkeys(self):
        for _ in range(10):
            small_square_width = random.randint(2, 2)
            small_square_x = random.randint(self.x, self.x + self.width - small_square_width)
            small_square_y = random.randint(self.y, self.y + self.height - small_square_width)
            monkey = Monkey(self.canvas, small_square_x, small_square_y, small_square_width)
            monkey.draw()
            self.monkeys.append(monkey)
        return self.monkeys

    def is_monkey_in_island(self, monkey):
        monkey_x1, monkey_y1, monkey_x2, monkey_y2 = self.canvas.coords(monkey.shape)
        island_x1, island_y1, island_x2, island_y2 = self.x, self.y, self.x + self.width, self.y + self.height

        if (
            monkey_x1 >= island_x1 and
            monkey_x2 <= island_x2 and
            monkey_y1 >= island_y1 and
            monkey_y2 <= island_y2
        ):
            return True
        else:
            return False


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


def one_percent_probability():
    random_number = random.random()
    if random_number <= 0.01:
        return True
    else:
        return False


def check_monkey_position():
    for island in islands:
        island.monkeys = [monkey for monkey in island.monkeys if not monkey.is_dead]

        for monkey in island.monkeys:
            if island.is_monkey_in_island(monkey):
                monkey.island_death_timer_counter += 1
                if monkey.island_death_timer_counter == 10:
                    if one_percent_probability():
                        monkey.death_type = "land"
                        monkey.death_sound_thread.start()
                        monkey.stop_death_thread()
                        canvas.delete(monkey.shape)
                    monkey.island_death_timer_counter = 0
            else:
                if one_percent_probability():
                    monkey.death_type = "sea"
                    monkey.death_sound_thread.start()
                    monkey.stop_death_thread()
                    canvas.delete(monkey.shape)
    canvas.after(1000, check_monkey_position)


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

check_monkey_position()
ikkuna.grid_rowconfigure(1, weight=1)
ikkuna.grid_columnconfigure(0, weight=1)
ikkuna.mainloop()
