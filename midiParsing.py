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

#gets bits of a list of bytes most significant first
def getConcatBits(bytes):
	bitstring = ''
	for byte in bytes:
		byte = ord(byte)
		for i in reversed(range(8)):
			bitstring += str((byte >> i) & 1)
	return bitstring

#byte --> decimal
def getIntValue(byte):
	return int(getBits(byte),base=2)

def getConcatIntValue(bytes):
	return int(getConcatBits(bytes),base=2)

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
		print(i,":",getBits(byte),"       ",getIntValue(byte),"         ",hex(getIntValue(byte)),"       ",strslice)

#takes in a midi file and list of track numbers and creates a list of note on and off events
#format of each event:
#[note the event occurs in, absolute time of the event, 'on' or 'off', track of origin]
#or, for time signature and tempo changes
#[-1,absolute time, 'tempo change' or 'time signature change',(relevant info from MIDI message)]
def createEventList(filename, tracknums):
	result = []
	bytes = getByteList(filename)
	# print(bytes)
	if(bytes[0:4] == [b'M', b'T', b'h', b'd']):
		sizeOfHeader = getConcatIntValue(bytes[4:8])
		midiType = getConcatIntValue(bytes[8:10])
		numTracks = getConcatIntValue(bytes[10:12])
		numTicksPerQuarterNote = getConcatIntValue(bytes[12:14])
		result.append([-1,-1,numTicksPerQuarterNote])
		trackHeaderIndices = findSubList([b'M', b'T', b'r', b'k'],bytes)
		if len(trackHeaderIndices) == numTracks and len(trackHeaderIndices) > 0:
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
						#print("tempo:",tempo)

						#interpret MIDI message. If you don't know how, say which message caused you a problem.
						messageType = getBits(trackbytes[i])[:4]
						# print("messageType",messageType)
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
								i += 1
								metaMessageType = getBits(trackbytes[i])
								# print("metaMessageType",metaMessageType)
								i += 1
								metaMessageLength = getIntValue(trackbytes[i])
								# print("metaMessageLength",metaMessageLength)
								if metaMessageType == '01010001':#tempo change
									endIndex = i + metaMessageLength + 1
									bitString = ''
									i += 1
									while i < endIndex:
										bitString += getBits(trackbytes[i])
										i += 1
									tempo = int(bitString,base=2)
									event = [-1,absoluteTime,'tempo change',tempo]
									result.append(event)
								elif metaMessageType == '01011000':#time signature change
									i += 1
									timeSigNumer = getIntValue(trackbytes[i])
									i += 1
									timeSigDenom = getIntValue(trackbytes[i])
									i += 1
									timeSigClocksPerClick = getIntValue(trackbytes[i])
									i += 1
									timeSig32ndNotesPerBeat = getIntValue(trackbytes[i])
									i += 1
									event = [-1,absoluteTime,'time signature change',timeSig32ndNotesPerBeat]
									result.append(event)
								else:
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
							printByteInfo([trackbytes[i]])
							i = len(trackbytes)

				else:
					print("The file doesn't have enough tracks to have track number", tracknum)
		elif len(trackHeaderIndices) < numTracks:
			print("The file has fewer MIDI track headers than tracks according to the file header so it's probably corrupted")
		elif len(trackHeaderIndices) > numTracks:
			print("the file has more track headers than tracks according to the file header. Look for a false positive")
		else:
			print("the file has no tracks")
	else:
		print("That file doesn't have a proper MIDI header so either it's not a MIDI file or it's a corrupted MIDI file")
	return result



























#Start of methods which are specific to my game

