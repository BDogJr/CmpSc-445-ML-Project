# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 17:14:10 2021

@author: Brayden Peoples
"""
# get data into csv file
featureVectors=[makeMeasures(completeDataset[i]) for i in range(len(completeDataset))]

measures=[]
for i in range(len(featureVectors)):
    for j in range(len(featureVectors[i])):
        measures.append(featureVectors[i][j].reshape(1,8448))
        
del featureVectors

X=np.concatenate(measures,axis=0)

X2=np.concatenate(measures[40000:70000],axis=0)
X=np.concatenate((X,X2),axis=0)
del X2


pd.DataFrame(X).to_csv('0-50k.csv')
X=pd.read_csv('0-50k.csv')

import numpy as np
import tempfile
from keras import backend as K
from keras.callbacks import LambdaCallback

