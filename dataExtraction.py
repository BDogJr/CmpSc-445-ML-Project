# MIDI File Data Extraction (Web Scrapping)
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
import pickle

"""
A function that extracts midi files from vgmusic.com
This function performs the following tasks:
    1. Web scrapes the links for downloadable midi files
    2. Downloads all the midi files
    3. Creates a list of MidiFile mido objects
Input: 
    1. Website URL
Output:
    1. A list of MidiFile mido objects 
"""
def getMidiFiles(baseURL):

    print('Extarcting MIDI files from ' + baseURL)  # Show progress
    vgMusicPage = requests.get(baseURL)

    soup = BeautifulSoup(vgMusicPage.content, 'html.parser')

    # Find all downloadable links on the webpage
    pageLinks = soup.find_all('a')

    midiFiles = [] # List to store extracted midi files

    i = 0 # For testing purposes

    for link in pageLinks:
        linkString = str(link.get('href'))
        
        if (linkString.endswith('.mid')): # The link is a downloadable midi file
            midiLink = baseURL + linkString
                
            fileName = midiLink.split('/')[-1]

            # Download the midi file
            midiFile = requests.get(midiLink, stream = True)

            # Store the midi file on the hard drive
            with open(fileName, 'wb') as file:
                file.write(midiFile.content)

            try: # Try to create a MidiFile mido object
                tempMidiFile = MidiFile(fileName, clip = True)
                print('File ', i, fileName, " ") # Show progress
                i +=1
            except (BaseException): # Skip the corrupted midi files
                print("Error! File corrupted.")
                os.remove(fileName)
                continue
                
            midiFiles.append(tempMidiFile) # Add mido object to the midiFiles list
            os.remove(fileName) # Delete the raw midi file

    return midiFiles


# Main function that calls the getMidiFiles() function and saves the list of mido objects to a bytes file
if __name__ == '__main__':
        
    NES_URL = 'http://vgmusic.com/music/console/nintendo/nes/'
    SEGA_MasterSystem_URL = 'https://www.vgmusic.com/music/console/sega/master/'
    
    midiFiles = getMidiFiles(NES_URL) + getMidiFiles(SEGA_MasterSystem_URL)
    
    rawMidiFiles_FileName = 'rawMidiFiles'

    with open(rawMidiFiles_FileName, 'wb') as f:
        pickle.dump(midiFiles, f)