#given a list of events, including tempo changes, finds absolute time in microseconds 
def adjustForTimeSignatureChanges(eventList):
	eventList.sort(key = lambda x: int(x[1]))
	tempo = 500000 #microseconds per quarter note
	timeSig32ndNotesPerBeat = 8
	#header with pulses per quarter note guaranteed to be at the start
	pulsesPerQuarterNote = eventList[0][2]
	del eventList[0]
	# print(tempo,timeSig32ndNotesPerBeat,pulsesPerQuarterNote)

	for event in eventList:
		event.append(event[1])
		event[4] *= (tempo * timeSig32ndNotesPerBeat) / (8 * pulsesPerQuarterNote)
		event[4] = int(event[4])

	i = 0
	while i < len(eventList):
		if eventList[i][2] == 'tempo change':
			tempo = eventList[i][3]
			timeOfEventTicks = eventList[i][1]
			timeOfEventMicroseconds = eventList[i][4]
			j = i
			while(j < len(eventList)):
				timeMicroseconds = eventList[j][1]
				timeMicroseconds -= timeOfEventTicks
				timeMicroseconds *= (tempo * timeSig32ndNotesPerBeat) / (8 * pulsesPerQuarterNote)
				timeMicroseconds += timeOfEventMicroseconds
				timeMicroseconds = int(timeMicroseconds)
				eventList[j][4] = timeMicroseconds
				j += 1
		elif eventList[i][2] == 'time signature change':
			if(eventList[i][3] != timeSig32ndNotesPerBeat):
				timeSig32ndNotesPerBeat = eventList[i][3]
				timeOfEventTicks = eventList[i][1]
				timeOfEventMicroseconds = eventList[i][4]
				j = i
				while(j < len(eventList)):
					timeMicroseconds = eventList[j][1]
					timeMicroseconds -= timeOfEventTicks
					timeMicroseconds *= (tempo * timeSig32ndNotesPerBeat) / (8 * pulsesPerQuarterNote)
					timeMicroseconds += timeOfEventMicroseconds
					timeMicroseconds = int(timeMicroseconds)
					eventList[j][4] = timeMicroseconds
					j += 1
		i += 1

	#now event[4] is the time in microseconds for each event. 
	#Later functions are expecting event[1] to contain time info
	#so I will switch column 4 to column 1 and delete column 4
	#also, I will trim out the time sig and tempo change events because they're not needed anywhere else
	i = 0
	lenEventList = len(eventList)
	while i < lenEventList:
		if eventList[i][0] == -1: #any time stuff
			del eventList[i]
			lenEventList -= 1
		else:
			eventList[i][1] = eventList[i][4]
			del eventList[i][4]
			i += 1

	return eventList


#gets time sorted list of events pertaining to the specified note
def getEventsForNote(eventList,note):
	result = []
	for event in eventList:
		if event[0] == note:
			result.append(event)
	result.sort(key = lambda x: int(x[1]))
	return result

# If event list has been created from merged tracks, return version where notes that are overlapping 
# (same note, same time region, different tracks) are put into an ordered sequence.
# assumed to come before first and last events are labeled
def trimOverlappingEvents(eventList):
	noteSet = set([event[0] for event in eventList])
	resultList = []
	for note in noteSet:
		eventsForNote = getEventsForNote(eventList,note)
		notesPlayingCurrently = 0
		result = []
		currentTrackPlaying = eventsForNote[0][3]
		for event in eventsForNote:
			if event[2] == 'on':
				notesPlayingCurrently += 1
				if notesPlayingCurrently == 1:
					result.append(event)
					currentTrackPlaying = event[3]
				else:
					result.append([note,event[1],'off',currentTrackPlaying])
					result.append(event)
			else:
				notesPlayingCurrently -= 1
				if notesPlayingCurrently == 0:
					result.append(event)
			if notesPlayingCurrently == -1:
				print("hmm, notesPlayingCurrently has somehow dipped into negatives")
		resultList.extend(result)
		if notesPlayingCurrently > 0:
			print("hmm, notesPlayingCurrently is still positive at the end")
	return resultList

