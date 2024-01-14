import os
import tkinter as tk
import pygame
import pickle

root = tk.Tk()
root.geometry("400x400")

icon = tk.PhotoImage(file="imgs/icon_png.png")
root.iconphoto(True, icon)
root.title("Fuzzy Racer")

# Load the background image
bg_image = tk.PhotoImage(file="imgs/road.png")

# Create a canvas to put the background image on
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_image, anchor="nw")

# Functions 
def play():
    import fuzzyracergame as fr 
    fr.main()
    root.destroy()
def neural_engine():
    import fuzzyracerpickled as frp
    with open('neural_engine.pkl', 'rb') as p:
        net = pickle.load(p)
    frp.main(net)
def train():    
    import fuzzyracerneuraltraining as frt
    config_file = os.path.join(os.path.dirname(__file__), 'config.txt') 
    frt.run(config_file)

# Create buttons directly inside the canvas
button1 = tk.Button(canvas, text="PLAY", bg="orange",activebackground = 'yellow', fg="white",width = 30, height = 3, font=("Arial", 12), command = play)
button1.place(relx=0.5, rely=0.3, anchor="center")

button2 = tk.Button(canvas, text="LET NEURAL ENGINE PLAY", bg="orange",activebackground = 'yellow', fg="white",width = 30, height = 3, font=("Arial", 12), command = neural_engine)
button2.place(relx=0.5, rely=0.5, anchor="center")

button3 = tk.Button(canvas, text="TRAIN THE MODEL", bg="orange",activebackground = 'yellow', fg="white",width = 30, height = 3, font=("Arial", 12), command = train)
button3.place(relx=0.5, rely=0.7, anchor="center")

root.mainloop()
