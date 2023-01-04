# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 19:19:01 2022

@author: Brayden

This file utilizes the class and functions defined in dataCleanup.py to clean up the data and get it into a form that can
be used for training.

Will need to load the the Song objects with pickle before this file can be run
"""

from dataCleanup import Song, makeMeasures
import os
from mido import MidiFile
import pickle

file_location='C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\featureVectors\\'

with open('C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\songs','rb') as f:
    Songs=pickle.load(f)

#remove duplicate tracks from the midi files
for song in Songs:
    midi = song.midiFile

    message_numbers = []
    duplicates = []

    for track in midi.tracks:
        if len(track) in message_numbers:
            duplicates.append(track)
        else:
            message_numbers.append(len(track))
    
    for track in duplicates:
        midi.tracks.remove(track)

#Generate feature vectors for each song and save the generated vectors
for i, song in zip(range(len(Songs)), Songs):
    temp=Song(song.midiFile)
    try:
        temp.generateFeatureVector()
        temp.saveFeatureVector(file_location+'song'+str(i)+'.npy')
    except Exception as e:
        continue
        
"""
Model Data Extraction V1:
    Pull the first 16 measures of each song to train the model on
"""
featureVectors = [makeMeasures(song) for song in Songs]
