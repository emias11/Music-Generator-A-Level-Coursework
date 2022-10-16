# Music-Generator-A-Level-Coursework

This project combined midi files using Markov chains to produce an output midi file that was "merges" the songs. 

Using a Flask GUI, the user is asked for input songs, which are searched for on some major MIDI file websites and scrapped using Beautiful Soup. The user also inputs the song length, ticks per beat and what instruments to include from the songs (this list is generated from the input songs).

The midi files are then cleaned, before being analysed. The following parameters are then recorded for each note:

- velocity on
- velocity off
- delay from previous note
- pitch
- note length




Tempo changes, control changes, and note sequences will remain as stated in Approach 2. Unless time allows, program changes will be ignored as only apply for songs over 16 instruments, unlikely (and can ensure if this is the case, it will just ignore these messages). 


Packaged Used:
Mido (Python package)
  Used to manipulate the MIDI files. This is helpful as MIDI messages are encoded as 8-bit words, and thus are difficult to read without a suitable container- which Mido   provides. Also makes tasks like creating new MIDI messages or identifying MIDI message types easy. 
Beautiful Soup (Python package) 
  Used to scrape the MIDI websites in order to retrieve MIDI files 
Requests (Python package)
  Used to send HTTP(S) requests 
Pygame (Python package) 
  Used to play back any MIDI output on the console 
Flask (Python package)
  Used to provide the user interface for the user to interact with the user program. It provides an interface between the backend to allow the user input to be passed     through to the main algorithm and the correct output passed back to be shown on the user program
Numpy
  Used to provide added mathematical functionality that will be necessary when creating the Markov Chains
