from tkinter import *
from tkinter.ttk import Progressbar
import time
import pygame
#import mido
"""
Need to have:
python3 -m pip install pygame==2.0.0
conda install -c roebel mido
From anaconda: tk, keras, tensorflow

"""
# Initialise program
root = Tk()
pygame.mixer.init()

# set window color and size and name
bgColor = "white"  # "#f8f4ec"
root.title("NES MIDI Maker")
root.geometry("1080x720")
root.configure(bg=bgColor)
textSize = 25
# frame for play/ stop
frame_c = Frame()
# frame for download
frame_d = Frame()
# frame for Dummy
frame_z = Frame()


# Loading Bar function to run
def start():
    task = 10
    x = 0
    bar = Progressbar(master=frame_d, orient=HORIZONTAL, length=300)
    bar.grid(row=3, column=1)

    while (x < task):
        time.sleep(1)
        bar['value'] += 10
        x += 1
        frame_c.update_idletasks()


# show title at top of page
def showTitle():
    Prompt = Label(root, text="Select keyword for below\nEach will provide a MIDI and mp3 file ", height=5,
                   background=bgColor, foreground="purple", font=("Arial", 30))
    Prompt.pack()


# show all buttons for options
def UserButtons():
    # button for selection
    frame_a = Frame()
    button = Button(master=frame_a, text="Boss Fight", background="white", fg="purple", font=("Arial", textSize),
                    command=lambda: [dummyValue(), showOptions()])
    button.grid(row=1, column=0)

    button1 = Button(master=frame_a, text="Spooky", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions()])
    button1.grid(row=1, column=1)

    button2 = Button(master=frame_a, text="Adventurous", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions()])
    button2.grid(row=1, column=2)

    button3 = Button(master=frame_a, text="Upbeat Overworld", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions()])
    button3.grid(row=1, column=3)

    button2 = Button(master=frame_a, text="Ominous", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions()])
    button2.grid(row=1, column=4)

    button3 = Button(master=frame_a, text="Calm Overworld", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions()])
    button3.grid(row=1, column=5)
    frame_a.pack()


# to show option to play sound
def playSound():
    def stopPlay():
        pygame.mixer.music.stop()

    def play():
        pygame.mixer.music.load("Test.mp3")
        pygame.mixer.music.play(loops=0)

    emptyText = Label(master=frame_c, text=" \n \n \n", background=bgColor)
    emptyText.grid(row=0, column=0)

    play_button = Button(master=frame_c, text="Play Song", background=bgColor, foreground="purple",
                         font=("Arial", textSize), command=play)
    play_button.grid(row=1, column=0)

    stop_button = Button(master=frame_c, text="Stop Song", background=bgColor, foreground="purple",
                         font=("Arial", textSize), command=stopPlay)
    stop_button.grid(row=1, column=1)
    frame_c.pack()


# download option
def downloadMIDI():
    emptyText = Label(master=frame_d, text=" \n \n \n", background=bgColor)
    emptyText.grid(row=1, column=1)

    Button2 = Button(master=frame_d, text="Download MIDI", background=bgColor, foreground="purple", command=start)
    Button2.grid(row=2, column=1)

    frame_d.pack()
    # end MIDI download


# function holder for machine learning
def dummyValue():
    emptyText = Label(master=frame_z, text=" \n test \n", background=bgColor)
    emptyText.grid(row=1, column=1)
    frame_z.pack()


# after button press to show song and download
def showOptions():
    playSound()
    downloadMIDI()


def main():
    showTitle()
    UserButtons()
    root.mainloop()


if __name__ == "__main__":
    main()
