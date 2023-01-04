# -*- coding: utf-8 -*-
"""
ComposerV1.py

Data Format:
    A measure is defined as 1920 ticks of a mdid file. This will be fed into the measure encoder.
    8 of these encoded measures will be appended and fed into the song encoder. This format yields
    a measure encoder with an input dimension of 168,960
    
Model Structure:
    The model will treat a song as entirely time independent, like one entity all together rather than
    a series of entities associated across time
"""

import os
import shutil
import numpy as np

# source_directory = 'C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\featureVectors\\'
# destination_directory = 'C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\Composer V1 Data\\'

#iterate through the feature vector files and only keep the ones with atleast 8 measures - complete
# for filename in os.listdir(source_directory):
#     with open(source_directory+filename, 'rb') as tempfile:
#         tempvec = np.load(tempfile, allow_pickle=True)
#         if len(tempvec)//1920 >= 8:
#             shutil.copy(source_directory+filename, destination_directory+filename)

"""
For each file in destination_directory (the original complete songs), split them into measures
and format them for input into the network. Add each of these formatted songs into a new file in a new directory
"""
#redfine the directories
source_directory = 'C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\Composer V1 Data\\'
destination_directory = 'C:\\Users\\jason\\Documents\\Python Scripts\\CmpSc-445-ML-Project-main\\Song Objects\\Composer V1 Measures\\'

#split the songs into measures and place each measure file into the proper directory
# from dataCleanup import makeMeasures
# from random import sample
# import pickle

# for filename in os.listdir(source_directory):
#     with open(source_directory+filename, 'rb') as tempfile:
#         tempsong = np.load(tempfile, allow_pickle=True)
#         #Now split the song into measures and retain 3 measures at random, yielding about 15k training samples
#         measures = makeMeasures(tempsong)
        
#         indices = list(range(0,len(measures))) 
#         rand_index = sample(indices, 3)
        
#         for item in rand_index:
#             with open(destination_directory+filename[:-4]+'-'+str(item)+'.npy', 'wb') as tempmeasure:
#                 np.save(tempmeasure, measures[item].reshape((168960,1)), allow_pickle=True)


"""
The following section will setup the generator to feed the data into the model. It closely follows the guide 
provided in https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly.
"""
#create partition of training and validation and testing data
partition = {'training':[],
               'validation':[],
               'testing':[]}

allIDs = []
for filename in os.listdir(destination_directory):
    allIDs.append(destination_directory+filename)
    
from sklearn.model_selection import train_test_split

train_size = .7
val_size = .15
test_size = .15

partition['training'], leftover = train_test_split(allIDs, train_size=train_size, random_state=36)
partition['validation'], partition['testing'] = train_test_split(leftover, train_size=.5) #.5 of leftover is .15 of total

params = {'dim':(168960,),
          'batch_size':8,
          'n_channels':1,
          'shuffle':True}

#Define the generators
from DataGeneratorV1 import DataGenerator

training_generator = DataGenerator(partition['training'], **params)
validation_generator = DataGenerator(partition['validation'], **params)

"""
The follow section defines the measure autoencoder. The encoded results of the measure encoder will eventually be
passed along to the song encoder.

Model Structure:
    Input layer - 168960
    Hidden Layer 1 - 20000
    Hidden Layer 2 - 8000
    Hidden Layer 3 - 1500
    Code Size - 800
    Hidden layer 4 - 1500
    Hidden Layer 5 - 8000
    Hidden Layer 6 - 20000
    Output layer - 168960
"""
input_size = 168960
hidden_1_size = 20000
hidden_2_size = 8000
hidden_3_size = 1500
code_size = 800

from keras.layers import Input, Dense
from keras.models import Model
from keras import callbacks, backend

#define callbacks for model monitoring
cb=callbacks.Callback()
es=callbacks.EarlyStopping(monitor='val_loss', mode='min', patience=50)

cb_list=[es]

#define the model layers and compile the model
input_layer = Input(shape=(input_size,))
hidden_layer_1 = Dense(hidden_1_size, activation='relu')(input_layer)
hidden_layer_2 = Dense(hidden_2_size, activation='relu')(hidden_layer_1)
hidden_layer_3 = Dense(hidden_3_size, activation='relu')(hidden_layer_2)
encoded_measure = Dense(code_size, activation='relu')(hidden_layer_3)
hidden_layer_4 = Dense(hidden_3_size, activation='relu')(encoded_measure)
hidden_layer_5 = Dense(hidden_2_size, activation='relu')(hidden_layer_4)
hidden_layer_6 = Dense(hidden_1_size, activation='relu')(hidden_layer_5)
output_layer = Dense(input_size, activation='relu')(hidden_layer_6)

measure_model = Model(input_layer, output_layer)

measure_model.compile(optimizer='adam', loss='mse')

#fit the measure autoencoder
measure_model.fit_generator(generator=training_generator,
                            validation_data=validation_generator,
                            use_multiprocessing=True,
                            workers=1,
                            epochs=10,
                            callbacks=cb_list,
                            steps_per_epoch = 202/8)