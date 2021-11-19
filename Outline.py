# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 11:25:28 2021

@author: Brayden Peoples
"""

"""
Model outline:
    Structure:
        RNN
        CNN will not work due to underlying assumptions.
        LSTM could be used if we modify it to learn structure as well
            Melodic structures within measures are learned, then
            another feature is respsonsible for structure, or another
            LSTM learns the structure based on melody labeling.

        
        Code Parade Approach:
            Dense network learns the measure and encodes into a
            feature vector of 200 dimensions
            Those vectors are fed into Autoencoder of 120 dimensinos 
            that learns the song
            
            2 Models
                First learns the measure structures
                Second learns the song structure built of measures
        
        Melody Recurrent NN from Magenta:
            
            
    Input schemes:
        We generate simple midi files to prime, or we generate 
        feature vectors at a higher level spot in the process and 
        input those directly to the decoder
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import tensorflow as tf
from keras.models import Model
        
"""
Model Architecture for encoding measures:
    Input Layer
    Hidden 1
    Hiddne 2
    Code (Feature Vector)
    Hidden 3
    Hidden 4
    Output Layer
"""
from keras.layers import Input, Dense, Flatten, Reshape, TimeDistributed

input_size=8448
hidden_1_size=2000
hidden_2_size=800
code_size=150
hidden_3_size=800
hidden_4_size=2000
output_size=8448


#reshape data for network
#convert each measure into matrix with 88x96x1, res
measure=measures[0]
measure=measure.reshape(8448,1)

#define measure encoder 
input_measures=Input(shape=(88,96))
flattener=Flatten(input_shape=(88,96))(input_measures)
hidden_1=Dense(hidden_1_size,activation='relu')(flattener)
hidden_2=Dense(hidden_2_size, activation='relu')(hidden_1)

code=Dense(code_size,activation='relu')(hidden_2) #this will be sent to the second autoencoder

hidden_3=Dense(hidden_3_size,activation='relu')(code)
hidden_4=Dense(hidden_4_size,activation='relu')(hidden_3)
output_measures=Dense(output_size,activation='sigmoid')(hidden_4)
output_measures=Reshape((88,96))(output_measures)
 

autoencoder=Model(input_measures,output_measures)
autoencoder.compile(optimizer='adam',loss='mean_squared_error')

#fit the measure encoder
autoencoder.fit(x_train,x_train,
                epochs=200,
                batch_size=100,
                validation_data=(x_test,x_test))



"""
The above model will learn the measures. The output the encoder section, code, will be sent as one part
of the input to the second one, which will receive 16 of them comprising the whole song. 
"""

song_size=100

#encode measures to send to second encoder, that learns the songs
encoded_measures_train=encoder.predict(x_train)
encoded_measures_test=encoder.predict(x_test)

input_song=Input(shape=(code_size), batch_size=16)
encoded_song=Dense(song_size, activation='relu')(input_song)
output_song=Dense(code_size,activation='sigmoid')(encoded_song)

autoencoder2=Model(input_song,output_song)
autoencoder2.compile(optimizer='adam',loss='binary_crossentropy')

autoencoder2.fit(encoded_measures_train,encoded_measures_train,
                 epochs=300,
                 batchsize=10,
                 validation_data=(encoded_measures_test,encoded_measures_test))

#generates the song based on the seed values
def generate_song():
    return None
    
#returns the seed values for the encoded song
def get_song_seed():
    return None









