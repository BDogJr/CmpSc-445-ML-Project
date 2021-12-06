# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 12:03:21 2021

@author: Brayden Peoples
"""
import pandas as pd
import numpy as np
import pickle
#This script will handle encoding all of our songs for clustering
maxs=pd.read_csv('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\Maxs.csv')
mins=pd.read_csv('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\Mins.csv')
del maxs['Unnamed: 0']
del mins['Unnamed: 0']

with open('C:\\Users\\Brayden Peoples\\OneDrive\\Documents\\Python\\Scripts\\Applied Machine Learning\\FInal Project\\rawMidiFiles', 'rb') as f:
    rawMidiFiles = pickle.load(f)

k = 0
encoded_songs=[]
for midiFile in rawMidiFiles:
    try:
        song = Song(midiFile)
        song.generateFeatureVector()
        #Now, if the song has length >=16, take 16 measures and encode them into a song vector
        featureVectors=makeMeasures(song)

        measures=[]
        for i in range(len(featureVectors)):
            measures.append(featureVectors[i].reshape(1,8448)) 
            #meaures is a list of arrays, each array has shape (1,8448)
        
        X=np.concatenate(measures,axis=0) # will be encoded into a song
        #set X to all zero and 1
        X=pd.DataFrame(X)
        X=X.astype(bool).astype(int)
        X=X.to_numpy()
        
        if X.shape[0]>=16 and X.shape[0]<800:
            X=X[0:16]
            encoded_measures=measureEncoder.predict(X)
            #Perform min max scaling on encoded measures
            song_vectors=pd.DataFrame(encoded_measures)
            song_vectors_norm=(song_vectors-mins.to_numpy().transpose())/(maxs.to_numpy().transpose()) 
                #difference of mins is not needed since mins is all 0
            song_vectors_norm=song_vectors_norm.fillna(0)
            song_vectors_norm=song_vectors_norm.to_numpy()
                        
            
            song_vectors_norm=song_vectors_norm.reshape(1,3520)
            #This is now a (1,3520) vector
            
            encoded_song=songEncoder.predict(song_vectors_norm)
            encoded_songs.append(encoded_song)
            
        else:
            print('song not the right size for encoding')
        
        
        
        print("Success", k)
        k += 1
    except:
        k += 1
        print('Failure on song ', k)
        
clusterable=np.concatenate(encoded_songs,axis=0)
pd.DataFrame(clusterable).to_csv('encoded_songs.csv')

#Now starts the clustering bit
from sklearn.cluster import MiniBatchKMeans

Eval=[]
k=range(1,15)
for K in k:
    cluster_model=MiniBatchKMeans(n_clusters=K)
    cluster_model=cluster_model.fit(clusterable)
    Eval.append(cluster_model.inertia_)
    
plt.plot(k, Eval, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()

cluster_model=MiniBatchKMeans(n_clusters=7).fit(clusterable)

centroids=cluster_model.cluster_centers_
labels=cluster_model.predict(clusterable)

first, second, third, fourth, fifth, sixth, seventh=(clusterable[labels==0], clusterable[labels==1],
                                                     clusterable[labels==2], clusterable[labels==3],
                                                     clusterable[labels==4], clusterable[labels==5],
                                                     clusterable[labels==6])

#use the above arrays to determine the max and min value of each feature in each cluster
ranges=np.ndarray((14,400))
for i in range(14):
    for j in range(400):
        if i == 0:
            ranges[i,j]=max(first[:,j])
        elif i ==1:
            ranges[i,j]=max(second[:,j])
        elif i ==2:
            ranges[i,j]=max(third[:,j])
        elif i ==3:
            ranges[i,j]=max(fourth[:,j])
        elif i ==4:
            ranges[i,j]=max(fifth[:,j])
        elif i ==5:
            ranges[i,j]=max(sixth[:,j])
        elif i ==6:
            ranges[i,j]=max(seventh[:,j])
        elif i == 7:
            ranges[i,j]=min(first[:,j])
        elif i ==8:
            ranges[i,j]=min(second[:,j])
        elif i ==9:
            ranges[i,j]=min(third[:,j])
        elif i ==10:
            ranges[i,j]=min(fourth[:,j])
        elif i ==11:
            ranges[i,j]=min(fifth[:,j])
        elif i ==12:
            ranges[i,j]=min(sixth[:,j])
        elif i ==13:
            ranges[i,j]=min(seventh[:,j])

def get_song_seed(genre, ranges):
    from random import uniform
    #return a new song seed, being the encoded song, based on the given genre.
    #genre is an integer 0-6.
    song_seed=np.ndarray((1,400))
    for i in range(400):
        song_seed[0,i]=uniform(ranges[genre,i],ranges[genre+7,i])
        
    return song_seed

def generate_song(seed, maxs, mins):
    new_song=songDecoder.predict(seed)
    new_song=new_song.reshape(16,220)
    #The next line rescales to the measure encoder space, it was scaled down to speed up training
    new_song=(new_song*maxs.to_numpy().transpose())+mins.to_numpy().transpose()
    new_song=measureDecoder.predict(new_song)
    return new_song
    #at this point, new_song has lots of values very close to 0, but not 0. Try cleaning up file
    # by including, excluding, or selectively including them to what the output is. Possibly choose to
    #include them randomly 