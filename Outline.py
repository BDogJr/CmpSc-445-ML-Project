# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 11:25:28 2021

@author: Brayden Peoples
"""

"""
Model Structure:
    
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

#Data Preparation - made possible with the contents of dataCleanup.py

#Extract the measures from the song objects. featureVectors is a list of 
# arrays. Each array contains 96x88 matrices representing the measures 
# in a song.

featureVectors = measures #measures was defined in dataPrep.py

#Reshape the measures and stack them. The resulting array is of shape
# (numMeasures, 8448), numMeasures is sum of measures of all songs.
measures=[]
for i in range(len(featureVectors)):
    for j in range(len(featureVectors[i])):
        measures.append(featureVectors[i][j].reshape(1,8448))
        
X=np.concatenate(measures,axis=0)

x_train=X[:5000]
x_test=X[7000:7800]
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
import tensorflow as tf
import tensorflow.train
from keras.models import Model, Sequential, load_model
from keras.layers import Input, Dense, Flatten, Reshape, TimeDistributed
from keras import callbacks
from keras import backend as K
import tempfile
import matplotlib.pyplot as plt

input_size=8448
hidden_1_size=3000
hidden_2_size=800
code_size=220
hidden_3_size=800
hidden_4_size=2000
output_size=8448



cb=callbacks.Callback()
es=callbacks.EarlyStopping(monitor='val_loss', mode='min', patience=50)
mc=callbacks.ModelCheckpoint('best_model.tf', monitor='val_loss', verbose=1, save_best_only=True)
cb_list=[es, mc]




#define measure encoder 
input_measures=Input(shape=(8448,))
hidden_1=Dense(hidden_1_size,activation='relu')(input_measures)
hidden_2=Dense(hidden_2_size, activation='relu')(hidden_1)
code=Dense(code_size,activation='relu',name='code')(hidden_2) #this will be sent to the second autoencoder

measureEncoder=Model(input_measures,code)


#define measure decoder
code_input=Input(shape=(code_size,))

hidden_3=Dense(hidden_3_size,activation='relu')(code_input)
hidden_4=Dense(hidden_4_size,activation='relu')(hidden_3)
output_measures=Dense(output_size,activation='sigmoid')(hidden_4)
output_measures=Reshape((8448,))(output_measures)

measureDecoder=Model(code_input,output_measures)


#make the autoencoder to train the pieces
autoencoder=Model(input_measures,measureDecoder(measureEncoder(input_measures)))
autoencoder.compile(optimizer='adam',loss='mean_squared_error')

K.set_value(autoencoder.optimizer.learning_rate, 1e-4)

#fit the measure encoder
measure_model=autoencoder.fit(x_train,x_train,
                batch_size=8,
                epochs=100,
                validation_split=.15,
                callbacks=cb_list,
                initial_epoch=0)




#Create the songs to send to the song encoder
encoded_measures_train=measureEncoder.predict(x_train) #array of measures with shape: (numMeasures, code_size)
encoded_measures_test=measureEncoder.predict(x_test)   # with code_size being the size of the measure

song_vectors=measureEncoder.predict(X)

#scale with min-max scaling
song_vectors=pd.DataFrame(song_vectors)
song_vectors_norm=(song_vectors-song_vectors.min())/(song_vectors.max()-song_vectors.min())
song_vectors_norm.fillna(0, inplace=True)
song_vectors_norm=song_vectors_norm.to_numpy()

mins=song_vectors.min()
maxs=song_vectors.max()
#song vectors will be (1, numInSong*code_size) where numInSong is the number of measures in the song



numInSong=16
songs=[]
for i in range(0,len(song_vectors_norm),numInSong):
    app=np.concatenate(song_vectors_norm[i:i+numInSong],axis=0)
    try:
        songs.append(app.reshape((1,numInSong*code_size)))
    except ValueError:
        break


song_vectors_norm=np.concatenate(songs,axis=0)


#create call backs for song encoder and decoder
song_es=callbacks.EarlyStopping(monitor='val_loss', mode='min', patience=10)
song_mc=callbacks.ModelCheckpoint('song_best_model.tf', monitor='val_loss', verbose=1, save_best_only=True)
song_cb_list=[song_es, song_mc]


song_input_size=16*220
song_hidden_size=1300
song_size=400

#Define the song encoder
input_song=Input(shape=(song_input_size,))
song_hidden_1=Dense(song_hidden_size,activation='relu')(input_song)
encoded_song=Dense(song_size, activation='selu')(song_hidden_1)

songEncoder=Model(input_song,encoded_song)

#Define the song decoder
song_code_input=Input(shape=(song_size,))
song_hidden_2=Dense(song_hidden_size,activation='relu')(song_code_input)
output_song=Dense(song_input_size,activation='sigmoid')(song_hidden_2)

songDecoder=Model(song_code_input, output_song)

#make the autoencoder to train the pieces
song_autoencoder=Model(input_song, songDecoder(songEncoder(input_song)))
song_autoencoder.compile(optimizer='adam',loss='mean_squared_error')

K.set_value(song_autoencoder.optimizer.learning_rate, 1e-4)

song_model=song_autoencoder.fit(song_vectors_norm[0:6000],song_vectors_norm[0:6000],
                 epochs=300,
                 batch_size=8,
                 validation_split=.1,
                 callbacks=song_cb_list,
                 initial_epoch=0)


#rescaling after song decoder
decoded_song=songDecoder.predict()
decoded_song=(decoded_song*(maxs-mins)+mins)


#Saving the models
measureEncoder.save('measureEncoder.tf')
measureDecoder.save('measureDecoder.tf')
autoencoder.save('measureAutoencoder.tf')

songEncoder.save('songEncoder.tf')
songDecoder.save('songDecoder.tf')
song_autoencoder.save('songAutoencoder.tf')

#reload the model
measureEncoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\measureEncoder.tf')
measureDecoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\measureDecoder.tf')
autoencoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\autoencoder.tf')

songEncoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\songEncoder.tf')
songDecoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\songDecoder.tf')
song_autoencoder=load_model('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\songAutoencoder.tf')


#save the data
pd.DataFrame(X).to_csv('X.csv')

#load the data
X=pd.read_csv('X.csv')
X=X.to_numpy()
X=np.delete(X,0,1)


#generates the song based on the seed values
def generate_song():
    return None
    
#returns the seed values for the encoded song
def get_song_seed():
    return None









