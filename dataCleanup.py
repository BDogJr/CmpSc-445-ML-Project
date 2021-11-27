import pickle
import string
import numpy as np
import matplotlib.pyplot as plt
import mido
from midi2audio import FluidSynth

# Source for midi to : https://pypi.org/project/midi2audio/
# https://gist.github.com/jiaaro/339df443b005e12d6c2a

class Song:
    # A list of meausures converted to matrices. corresponds to samples
    featureVector = []

    # Minimum percentage of messages to  
    minMessagePct = 0.1 

    # Constructor that takes a midi file
    def __init__(self, midi):
        self.midiFile = midi

    # Place holder constructor so Song objects can be made without providing a midi file
    def __init__(self):
        self.temp = 0

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

        # Ensure that all multidimensional lists have the same dimmensions
        for i in range(len(trackLists)):
            if(len(trackLists[i]) < maxLength):
                trackLists[i] += [[0] * 88] * (maxLength - len(trackLists[i]))

        trackArrays = np.array(trackLists)
        trackArrays = trackArrays.max(axis = 0)

        # Remove preceeding and trailing zeros
        sums = trackArrays.sum(axis = 1)
        endPoints = np.where(sums > 0)[0]

        self.featureVector = trackArrays[min(endPoints): max(endPoints)]


    def featureVector_toMidi(self, encodedArray):

        tempList = [np.array([[0] * 88]), np.array(encodedArray)]
        tempArray = np.concatenate(tempList, axis = 0)
        differences = tempArray[1:] - tempArray[:-1]

        """Prep midi new file"""
        midi = mido.MidiFile() # Create midi file
        midiTrack = mido.MidiTrack() # Create midi track
        midi.tracks.append(midiTrack) # Add a new track
        # Set tempo to 500000
        midiTrack.append(mido.MetaMessage('set_tempo', tempo = 500000, time = 0))

        """Account for the differences in midiTrack"""
        prevTime = 0
        for d in differences:
            if(set(d) == {0}): # There is no difference
                prevTime += 1
            else:
                onNotes = np.where(d > 0)[0]
                notesVelocity = d[onNotes]
                offNotes = np.where(d < 0)[0]
                firstNote = True

                """Generate appropriate tracks"""
                for note,vel in zip(onNotes, notesVelocity): # Cycle through onNotes
                    updatedTime = 0
                    if (firstNote == True): # Do not update time for first note
                        updatedTime = prevTime

                    midiTrack.append(mido.Message('note_on', note = note + 21, velocity = vel, time = updatedTime))
                    firstNote = False

                for note in offNotes: # Cycle through offNotes
                    updatedTime = 0
                    if (firstNote == True):  # Do not update time for first note
                        updatedTime = prevTime

                    midiTrack.append(mido.Message('note_off', note = note + 21, velocity = 0, time = updatedTime))
                    firstNote = False

                prevTime = 0
        return midi

    def midiToAudio(self):
        test = 0


    def plotMidi(self, sampleNumber):

        xRange = range(self.featureVector.shape[0])
        yRange = np.multiply(np.where(self.featureVector > 0, 1, 0), range(1, 89))

        plt.plot(xRange, yRange, marker = '.', markersize = 1, linestyle = '')
        plt.title('Sample Number ' + str(sampleNumber))
        plt.xlabel('Time')
        plt.ylabel('Pitch')
        plt.savefig('Sample_Number' + str(sampleNumber) + '.png')

if __name__ == '__main__':

    with open('testDataset', 'rb') as f:
        test = pickle.load(f)

    testFeatureVect = test[7]
    midi = testFeatureVect.featureVector_toMidi(testFeatureVect.featureVector)
    midi.save("testSongConversion1.mid")

    """
    with open('rawMidiFiles', 'rb') as f:
        rawMidiFiles = pickle.load(f)

    Plot a few feature vectors
    song1 = Song(rawMidiFiles[5])
    song1.generateFeatureVector()
    song1.plotMidi(5)

    song2 = Song(rawMidiFiles[10])
    song2.generateFeatureVector()
    song2.plotMidi(10)

    song3 = Song(rawMidiFiles[15])
    song3.generateFeatureVector()
    song3.plotMidi(15)

    song4 = Song(rawMidiFiles[20])
    song4.generateFeatureVector()
    song4.plotMidi(20)

    song5 = Song(rawMidiFiles[25])
    song5.generateFeatureVector()
    song5.plotMidi(25)
    
    i = 0
    completeDataset = []
    print(len(rawMidiFiles))
    for midiFile in rawMidiFiles[0:1500]:
        song = Song(midiFile)
        song.generateFeatureVector()
        completeDataset.append(song)
        print("Success", i)
        i += 1

    with open('completeDataset(0_1500)', 'wb') as f:
        pickle.dump(np.array(completeDataset), f)
    """
        
        
