
import pickle
import string
import numpy as np
import matplotlib.pyplot as plt

class Song:
    # A list of meausures converted to matrices. corresponds to samples
    featureVector = []

    # Minimum percentage of messages to  
    minMessagePct = 0.1 

    # Constructor that takes a midi file
    def __init__(self, midi):
        self.midiFile = midi


    def getState(self, track_messageString, lastState):
        """Convert track_messageString to a dictionary"""
        newMessage = dict()
        if ('note_on' in track_messageString):
            on = True
        elif ('note_off' in track_messageString):
            on = False
        else:
            on = None

        # Parse track_messageString to extract the time attribute
        time = track_messageString[track_messageString.rfind('time'):].split(' ')[0].split('=')[1]
        time = time.translate(str.maketrans({x: None for x in string.punctuation}))
        newMessage['time'] = int(time)

        if (on is not None):
            relAttributes = ['note', 'velocity'] # Relevant attributes
            for attribute in relAttributes:
                tempAttribute = track_messageString[track_messageString.rfind(attribute):].split(' ')[0].split('=')[1]
                tempAttribute = tempAttribute.translate(str.maketrans({x: None for x in string.punctuation}))
                newMessage[attribute] = int(tempAttribute)

        """Update the state of the note"""
        if (on is not None):
            note = newMessage['note']
            vel = newMessage['velocity']
                
            if (lastState is None):
                newState = [0] * 88
            else:
                newState = lastState.copy()

            # Ignore the notes out of the range of notes on a piano
            if (21 <= note <= 108):
                if (on == True):
                    newState[note - 21] = vel
                else:
                    newState[note - 21] = 0

        else:
            newState = lastState

        return [newState, newMessage['time']]
            
        

    def generateFeatureVector(self):
        
        trackLengths = []
        
        # Populate a list containing the length of each track 
        for track in self.midiFile.tracks:
            trackLengths.append(len(track))

        # Calculate the minimum number of messages to evaluate
        minMessages = max(trackLengths) * self.minMessagePct

        # Generate a list representations of each track
        trackLists = []
        for track in self.midiFile.tracks:
            if (len(track) > minMessages):

                tempList = []

                lastState, lastTime = self.getState(str(track[0]), [0] * 88)

                for i in range(1, len(track)):
                    newState, newTime = self.getState(str(track[i]), lastState) 
                    if(newTime > 0):
                        tempList += [lastState] * newTime

                    lastState = newState
                    lastTime = newTime

                trackLists.append(tempList)

        # Calculate the maximum length of the elements in trackLists
        trackListLengths = []
        for tl in trackLists:
            trackListLengths.append(len(tl))

        maxLength = max(trackListLengths)

        # Ensure that all multidimmentional lists have the same dimmensions
        for i in range(len(trackLists)):
            if(len(trackLists[i]) < maxLength):
                trackLists[i] += [[0] * 88] * (maxLength - len(trackLists[i]))

        trackArrays = np.array(trackLists)
        trackArrays = trackArrays.max(axis = 0)

        # Remove preceeding and trailing zeros
        sums = trackArrays.sum(axis = 1)
        endPoints = np.where(sums > 0)[0]

        self.featureVector = trackArrays[min(endPoints): max(endPoints)]


    def featureVecture_toMidi(self):
        test = 0



if __name__ == '__main__':
    with open('testFiles', 'rb') as f:
        testFiles = pickle.load(f)
    """
    song = Song(testFiles[5])
    song.generateFeatureVector()

    plt.plot(range(song.featureVector.shape[0]), np.multiply(np.where(song.featureVector > 0, 1, 0), range(1, 89)), marker='.', markersize=1, linestyle='')
    plt.show()
    """

    i = 0
    testDataset = []
    for test in testFiles:
        song = Song(test)
        song.generateFeatureVector()
        testDataset.append(song)
        print("Success", i)
        i += 1

    # Create a test file containing an array of 11 song objects for experimentation 
    with open('testDataset', 'wb') as f:
        pickle.dump(np.array(testDataset), f)

        
        
