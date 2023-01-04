# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 09:41:14 2022

@author: Brayden

This file should only need to be used once. It is to extract all the midi files into Song objects and stored 
with the pickle module after creation
"""

from mido import MidiFile
import pickle
from dataCleanup import Song
import numpy as np
import pandas as pd

file = r'C:\Users\jason\Documents\Python Scripts\CmpSc-445-ML-Project-main\rawMidiFiles\rawMidiFiles'

#extract data from pickled file
midiFiles = open(file, 'rb')
midi = pickle.load(midiFiles)
midiFiles.close()

#initialize list of songs and add Song objects to it
#Only retain files longer than 10 seconds
Songs = []
for item in midi:
    try:
        if 10 <= item.length <= 300:
            Songs.append(Song(item))
    except TypeError:
        print("Type Error")
        
with open(r'C:\Users\jason\Documents\Python Scripts\CmpSc-445-ML-Project-main\Song Objects\songs', 'wb') as f:
    pickle.dump(Songs, f)