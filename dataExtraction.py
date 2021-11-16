# NES MIDI File Data Extraction (Web Scrapping)
# Developer: Jakob Loedding

""" Sources:
1. https://www.youtube.com/watch?v=0HgZxv6DJUY
2. https://www.twilio.com/blog/working-with-midi-data-in-python-using-mido
3. https://stackoverflow.com/questions/5710867/downloading-and-unzipping-a-zip-file-without-writing-to-disk
"""

import requests
import os
from bs4 import BeautifulSoup
from mido import MidiFile
from io import BytesIO
import pickle

# Runtime 8:48 pm -
# Stops at file 3286 for some reason

# Extract midi files from vgmusic.com
def getMidiFiles(baseURL):

    print('Extarcting MIDI files from ' + baseURL)    
    vgMusicPage = requests.get(baseURL)

    soup = BeautifulSoup(vgMusicPage.content, 'html.parser')

    pageLinks = soup.find_all('a')

    midiFiles = [] # List to store extracted midi files

    i = 0 # for testing purposes

    for link in pageLinks:
        
        #if(i == 3):# testing
         #   break

        linkString = str(link.get('href'))
        
        if (linkString.endswith('.mid')):
            #print(linkString + '\n')
            midiLink = baseURL + linkString
                
            fileName = midiLink.split('/')[-1]

            midiFile = requests.get(midiLink, stream = True)
            
            with open(fileName, 'wb') as file:
                file.write(midiFile.content)

            try:
                tempMidiFile = MidiFile(fileName, clip = True)
                print('File ', i, fileName, " ") # testing
                i +=1 # testing
            except (BaseException): # skip the corrupted midi files
                print("Handle key signature error here!") # testing
                os.remove(fileName)
                continue
                
            midiFiles.append(tempMidiFile)
            os.remove(fileName)

    return midiFiles

if __name__ == '__main__':
        
    NES_URL = 'http://vgmusic.com/music/console/nintendo/nes/'
    SEGA_MasterSystem_URL = 'https://www.vgmusic.com/music/console/sega/master/'
    
    midiFiles = getMidiFiles(NES_URL) + getMidiFiles(SEGA_MasterSystem_URL)
    
    rawMidiFiles_FileName = 'rawMidiFiles'

    with open(rawMidiFiles_FileName, 'wb') as f:
        pickle.dump(midiFiles, f)            
    
    





