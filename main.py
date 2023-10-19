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
    "monkey": "#8B4513",
    "dock_color": "#8B4513"
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
    def __init__(self, canvas, island, x, y, size):
        self.island = island
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
        self.is_swimming = False

    def stop_death_thread(self):
        self.death_sound_flag.set()
        self.is_dead = True

    def death_sound_timer(self):
        while not self.death_sound_flag.is_set():
            if self.death_type == "sea":
                playsound("sounds/shark_drowned_monkey.wav")
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

        if not self.is_swimming:
            new_x = self.x + dx * self.size
            new_y = self.y + dy * self.size

            island_x1, island_y1, island_x2, island_y2 = self.get_island_boundary()

            new_x = max(island_x1, min(new_x, island_x2 - self.size))
            new_y = max(island_y1, min(new_y, island_y2 - self.size))

            self.canvas.move(self.shape, new_x - self.x, new_y - self.y)
            self.x, self.y = new_x, new_y

        self.canvas.after(self.wander_interval, self.wander)

    def get_island_boundary(self):
        island_x1 = self.island.x
        island_y1 = self.island.y
        island_x2 = island_x1 + self.island.width
        island_y2 = island_y1 + self.island.height
        return island_x1, island_y1, island_x2, island_y2


class Island:
    def __init__(self, canvas):
        self.label_name = f"S{len(islands) + 1}"
        self.label_id = None
        self.width = random.randint(50, 80)
        self.height = random.randint(50, 80)
        self.x = random.randint(0, window_width - self.width)
        self.y = random.randint(0, window_height - self.height)
        self.label_x = self.x + self.width // 2
        self.label_y = self.y + self.height // 2
        self.color = colormap["grass_green"]
        self.canvas = canvas
        self.sound_thread = threading.Thread(target=self.sound_timer)
        self.flag = threading.Event()
        self.monkey_label_amount = None
        self.monkeys = []
        self.is_aware = False


    def draw_docks(self):
        if self.is_aware:
            dock_size = 15
            # top, left, right, bottom
            self.canvas.create_rectangle(self.x + dock_size, self.y - dock_size, self.x + dock_size*2, self.y,
                                         fill=colormap["dock_color"])
            self.canvas.create_rectangle(self.x - dock_size, self.y + dock_size, self.x, self.y + dock_size*2,
                                         fill=colormap["dock_color"])
            self.canvas.create_rectangle(self.x + self.width, self.y + dock_size,
                                         self.x + self.width + dock_size, self.y + dock_size*2,
                                         fill=colormap["dock_color"])

            self.canvas.create_rectangle(self.x + dock_size*2, self.y + self.height, self.x + dock_size*3,
                                         self.y + self.height + dock_size, fill=colormap["dock_color"])

    def draw(self):
        self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.color)
        self.label_id = self.canvas.create_text(
            self.label_x, self.label_y,
            text=self.label_name,
            fill="black",
            font=("Arial", 12)
        )
        self.generate_monkeys()
        self.sound_thread.start()
        self.update_monkey_label()
        if self.is_aware:
            self.draw_docks()

    def stop_thread(self):
        self.flag.set()

    def update_monkey_label(self):
        if self.monkey_label_amount:
            self.canvas.delete(self.monkey_label_amount)

        monkey_count = len(self.monkeys)
        self.monkey_label_amount = self.canvas.create_text(
            self.label_x, self.label_y + 20,
            text=f"{monkey_count}",
            fill="black",
            font=("Arial", 12)
        )

    def sound_timer(self):
        while not self.flag.is_set():
            time.sleep(10)
            playsound("sounds/monkey_noise.wav")

    def generate_monkeys(self):
        for _ in range(10):
            small_square_width = random.randint(2, 2)
            small_square_x = random.randint(self.x, self.x + self.width - small_square_width)
            small_square_y = random.randint(self.y, self.y + self.height - small_square_width)
            monkey = Monkey(self.canvas, self, small_square_x, small_square_y, small_square_width)
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
        island.update_monkey_label()
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
                   # i_suppose_i_have_earned_so_much_points(2)

    canvas.after(1000, check_monkey_position)


def create_island():
    if len(islands) < 10:
        new_island = Island(canvas)
        if len(islands) == 0:
            new_island.is_aware = True
        while check_collision(islands, new_island):
            new_island = Island(canvas)

        new_island.draw()
        islands.append(new_island)


def clear_islands():
    canvas.delete("all")
    for island in islands:
        island.stop_thread()
    islands.clear()
    # i_suppose_i_have_earned_so_much_points(1)


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
