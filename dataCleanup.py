import pickle
import string
import numpy as np
import matplotlib.pyplot as plt
import mido
from collections import defaultdict
from pydub import AudioSegment
from pydub.generators import Sine

"""
Song class: that acts as a place holder for a feature vector corresponding to a single song
Includes functionality for the following tasks:
    1. Convert a midi file to a feature vector
    2. Plot a feature vector
    3. Convert a feature vector back to a midi file
    4. Convert a midi file to an mp3 file
"""
class Song:
    # A list of meausures converted to matrices. corresponds to samples
    featureVector = []

    # Minimum percentage of messages to  
    minMessagePct = 0.1 


    # Constructor that takes a midi file or no arguments
    def __init__(self, *midi):
        if(len(midi) == 1): # Initialize midiFile attribute
            self.midiFile = midi[0]
        else: # No midiFile attribute
            print("yes")

    """
    An intermediate function that gets the current state of a note
    Input:
        1. track_messageString: The message of a track as a string
        2. lastState: an nx88 array
    Output:
        1. A list containing the current state of a note along with its time stamp
    """
    def getState(self, track_messageString, lastState):
        #Convert track_messageString to a dictionary
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

        #Update the state of the note
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

    """
    A function that generates an nx88 feature vector as an array
    Input:
        1. None
    Output:
        1. None: The function updates the featureVector attribute inside the class
    """
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


    """
    A function that converts a feature vector back to a MidiFile mido object
    Input:
        1. encodedArray: A 96x88 array. The output of our machine learning model
    Output:
        1. A MidiFile mido object
    """
    def featureVector_toMidi(self, encodedArray):

        tempList = [np.array([[0] * 88]), np.array(encodedArray)]
        tempArray = np.concatenate(tempList, axis = 0)
        differences = tempArray[1:] - tempArray[:-1]

        # Prep midi new file
        midi = mido.MidiFile() # Create midi file
        midiTrack = mido.MidiTrack() # Create midi track
        midi.tracks.append(midiTrack) # Add a new track
        # Set tempo to 500000
        midiTrack.append(mido.MetaMessage('set_tempo', tempo = 500000, time = 0))

        # Account for the differences in midiTrack
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

    """
    A function that converts a feature vector to a midi file and then converts the midi file to an mp3 file
    Input:
        1. encodedArray: A 96x88 array. The output of our machine learning model
    Output:
        1. None: This functions downloads the mp3 file directly to the hard drive
    """
    def midiToAudio(self, encodedArray):
        midi =  self.featureVector_toMidi(encodedArray)
        audio = AudioSegment.silent(midi.length * 1000.0)
        bpm = 100 # Beats per minute

        for track in midi.tracks:
            currentPosition = 0.0
            currentNotes = defaultdict(dict)

            for message in track:
                # Convert ticks to milliseconds
                tickMS = (60000.0 / bpm) / midi.ticks_per_beat
                currentPosition += (message.time * tickMS)

                if (message.type == 'note_on'):
                    currentNotes[message.channel][message.note] = (currentPosition, message)

                if (message.type == 'note_off'):
                    startPostion, startMessage = currentNotes[message.channel].pop(message.note)

                    totalDuration = currentPosition - startPostion

                    # Convert midi note number to frequency
                    # Formula found here: https://newt.phys.unsw.edu.au/jw/notes.html
                    freq = (2.0 ** ((message.note - 69) / 12.0)) * 440.0
                    sigGenerator = Sine(freq)

                    # Render a single segment of the mid file
                    segRendered = sigGenerator.to_audio_segment(duration = totalDuration - 50, volume = -20).fade_out(100).fade_in(30)
                    audio = audio.overlay(segRendered, startPostion)

        audio.export("autoGeneratedMP3.mp3", format = 'mp3')

    """
    A function that generates and saves a pitch-time plot using the feature vector corresponding to a midi file
    Input:
        1. sampleNumber: An integer (the index of the sample)
    Output:
        1. None: This function saves the pitch-time plot directly to the hard drive
    """
    def plotMidi(self, sampleNumber):

        xRange = range(self.featureVector.shape[0])
        yRange = np.multiply(np.where(self.featureVector > 0, 1, 0), range(1, 89))

        plt.plot(xRange, yRange, marker = '.', markersize = 1, linestyle = '')
        plt.title('Sample Number ' + str(sampleNumber))
        plt.xlabel('Time')
        plt.ylabel('Pitch')
        plt.savefig('Sample_Number' + str(sampleNumber) + '.png')

# A main function to test the functions in the Song class
# Also
if __name__ == '__main__':

    with open('testFiles', 'rb') as f:
        rawMidiFiles = pickle.load(f)

    """Plot a few feature vectors
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
    """
    
    i = 0 # Helps keep track of progress
    completeDataset = []
    for midiFile in rawMidiFiles:
        song = Song(midiFile)
        song.generateFeatureVector()
        completeDataset.append(song)
        print("Success", i) # Print progress
        i += 1

    with open('completeDataset', 'wb') as f:
        pickle.dump(np.array(completeDataset), f)
        
        
