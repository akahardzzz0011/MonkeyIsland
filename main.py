import tkinter as tk
# import winsound
import time
import matplotlib.pyplot as plt
from playsound import playsound
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
import threading


ikkuna = tk.Tk()
ikkuna.title("Exercise 8")
window_width, window_height = 700, 700
ikkuna.geometry(f"{window_width}x{window_height}")

point_button = []

for i in range(5):
    button_temp = tk.Button(ikkuna, text="Points: "+str(i+1), padx=40)
    button_temp.grid(row=0, column=i+1)
    point_button.append(button_temp)


def i_suppose_i_have_earned_so_much_points(amount_of_points):
    for i in range(5):
        point_button[i].configure(bg='gray')
    time.sleep(1)
    for i in range(amount_of_points):
        point_button[i].configure(bg='green')
        playsound("sounds/point_earned.wav")


# colors: sand, pool/digged ground, trench, monkey
colormap = ListedColormap(["#FFD699", "#FFB266", "#FFEDB3", "#674300", "#0077B6"])