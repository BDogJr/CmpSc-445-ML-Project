# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 15:39:42 2021

@author: Brayden Peoples
"""
# This is all the stuff we need for the interface to work properly
import numpy as np
import pandas as pd

import tensorflow as tf
# import tensorflow.train
from keras.models import Model, Sequential, load_model
from keras.layers import Input, Dense, Flatten, Reshape, TimeDistributed
from keras import callbacks
from keras import backend as K
import tempfile
import matplotlib.pyplot as plt

# All the encoders and decoders: The file path will need to be edited

measureDecoder = load_model(
    'C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\measureDecoder.tf')

songDecoder = load_model(
    'C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\songDecoder.tf')


# These two functions:
def get_song_seed(genre, ranges):
    from random import uniform
    # return a new song seed, being the encoded song, based on the given genre.
    # genre is an integer 0-6.
    song_seed = np.ndarray((1, 400))
    for i in range(400):
        song_seed[0, i] = uniform(ranges[genre, i], ranges[genre + 7, i])

    return song_seed


def generate_song(seed, maxs, mins):
    from random import uniform
    new_song = songDecoder.predict(seed)
    new_song = new_song.reshape(16, 220)
    # The next line rescales to the measure encoder space, it was scaled down to speed up training
    new_song = (new_song * maxs.to_numpy().transpose()) + mins.to_numpy().transpose()
    new_song = measureDecoder.predict(new_song)

    ret = []
    for i in range(16):
        ret.append(np.reshape(new_song[i], (96, 88)))

    ret=np.concatenate(ret,axis=0).astype(int)*100
    
    #If timestep has excess notes in it, remove some of them
    # for i in range(1536):
    #     if sum(ret[i]>=6):
    #         notes=np.argwhere(ret[i]==1)
    #         for j in range(len(notes)-2):
    #             prob=uniform(0,1)
    #             if prob<.5:
    #                 ret[i][notes[j+1]]=0
    
    
    for i in range(1530):
        for j in range(88):
            if ret[i][j]==0 and ret[i+1][j]==1 and ret[i+2][j]==1 and ret[i+3][j]==1 and ret[i+4][j]==1 and ret[i+5][j]==1 and ret[i+6]==0:
                ret[i+1][j]=0
                ret[i+2][j]=0
                ret[i+3][j]=0
                ret[i+4][j]=0
                ret[i+5][j]=0
            elif ret[i][j]==0 and ret[i+1][j]==1 and ret[i+2][j]==1 and ret[i+3][j]==1 and ret[i+4][j]==1 and ret[i+5][j]==0:
                ret[i+1][j]=0
                ret[i+2][j]=0
                ret[i+3][j]=0
                ret[i+4][j]=0
            elif ret[i][j]==0 and ret[i+1][j]==1 and ret[i+2][j]==1 and ret[i+3][j]==1 and ret[i+4][j]==0:
                ret[i+1][j]=0
                ret[i+2][j]=0
                ret[i+3][j]=0
            elif ret[i][j]==0 and ret[i+1][j]==1 and ret[i+2][j]==1 and ret[i+3][j]==0:
                ret[i+1][j]=0
                ret[i+2][j]=0
            elif ret[i][j]==0 and ret[i+1][j]==1 and ret[i+2][j]==0:
                ret[i+1][j]=0
    return ret


# feature_ranges.csv
ranges = pd.read_csv('feature_ranges.csv')
ranges = ranges.to_numpy()
# Maxs.csv and Mins.csv
maxs = pd.read_csv('Maxs.csv')
mins = pd.read_csv('Mins.csv')
del maxs['Unnamed: 0']
del mins['Unnamed: 0']