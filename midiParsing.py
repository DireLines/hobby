#midiParsing.py

import sys
import time

def getByteList(filename):
	allthebytes = []
	with open(filename,"rb") as file:
		byte = file.read(1)
		while byte != b'':
			allthebytes.append(byte)
			byte = file.read(1)
	return allthebytes

def getBits(byte):
	bitstring = ''
	byte = ord(byte)
	for i in reversed(range(8)):
		bitstring += str((byte >> i) & 1)
	return bitstring

def getIntValue(byte):
	return int(getBits(byte),base=2)

#from https://stackoverflow.com/questions/17870544/find-starting-and-ending-indices-of-sublist-in-list
def findSubList(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))
    return results

def createEventList(filename, tracknum):
	result = []
	bytes = getByteList(filename)
	if(bytes[0:4] == [b'M', b'T', b'h', b'd']):
		trackHeaderIndices = findSubList([b'M', b'T', b'r', b'k'],bytes)
		if len(trackHeaderIndices) > 0:
			print(len(trackHeaderIndices))
			if len(trackHeaderIndices) > tracknum:
				trackHeaderIndices.append([len(bytes)])
				trackbytes = []
				for byte in bytes[(trackHeaderIndices[tracknum][1] + 1):(trackHeaderIndices[tracknum + 1][0])]:
					trackbytes.append(byte)
				# ok so now we have the bytes of the track we care about. next we can eat the pointless 4 bytes
				# used to indicate the tracklength (which are often wrong apparently)
				trackbytes = trackbytes[4:]
				# now it's just time:message pairs all the way down.
				i = 0
				absoluteTime = 0
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
						i += 1
						note = getIntValue(trackbytes[i])
						i += 1
						velocity = getIntValue(trackbytes[i])
						if(velocity == 0):
							event = '' + str(absoluteTime) + ': ' + str(note) + ' turned off'
							result.append(event)
						else:
							event = '' + str(absoluteTime) + ': ' + str(note) + ' turned on'
							result.append(event)
						i += 1
					elif(messageType == '1000'):#note off
						i += 1
						note = getIntValue(trackbytes[i])
						i += 2
						event = '' + str(absoluteTime) + ': ' + str(note) + ' turned off'
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
					else:
						print("was unable to parse message with message type",messageType,"at line",i)
						i = len(trackbytes)


				# for i in range(len(trackbytes)):
				# 	byte = trackbytes[i]
				# 	strr = str(byte)
				# 	strslice = strr[2:len(strr) - 1]
				# 	if(strslice == ' '):
				# 		strslice = 'space'
				# 	print(i,":",strslice,"       ",getIntValue(byte),"         ",hex(getIntValue(byte)),"       ",getBits(byte))

			else:
				print("The file doesn't have enough tracks to have a track of that number")
		else:
			print("The file doesn't have any valid MIDI track headers so it's probably corrupted")
	else:
		print("That file doesn't have a proper MIDI header so either it's not a MIDI file or it's a corrupted MIDI file")
	return result



if(len(sys.argv) < 3):
	print("Usage: python midiParsing.py [midi file to analyze] [track number to analyze]")
	print("Example: python midiParsing.py yankeedoodle.midi 1")
else:
	filename = sys.argv[1]
	tracknum = int(sys.argv[2])
	for event in createEventList(filename,tracknum):
		print(event)