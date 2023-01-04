# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 09:14:49 2022

@author: Brayden

Log file:
    Keeps track of the purpose of each object and whether the functionality is working properly. Documentation 
    for each function and class will be contained here
    
"""
"""
dataCleanup.py

    Song class: acts as a place holder for a feature vector corresponding to a single song
    Includes functionality for the following tasks:
        1. Convert a midi file to a feature vector
        2. Plot a feature vector
        3. Convert a feature vector back to a midi file
        4. Convert a midi file to an mp3 file
        
        
        
        
    dataExtraction.py ******************DO NOT RUN************************
        This file was written by Jake Loedding. It should only need to be run once if the data isn't already available.
        The purpose is to scrape the data from the internet and store the resulting midi objects using pickle. Currently, 
        these files are stored in the rawMidiFiles folder.
        
    midi to pyhton.py
        The purpose of this file is to get the data in rawMidiFiles converted from the MidiFile objects into Song objects.
        These song objects are then used to better organize and handle the data going in and out of the model. These
        objects will be stored using pickle.
        
    loading_sciprt.py
        Only used when the model is complete and ready to be run.
        
    midi to python.py
        This file simply extracts the midi files and puts them all into Song objects, but the Song objects have not
        generated the feature vectors, this must be done upon further processing.
"""


