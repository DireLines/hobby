#midiParsing.py

import sys
import time

#shoves a file into a big list of byte objects
def getByteList(filename):
	allthebytes = []
	with open(filename,"rb") as file:
		byte = file.read(1)
		while byte != b'':
			allthebytes.append(byte)
			byte = file.read(1)
	return allthebytes

#gets bits of a byte most significant first
def getBits(byte):
	bitstring = ''
	byte = ord(byte)
	for i in reversed(range(8)):
		bitstring += str((byte >> i) & 1)
	return bitstring

#byte --> decimal
def getIntValue(byte):
	return int(getBits(byte),base=2)

#finds all indices of a sublist within a list. Returns a list of tuples which are (beginning index of sublist, end index of sublist)
#from https://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
def findSubList(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))
    return results

#nice printing method which prints byte representation, decimal, hex, and binary
def printByteInfo(bytes):
	for i in range(len(bytes)):
		byte = bytes[i]
		strr = str(byte)
		strslice = strr[2:len(strr) - 1]
		if(strslice == ' '):
			strslice = 'space'
		print(i,":",strslice,"       ",getIntValue(byte),"         ",hex(getIntValue(byte)),"       ",getBits(byte))

#takes in a midi file and list of track numbers and creates a list of note on and off events
#format of each event:
#[note the event occurs in, absolute time of the event, 'on' or 'off', track of origin]
def createEventList(filename, tracknums):
	result = []
	bytes = getByteList(filename)
	# print(bytes)
	if(bytes[0:4] == [b'M', b'T', b'h', b'd']):
		trackHeaderIndices = findSubList([b'M', b'T', b'r', b'k'],bytes)
		if len(trackHeaderIndices) > 0:
			print("Number of tracks:",len(trackHeaderIndices))
			for tracknum in tracknums:
				if len(trackHeaderIndices) > tracknum:
					trackHeaderIndices.append([len(bytes)])
					trackbytes = bytes[(trackHeaderIndices[tracknum][1] + 1):(trackHeaderIndices[tracknum + 1][0])]
					del trackHeaderIndices[-1]
					# ok so now we have the bytes of the track we care about. 
					# next we can discard the pointless 4 bytes
					# used to indicate the tracklength (which are often wrong apparently)
					trackbytes = trackbytes[4:]
					# now it's just time:message pairs all the way down.
					i = 0
					absoluteTime = 0
					lastEventWasNoteOn = False
					while(i < len(trackbytes)):
						#interpret delta time
						deltaTimeBits = ''
						timeByte = getBits(trackbytes[i])
						deltaTimeBits += timeByte[1:]
						while(timeByte[0] == '1'):
							i += 1
							timeByte = getBits(trackbytes[i])
							deltaTimeBits += timeByte[1:]
						deltaTime = int(deltaTimeBits,base=2)
						i += 1
						absoluteTime += deltaTime
						# print("got delta time of",deltaTime)
						# print("absolute time is now",absoluteTime)

						#interpret MIDI message. If you don't know how, say which message caused you a problem.
						messageType = getBits(trackbytes[i])[:4]
						if(messageType == '1001'):#note on
							lastEventWasNoteOn = True
							i += 1
							note = getIntValue(trackbytes[i])
							i += 1
							velocity = getIntValue(trackbytes[i])
							if(velocity == 0):
								event = [note,absoluteTime,'off',tracknum]
								result.append(event)
							else:
								event = [note,absoluteTime,'on',tracknum]
								result.append(event)
							i += 1
						elif(messageType == '1000'):#note off
							lastEventWasNoteOn = False
							i += 1
							note = getIntValue(trackbytes[i])
							i += 2
							event = [note,absoluteTime,'off',tracknum]
							result.append(event)
						elif(messageType == '1111'): #could mean a number of things
							fullMessage = getBits(trackbytes[i])
							if(fullMessage == '11111111'):#it's a meta message
								i += 2
								metaMessageLength = getIntValue(trackbytes[i])
								i += metaMessageLength + 1
						elif(messageType == '1100'):#program change
							i += 2
						elif(messageType == '1011'):#control change
							i += 3
						elif(messageType == '1101'):#aftertouch
							i += 2
						elif(int(messageType,base = 2) < 8):#continuation from previous note on or note off event
							note = getIntValue(trackbytes[i])
							i += 1
							velocity = getIntValue(trackbytes[i])
							if(lastEventWasNoteOn):
								if(velocity == 0):
									event = [note,absoluteTime,'off',tracknum]
									result.append(event)
								else:
									event = [note,absoluteTime,'on',tracknum]
									result.append(event)
							else:
								event = [note,absoluteTime,'off',tracknum]
								result.append(event)
							i += 1

						else:
							print("was unable to parse message with message type",messageType,"at line",i)
							i = len(trackbytes)

				else:
					print("The file doesn't have enough tracks to have track number", tracknum)
		else:
			print("The file doesn't have any valid MIDI track headers so it's probably corrupted")
	else:
		print("That file doesn't have a proper MIDI header so either it's not a MIDI file or it's a corrupted MIDI file")
	return result

#Start of methods which are specific to my game

#counts how many on events correspond to each note and returns a dictionary of note:frequency pairs
def countNoteFrequencies(eventList):
	freqs = {}
	for event in eventList:
		if event[2] == 'on':
			if event[0] not in freqs:
				freqs[event[0]] = 1
			else:
				freqs[event[0]] += 1
	return freqs

# If event list has been created from merged tracks, return version where notes that are overlapping 
# (same note, same time region, different tracks) blob together
# def trimDuplicateEvents(eventList):
# 	result = []
# 	return result

#brings everything together. Given filename and track numbers to be included from the command line arguments,
#generates 
# def createGameEventList(filename, tracknums):


if(len(sys.argv) < 3):
	print("Usage: python midiParsing.py [midi file to analyze] [track numbers to analyze]")
	print("Example: python midiParsing.py yankeedoodle.midi 1 2")
else:
	filename = sys.argv[1]
	tracknums = map(lambda x: int(x), sys.argv[2:])
	allEvents = createEventList(filename,tracknums)
	freqs = countNoteFrequencies(allEvents)
	# for event in allEvents:
	# 	print(event)
	for thing in reversed(sorted(freqs)):
		print(thing,freqs[thing])
