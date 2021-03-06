"""
Need to have:
python3 -m pip install pygame==2.0.0
conda install -c roebel mido
From anaconda: tk, keras, tensorflow

"""
from tkinter import *
from tkinter.ttk import Progressbar
# from tkinter import tkFileDialog
import time
# import pygame
from PIL import ImageTk, Image
# import mido
from loading_script import get_song_seed, generate_song
from dataCleanup import Song
import numpy as np
import pandas as pd

'''
@ Skyler Voege
Python 3.6 conda

This is th GUI that will interact with the Machine learning and model to make various songs for NES style games.
This will go through selection, a test listen and downloading of a file (MIDI)
'''

# download option
def downloadMIDI():
    def start():
        task = 10
        x = 0
        bar = Progressbar(master=frame_d, orient=HORIZONTAL, length=300)
        bar.grid(row=3, column=1)
        # Download File............
        # name = asksaveasfile(mode='w', defaultextension=".mp3")
        # text2save = "Test"

        while (x < task):
            time.sleep(1)
            bar['value'] += 10
            x += 1
            frame_c.update_idletasks()

    emptyText = Label(master=frame_d, text=" \n \n \n", background=bgColor)
    emptyText.grid(row=1, column=1)

    Button2 = Button(master=frame_d, text="Download MIDI", background=bgColor, foreground="purple", command=start)
    Button2.grid(row=2, column=1)

    frame_d.pack()
    # end MIDI download


# to show option to play sound
# def playSound(Song):
#     def stopPlay():
#         pygame.mixer.music.stop()

#     def play():
#         pygame.mixer.music.load(Song)
#         pygame.mixer.music.play(loops=0)

#     emptyText = Label(master=frame_c, text=" \n \n \n", background=bgColor)
#     emptyText.grid(row=0, column=0)

#     play_button = Button(master=frame_c, text="Play Song", background=bgColor, foreground="purple",
#                          font=("Arial", textSize), command=play)
#     play_button.grid(row=1, column=0)

#     stop_button = Button(master=frame_c, text="Stop Song", background=bgColor, foreground="purple",
#                          font=("Arial", textSize), command=stopPlay)
#     stop_button.grid(row=1, column=1)
#     frame_c.pack()


# buffer main
def showOptions(genres):
    # get seed and array
    song_seed = get_song_seed(genres, ranges)
    arrayToSong = generate_song(song_seed, maxs, mins)
    song = Song()
    passMIDI = song.featureVector_toMidi(arrayToSong)
    passMIDI.save('songGenerated.mid')

     # send to get Mp3
    # passMP3 = song.midiToAudio(arrayToSong)
    # playSound(passMP3)
    # print(passMP3)
    downloadMIDI()


# spacing
def dummyValue():
    emptyText = Label(master=frame_z, text=" \n \n \n", background=bgColor)
    emptyText.grid(row=1, column=1)
    frame_z.pack()


# show all buttons for options
def UserButtons():
    # button for selection
    frame_a = Frame(background=bgColor)
    button = Button(master=frame_a, text="Boss Fight", background=bgColor, fg="purple", font=("Arial", textSize),
                    command=lambda: [dummyValue(), showOptions(0)])
    button.grid(row=2, column=0)

    button1 = Button(master=frame_a, text="Spooky", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(1)])
    button1.grid(row=2, column=1)

    button2 = Button(master=frame_a, text="Adventurous", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(2)])
    button2.grid(row=2, column=2)

    button3 = Button(master=frame_a, text="Upbeat Overworld", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(3)])
    button3.grid(row=2, column=3)

    button4 = Button(master=frame_a, text="Ominous", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(4)])
    button4.grid(row=3, column=1)

    button5 = Button(master=frame_a, text="Calm Overworld", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(5)])
    button5.grid(row=3, column=2)

    button6 = Button(master=frame_a, text=" Overworld", background=bgColor, fg="purple", font=("Arial", textSize),
                     command=lambda: [dummyValue(), showOptions(6)])
    button6.grid(row=3, column=3)
    frame_a.pack()


# show title at top of page
def showTitle():
    Prompt = Label(root, text="Select keyword from below\nEach will provide a MIDI file ", height=5,
                   background=bgColor, foreground="purple", font=("Arial", 30))
    Prompt.pack()

    # Create a photo image object of the image in the path
    image1 = Image.open("brainMusic.jpg")
    photoimage = image1.resize((150, 150), Image.ANTIALIAS)
    test = ImageTk.PhotoImage(photoimage)
    label1 = Label(image=test)
    label1.image = test

    # Position image
    label1.place(x=55, y=15)


def main():
    showTitle()
    UserButtons()
    root.mainloop()


'''
Initialise program
Global varable needed to:
    set up window size
    Set color of window
    set frame so it can be refreshed
Run program
'''
if __name__ == "__main__":
    root = Tk()
    # pygame.mixer.init()

    bgColor = "#f8f4ec"
    root.title("NES MIDI Maker")
    root.geometry("1080x720")
    root.resizable(width=False, height=False)
    root.configure(bg=bgColor)
    textSize = 25
    # frame for play/ stop
    frame_c = Frame()
    # frame for download
    frame_d = Frame()
    # frame for Dummy
    frame_z = Frame()

    # feature_ranges.csv
    ranges = pd.read_csv('feature_ranges.csv')
    ranges = ranges.to_numpy()
    # Maxs.csv and Mins.csv
    maxs = pd.read_csv('Maxs.csv')
    mins = pd.read_csv('Mins.csv')
    del maxs['Unnamed: 0']
    del mins['Unnamed: 0']

    main()