#does what it says. used to find out how much time should be slowed by.
#assumes first and last events have not been labeled yet
def getMedianDeltaTimeBetweenOnEvents(events):
	i = 1
	lastOnIndex = 0
	deltaList = []
	while i < len(events):
		if(events[i][2] == 'on'):
			delta = events[i][1] - events[lastOnIndex][1]
			if(delta != 0):
				deltaList.append(delta)
			lastOnIndex = i
		i += 1
	deltaList.sort()
	return deltaList[len(deltaList) // 2]

def getMeanDeltaTimeBetweenOnEvents(events):
	i = 1
	lastOnIndex = 0
	numEvents = 0
	sum = 0
	while i < len(events):
		if(events[i][2] == 'on'):
			delta = events[i][1] - events[lastOnIndex][1]
			if(delta != 0):
				sum += delta
				numEvents += 1
			lastOnIndex = i
		i += 1
	return (sum / numEvents)

#scales time values such that median delta time between on events corresponds to a certain magic number of seconds of gameplay
#specified by numberOfSecondsToStretchTo
#also converts microseconds to seconds
def stretchTime(events,numberOfSecondsToStretchTo):
	medianTime = getMedianDeltaTimeBetweenOnEvents(events)
	print("medianTime:",medianTime)
	meanTime = getMeanDeltaTimeBetweenOnEvents(events)
	print("meanTime:",meanTime)
	for event in events:
		event[1] *= (1000000 * numberOfSecondsToStretchTo) / medianTime
		event[1] /= 1000000
		event[1] = int(event[1])
	return events

#gets number of ticks note plays in the song
#assumes overlaps have already been eliminated
#which lets us assume even indices are on events and odd indices are off events
def getTimeSpentPlayingNote(eventList,note):
	result = 0
	eventsForNote = getEventsForNote(eventList,note)
	numEvents = len(eventsForNote)
	i = 1
	while(i < numEvents):
		result += eventsForNote[i][1] - eventsForNote[i-1][1]
		i += 2
	return result

#counts how many on events correspond to each note and returns a dictionary of note:frequency pairs
def countNoteFrequencies(eventList):
	freqs = {}
	for event in eventList:
		if event[2][0:3] == 'on':
			if event[0] not in freqs:
				freqs[event[0]] = 1
			else:
				freqs[event[0]] += 1
	return freqs

#starting at startTime seconds (normally where the last game ended),
#finds the first On event and then
#finds all events less than duration seconds after the time of that first On event.
#and returns that slice of the array
def trimToInterval(events,startTime,duration):
	endTime = startTime + duration
	startIndex = 0
	startHasBeenFound = False
	stopIndex = 0
	stopHasBeenFound = False
	i = 0
	while(i < len(events)):
		if not startHasBeenFound and events[i][1] >= startTime and events[i][2] == 'on':
			startHasBeenFound = True
			startIndex = i
			startTime = events[i][1]
			endTime = startTime + duration
		if events[i][1] > endTime:
			stopIndex = i
			i = len(events)
			stopHasBeenFound = True
		i += 1
	if not(startHasBeenFound):
		print("trimToInterval failed - Tried to trim events starting from a time before or after the interval")
		return events
	elif not(stopHasBeenFound):
		print("trimToInterval failed - There's not enough time in the events to have an interval that long")
		return events
	return events[startIndex:stopIndex]


#returns 4 dictionaries containing note:event index pairs
def findFirstAndLastEventsForEachNote(eventList,timeSorted=True):
	if(timeSorted == False):
		eventList.sort(key = lambda x: int(x[1]))
	noteSet = set([event[0] for event in eventList])
	numEvents = len(eventList)
	notesWithFirstOnIndices = {}
	notesWithFirstOffIndices = {}
	notesWithLastOnIndices = {}
	notesWithLastOffIndices = {}
	for note in noteSet:
		notesWithFirstOnIndices[note] = -1
		notesWithFirstOffIndices[note] = -1
		notesWithLastOnIndices[note] = -1
		notesWithLastOffIndices[note] = -1
	#find first and last indices for each note
	i = 0
	while(i < numEvents):
		note = eventList[i][0]
		message = eventList[i][2]
		if(message == 'on'):
			if(notesWithFirstOnIndices[note] == -1):
				notesWithFirstOnIndices[note] = i
			notesWithLastOnIndices[note] = i
		else:
			if(notesWithFirstOffIndices[note] == -1):
				notesWithFirstOffIndices[note] = i
			notesWithLastOffIndices[note] = i
		i += 1
	return [notesWithFirstOnIndices,notesWithFirstOffIndices,notesWithLastOnIndices,notesWithLastOffIndices]

#returns an edited version of eventList such that the first on and off events for each note are labeled as such
#and so are the last on and off events
#assumes duplicate and overlapping events have been trimmed away
#also resolves situations where trimToInterval caused Off event to be first or On event to be last for a note
def labelFirstAndLastEventsForEachNote(eventList,duration,timeSorted=True):
	dicts = findFirstAndLastEventsForEachNote(eventList,timeSorted=timeSorted)
	noteSet = set([event[0] for event in eventList])
	notesWithFirstOnIndices = dicts[0]
	notesWithFirstOffIndices = dicts[1]
	notesWithLastOnIndices = dicts[2]
	notesWithLastOffIndices = dicts[3]
	#label events accordingly. Spit out some debug cases
	for note in noteSet:
		firstOnIndex = notesWithFirstOnIndices[note]
		firstOffIndex = notesWithFirstOffIndices[note]
		lastOnIndex = notesWithLastOnIndices[note]
		lastOffIndex = notesWithLastOffIndices[note]
		if(lastOffIndex == -1 or firstOffIndex == -1):
			# print("no off event found for note",note)
			eventList[firstOnIndex][2] = 'on for the first and last time'
			trackOfOnEvent = eventList[firstOnIndex][3]
			eventList.append([note,duration,'off for the first and last time',trackOfOnEvent])
		elif(firstOnIndex == -1 or lastOnIndex == -1):
			# print("no on event found for note:",note)
			eventList[firstOffIndex][2] = 'off for the first and last time'
			trackOfOffEvent = eventList[firstOffIndex][3]
			eventList.append([note,0,'on for the first and last time',trackOfOffEvent])
		elif(firstOffIndex < firstOnIndex):
			# print("for note",note,"an off event occurred before the first on event")
			trackOfOffEvent = eventList[firstOffIndex][3]
			eventList[firstOffIndex][2] = 'off for the first time'
			eventList.append([note,0,'on for the first time',trackOfOffEvent])
			eventList[lastOnIndex][2] = 'on for the last time'
			eventList[lastOffIndex][2] = 'off for the last time'
		elif(lastOnIndex > lastOffIndex):
			# print("for note",note,"an on event occurred after the last off event")
			trackOfOnEvent = eventList[lastOnIndex][3]
			eventList[lastOnIndex][2] = 'on for the last time'
			eventList.append([note,duration,'off for the last time',trackOfOnEvent])
			eventList[firstOnIndex][2] = 'on for the first time'
			eventList[firstOffIndex][2] = 'off for the first time'
		else:
			if(firstOnIndex == lastOnIndex):
				eventList[firstOnIndex][2] = 'on for the first and last time'
			else:
				eventList[firstOnIndex][2] = 'on for the first time'
				eventList[lastOnIndex][2] = 'on for the last time'
			if(firstOffIndex == lastOffIndex):
				eventList[firstOffIndex][2] = 'off for the first and last time'
			else:
				eventList[firstOffIndex][2] = 'off for the first time'
				eventList[lastOffIndex][2] = 'off for the last time'

	return eventList

#makes it so that the time ticks begin at 0 as they would in a game
def normalizeTimes(eventList,timeSorted=True):
	if timeSorted == False:
		eventList.sort(key = lambda x: int(x[1]))
	if len(eventList) > 0:
		lowestTime = eventList[0][1]
		for event in eventList:
			event[1] -= lowestTime
	return eventList

#plays events back. should resemble the rhythm of the midi file
def printEventsOverTimeMicro(eventList):
	eventList.sort(key = lambda x: int(x[1]))
	time.sleep(eventList[0][1] / 1000000)
	print(eventList[0])
	for i in range(1,len(eventList)):
		time.sleep((eventList[i][1] - eventList[i-1][1]) / 1000000)
		print(eventList[i])

def printEventsOverTime(eventList):
	eventList.sort(key = lambda x: int(x[1]))
	time.sleep(eventList[0][1])
	print(eventList[0])
	for i in range(1,len(eventList)):
		time.sleep(eventList[i][1] - eventList[i-1][1])
		print(eventList[i])

# brings everything together. Given filename and track numbers to be included from the command line arguments,
# generates an initial list of game events and times they are associated with.
def createGameEventList(filename, tracknums, startTime=0,duration=3600000000):
	eventList = createEventList(filename,tracknums)
	eventList = adjustForTimeSignatureChanges(eventList)
	eventList = trimOverlappingEvents(eventList)
	eventList.sort(key = lambda x: int(x[1]))
	numberOfSecondsToStretchTo = 65
	eventList = stretchTime(eventList,numberOfSecondsToStretchTo)

	eventList = trimToInterval(eventList,startTime,duration)
	eventList = normalizeTimes(eventList)
	eventList = labelFirstAndLastEventsForEachNote(eventList,duration)
	eventList.sort(key = lambda x: int(x[1]))
	
	#events are now finalized, so I will put them in a txt file.
	with open("midiparseroutfile.txt","w") as outfile:
		for event in eventList:
			outfile.write(str(event))
			outfile.write('\n')
	return eventList

if(len(sys.argv) < 3):
	print("Usage: python midiParsing.py [midi file to analyze] [track numbers to analyze]")
	print("Example: python midiParsing.py yankeedoodle.midi 1 2")
else:
	filename = sys.argv[1]
	tracknums = map(lambda x: int(x), sys.argv[2:])
	events = createGameEventList(filename,tracknums)

	# bytes = getByteList(filename)
	# printByteInfo(bytes)

	for event in events:
		print(event)

	printEventsOverTime(events)

	# freq = countNoteFrequencies(events)
	# for thing in reversed(sorted(freq)):
	# 	print(thing,freq[thing], getTimeSpentPlayingNote(events,thing))

	# noteSet = set([event[0] for event in events])
	# for note in noteSet:
	# 	eventsForNote = getEventsForNote(events,note)
	# 	print("")
	# 	print(note)
	# 	print(getTimeSpentPlayingNote(events,note))
	# 	out = ""
	# 	for i in range(len(eventsForNote)):
	# 		out += str(eventsForNote[i])
	# 		if(i % 2 == 1):
	# 			print(out)
	# 			out = ""

























